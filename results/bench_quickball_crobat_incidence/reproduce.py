"""Independent exhaustive labeled opener/Prize/later-draw incidence oracle."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from bench_quickball_crobat_incidence import analyze  # noqa: E402
from bench_quickball_crobat_dedenne import analyze as continuation  # noqa: E402


def brute(*, deck_size: int, opening_size: int, prize_count: int,
          later_draws: int, quick_balls: int, discardable: int,
          other_basics: int):
    counts = (("D", 1), ("C", 1), ("K", 1), ("Q", quick_balls),
              ("F", discardable), ("O", other_basics))
    cards = [(name, index) for name, n in counts for index in range(n)]
    cards += [("X", i) for i in range(deck_size - len(cards))]
    accepted = 0
    opening_event = 0
    accepted_sequences = 0
    live_events = 0
    for opening in combinations(cards, opening_size):
        hand = set(opening)
        labels = [name for name, _ in opening]
        if not any(name in ("D", "C", "O") for name in labels):
            continue
        accepted += 1
        good = (labels.count("D") == 1 and labels.count("C") == 0
                and labels.count("K") == 0 and "Q" in labels
                and "F" in labels and "O" in labels)
        if good:
            opening_event += 1
        rest = [x for x in cards if x not in hand]
        for prizes in combinations(rest, prize_count):
            prize_set = set(prizes)
            rest2 = [x for x in rest if x not in prize_set]
            for draws in combinations(rest2, later_draws):
                accepted_sequences += 1
                if good and ("C", 0) not in prize_set and ("C", 0) not in draws:
                    live_events += 1

    all_hands = comb(deck_size, opening_size)
    per_open_sequences = comb(deck_size-opening_size, prize_count) * comb(
        deck_size-opening_size-prize_count, later_draws)
    return (Fraction(accepted, all_hands),
            Fraction(opening_event, all_hands),
            Fraction(live_events, all_hands * per_open_sequences),
            Fraction(live_events, accepted_sequences))


def validate() -> None:
    cases = (
        dict(deck_size=11, opening_size=4, prize_count=2,
             later_draws=1, quick_balls=2, discardable=2, other_basics=2),
        dict(deck_size=12, opening_size=4, prize_count=2,
             later_draws=1, quick_balls=2, discardable=2, other_basics=2),
        dict(deck_size=12, opening_size=5, prize_count=2,
             later_draws=1, quick_balls=2, discardable=2, other_basics=2),
    )
    for case in cases:
        x = analyze(**case)
        expected = brute(**case)
        assert (x.valid_open, x.opening_material, x.material_and_crobat_live,
                x.material_given_valid) == expected, (case, x, expected)
    case = analyze()
    assert case.material_given_valid < Fraction(1, 100)
    weighted_gain = case.material_given_valid * continuation(hand_size=5).access_gain
    print("Independent full labeled opening, prize, draw enumeration matched.")
    print(f"Valid opener: {float(case.valid_open):.6%}")
    print(f"Opening material and live Crobat | valid: {float(case.material_given_valid):.9%}")
    print(f"Staged h=5 continuation gain on this material: {float(continuation(hand_size=5).access_gain):.6%}")
    print(f"Weighted restricted target-access contribution: {float(weighted_gain):.9%}")


if __name__ == "__main__":
    validate()
