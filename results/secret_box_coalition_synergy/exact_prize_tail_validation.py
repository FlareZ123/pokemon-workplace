"""Brute-force micro-oracle and exact Aichi rare-Prize conditional odds."""

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from aichi_vileplume_als import BASICS, DECK_COUNTS
from accepted_opening_prize_probabilities import (
    fixed_nonbasic_prized_given_valid_opener,
)


def tiny_direct_enumeration() -> Fraction:
    """Count equally likely open-hand/Prize sequences on an eight-card deck."""
    basics = {0, 1}
    forced = {2, 3}
    target = 0
    valid = 0
    for hand in combinations(range(8), 3):
        if not basics.intersection(hand):
            continue
        remaining = [index for index in range(8) if index not in hand]
        for prizes in combinations(remaining, 3):
            valid += 1
            target += forced.issubset(prizes)
    return Fraction(target, valid)


def main() -> None:
    brute = tiny_direct_enumeration()
    analytic = fixed_nonbasic_prized_given_valid_opener(
        cards=8, basics=2, opening=3, prizes=3, forced_nonbasic=2,
    )
    assert brute == analytic, (brute, analytic)

    b = sum(DECK_COUNTS.get(name, 0) for name in BASICS)
    assert sum(DECK_COUNTS.values()) == 60 and b == 14
    p4 = fixed_nonbasic_prized_given_valid_opener(
        cards=60, basics=b, opening=7, prizes=6, forced_nonbasic=4,
    )
    p6 = fixed_nonbasic_prized_given_valid_opener(
        cards=60, basics=b, opening=7, prizes=6, forced_nonbasic=6,
    )
    assert p4 == Fraction(246_321, 7_805_903_600)
    assert p6 == Fraction(1_195, 57_598_385_152)
    assert p4 > p6 > 0

    print("Micro-oracle direct probability:", brute)
    print("Four fixed nonBasics all Prized conditional valid 7:", p4)
    print("Six fixed nonBasics all Prized conditional valid 7:", p6)
    print("Four fixed Prized expected 500k:", float(p4 * 500_000))
    print("Six fixed Prized expected 500k:", float(p6 * 500_000))
    print("Rare-Prize conditional exact and micro-oracle checks passed.")


if __name__ == "__main__":
    main()
