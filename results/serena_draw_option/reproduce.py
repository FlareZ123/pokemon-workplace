"""Exact Serena draw/gust opportunity-cost regression across typed Prize boards."""
from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.serena_draw_option import (
    action_values, draw_outcomes, expected_attacks
)
from tools.trainer_gust_catalog import CATEGORIES
from tools.typed_gust_target_minimax import Target, enumerate_boards


def main():
    assert CATEGORIES["Serena"].target_scope == "pokemon_v_family"
    assert "draw_alternative" in CATEGORIES["Serena"].gates
    assert sum(prob for *_, prob in draw_outcomes(2, 1, 7, 5)) == 1
    assert len(draw_outcomes(1, 0, 19, 5)) == 2

    active = Target(3, False)
    bench = (Target(1, False), Target(3, False))
    expected = {
        1: (Fraction(53, 20), Fraction(29, 10)),
        2: (Fraction(229, 95), Fraction(533, 190)),
    }
    for b, (want_draw, want_no_draw) in expected.items():
        draw = expected_attacks(active, bench, 0, 1, 0, b, 0, 20 - b, 6, True)
        no_draw = expected_attacks(active, bench, 0, 1, 0, b, 0, 20 - b, 6, False)
        assert (draw, no_draw) == (want_draw, want_no_draw)
        # Independent combinatorial policy proof: without Serena draw the
        # first 2 natural draws must find Boss; with Serena draw the
        # same 2-attack policy can expose 7 cards (1+5+1).
        assert no_draw == 2 + Fraction(comb(20 - b, 2), comb(20, 2))
        assert draw == 2 + Fraction(comb(20 - b, 7), comb(20, 7))
        print(
            f"{b} Boss in 20-card deck: Serena draw {draw}; "
            f"no draw mode {no_draw}; benefit {no_draw - draw}"
        )

    # The exact post-natural-draw policy sees one disposable filler and
    # can discard it to activate the first Serena draw mode.
    candidate_costs = dict(
        action_values(
            active, bench, 0, 1, 1, 1, 0, 18, 6, True
        )
    )
    assert candidate_costs["attack_active"] == Fraction(56, 19)
    assert candidate_costs["serena_draw_discard_0_boss_0_serena_1_filler"] == Fraction(51, 19)

    # With an immediately gustable 3-Prize V target, Serena's gust mode is
    # strategically necessary before the later Boss can hit a non-V.
    v_active = Target(1, False)
    v_bench = (
        Target(1, False), Target(3, False), Target(3, True)
    )
    for boss_count, cost in (
        (0, Fraction(4)),
        (1, Fraction(15, 4)),
        (2, Fraction(669, 190)),
        (3, Fraction(944, 285)),
    ):
        full = expected_attacks(
            v_active, v_bench, 0, 1, 0,
            boss_count, 0, 20 - boss_count, 6, True
        )
        gust_only = expected_attacks(
            v_active, v_bench, 0, 1, 0,
            boss_count, 0, 20 - boss_count, 6, False
        )
        assert full == gust_only == cost

    boards = tuple(enumerate_boards())
    assert len(boards) == 582
    results = {}
    checks = 0
    for boss_count, expected_positive in ((1, 105), (2, 120)):
        positive = zero = 0
        maximal_gain = Fraction(0)
        for a, b in boards:
            with_draw = expected_attacks(
                a, b, 0, 1, 0, boss_count, 0, 20 - boss_count, 6, True
            )
            no_draw = expected_attacks(
                a, b, 0, 1, 0, boss_count, 0, 20 - boss_count, 6, False
            )
            assert with_draw <= no_draw, (a, b, boss_count, with_draw, no_draw)
            positive += with_draw < no_draw
            zero += with_draw == no_draw
            maximal_gain = max(maximal_gain, no_draw - with_draw)
            checks += 1
        assert positive == expected_positive and positive + zero == 582
        assert maximal_gain == (Fraction(1, 2) if boss_count == 1 else Fraction(29, 38))
        results[boss_count] = (positive, zero, maximal_gain)
        print(
            f"Boss deck copies {boss_count}: Serena draw better in "
            f"{positive}/582 boards, tied in {zero}, max gain {maximal_gain}"
        )
    assert checks == 1164

    # Text literal: at least one discard is required; Serena alone with an
    # empty hand cannot invoke the draw mode until a normal card is drawn.
    no_discard = action_values(active, bench, 0, 1, 0, 1, 0, 19, 6, True)
    assert all("serena_draw" not in name for name, _ in no_discard)
    print("PASS 1,164 typed-board comparisons plus closed-form draw checks")


if __name__ == "__main__":
    main()
