"""Exact analytic and deterministic-limit checks for stochastic gust timing."""
from fractions import Fraction
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.gust_prize_minimax import enumerate_boards, minimum_attacks
from tools.stochastic_gust_draw import expected_attacks


def main() -> None:
    cases = 0
    for active, bench, values in enumerate_boards():
        for hand in range(3):
            # Every future draw is inert filler: recover the original minimax.
            actual = expected_attacks(active, bench, hand, 0, 6, 6)
            assert actual == minimum_attacks(active, bench, hand, 6)
            cases += 1
    assert cases == 438

    for deck_size in (6, 10, 40):
        # Active 1, Bench 1,3,3. One gust is useless against worst promotion.
        assert expected_attacks(1, (1, 3, 3), 0, 1, deck_size - 1) == 4

        two_hidden = expected_attacks(1, (1, 3, 3), 0, 2, deck_size - 2)
        one_ready = expected_attacks(1, (1, 3, 3), 1, 1, deck_size - 1)

        # In two-hidden case the useful first-three draw positions are
        # {1,2}: save 2 attacks; {1,3} and {2,3}: save 1 each.
        assert two_hidden == 4 - Fraction(4, comb(deck_size, 2))

        # With one gust already in hand, the second in draw positions 1,2
        # saves 2 attacks; draw position 3 saves 1.
        assert one_ready == 4 - Fraction(5, deck_size)
        print(
            f"Deck={deck_size}: two hidden {two_hidden} ({float(two_hidden):.9f}), "
            f"one held {one_ready} ({float(one_ready):.9f})"
        )

    assert expected_attacks(1, (1, 3, 3), 0, 2, 8) == Fraction(176, 45)
    assert expected_attacks(1, (1, 3, 3), 1, 1, 9) == Fraction(7, 2)
    assert expected_attacks(1, (1, 3, 3), 0, 2, 38) == Fraction(779, 195)
    print(f"PASS {cases} independent deterministic-limit states and analytic draw-position identities")


if __name__ == "__main__":
    main()
