"""Exact evaluation of protecting extra Serena/Boss cards against legal discard choices."""
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.serena_draw_option import expected_attacks, action_values
from tools.typed_gust_target_minimax import Target, enumerate_boards


def solve(active, bench, serenas_in_hand, boss_in_deck, protect):
    return expected_attacks(
        active, bench,
        0, serenas_in_hand, 0,
        boss_in_deck, 0, 20 - boss_in_deck,
        6, True, protect,
    )


def main():
    boards = tuple(enumerate_boards())
    assert len(boards) == 582
    expected_counts = {
        (2, 1): (52, Fraction(1, 20)),
        (2, 2): (65, Fraction(13, 190)),
        (3, 1): (114, Fraction(1, 10)),
        (3, 2): (128, Fraction(27, 190)),
    }
    checks = 0
    for copies_serena in (2, 3):
        for boss_deck in (1, 2):
            positive = 0
            gain_max = Fraction()
            for a, b in boards:
                unrestricted = solve(a, b, copies_serena, boss_deck, False)
                protected = solve(a, b, copies_serena, boss_deck, True)
                assert unrestricted <= protected
                positive += unrestricted < protected
                gain_max = max(gain_max, protected - unrestricted)
                checks += 1
            expected = expected_counts[(copies_serena, boss_deck)]
            assert (positive, gain_max) == expected, (
                copies_serena, boss_deck, positive, gain_max
            )
            print(
                f"{copies_serena} Serena in hand, {boss_deck} Boss in deck: "
                f"unrestricted discard improves {positive}/582 boards, "
                f"largest improvement {gain_max} expected attacks"
            )
    assert checks == 2328

    # Non-V three-Prize Active, non-V 1 and 3 Prize Bench: other Serena
    # copies are inert as gust effects, so discarding them digs deeper.
    active = Target(3, False)
    bench = (Target(1, False), Target(3, False))
    for serenas in (2, 3):
        for boss in (1, 2):
            full = solve(active, bench, serenas, boss, False)
            protected = solve(active, bench, serenas, boss, True)
            # Protected filler-only Serena mode draws 8 - serenas total
            # exposed cards through the next turn; unrestricted mode
            # can discard excess Serenas and expose seven.
            exposure = 8 - serenas
            assert protected == (
                Fraction(2) + Fraction(comb(20 - boss, exposure), comb(20, exposure))
            )
            assert full == (
                Fraction(2) + Fraction(comb(20 - boss, 7), comb(20, 7))
            )
            assert full < protected

    # After the natural draw adds a filler, the unrestricted Serena can
    # discard the *other* Serena and the filler, then draw five cards.
    action = dict(action_values(
        active, bench, 0, 2, 1, 1, 0, 18, 6, True, False
    ))
    restricted = dict(action_values(
        active, bench, 0, 2, 1, 1, 0, 18, 6, True, True
    ))
    assert "serena_draw_discard_0_boss_1_serena_1_filler" in action
    assert "serena_draw_discard_0_boss_1_serena_1_filler" not in restricted
    assert "serena_draw_discard_0_boss_0_serena_1_filler" in restricted
    assert action["serena_draw_discard_0_boss_1_serena_1_filler"] < (
        restricted["serena_draw_discard_0_boss_0_serena_1_filler"]
    )

    # Requiring protected Boss/Serena discards offers no improvement when
    # exactly one Serena and one Boss are already held in these 20-card
    # source scenarios, so indiscriminate discard remains unjustified.
    for bcount in (1, 2):
        for a, b in boards:
            full = expected_attacks(a, b, 1, 1, 0, bcount, 0, 20 - bcount)
            protected = expected_attacks(
                a, b, 1, 1, 0, bcount, 0, 20 - bcount, 6, True, True
            )
            assert full == protected

    print("PASS 2,328 discard-policy board checks and closed-form reveal audits")


if __name__ == "__main__":
    main()
