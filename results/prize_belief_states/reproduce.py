"""Reproduce pre-search Prize belief updates."""

from __future__ import annotations

from itertools import combinations
from math import comb, isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_belief import (  # noqa: E402
    group_prize_distribution,
    prize_only_line_failure_probability,
    singleton_prized_probability,
)


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _exhaustive_small_check() -> None:
    labels = ["A1", "A2", "F1", "F2", "F3", "F4", "F5"]
    total = comb(7, 2)
    brute: dict[int, float] = {}

    for prize_indices in combinations(range(7), 2):
        chosen = {labels[index] for index in prize_indices}
        prized_group = int("A1" in chosen) + int("A2" in chosen)
        brute[prized_group] = brute.get(prized_group, 0.0) + 1.0 / total

    modeled = dict(
        group_prize_distribution(
            group_copies=2,
            visible_group_copies=0,
            visible_nonprize_cards=3,
            deck_size=10,
            prize_count=2,
        )
    )

    assert set(brute) == set(modeled)
    for prized_group, probability in brute.items():
        _assert_close(modeled[prized_group], probability)


def main() -> None:
    _exhaustive_small_check()

    opening = singleton_prized_probability(visible_nonprize_cards=7)
    one_extra_miss = singleton_prized_probability(visible_nonprize_cards=8)
    five_extra_misses = singleton_prized_probability(visible_nonprize_cards=12)
    ten_extra_misses = singleton_prized_probability(visible_nonprize_cards=17)
    seen_singleton = singleton_prized_probability(
        visible=True,
        visible_nonprize_cards=8,
    )

    _assert_close(opening, 6 / 53)
    _assert_close(one_extra_miss, 6 / 52)
    _assert_close(five_extra_misses, 6 / 48)
    _assert_close(ten_extra_misses, 6 / 43)
    _assert_close(seen_singleton, 0.0)

    two_copy_opening_failure = prize_only_line_failure_probability(
        group_copies=2,
        minimum_unprized_needed=1,
        visible_nonprize_cards=7,
    )
    two_copy_after_five_misses = prize_only_line_failure_probability(
        group_copies=2,
        minimum_unprized_needed=1,
        visible_nonprize_cards=12,
    )

    _assert_close(two_copy_opening_failure, comb(51, 4) / comb(53, 6))
    _assert_close(two_copy_after_five_misses, comb(46, 4) / comb(48, 6))

    print("Unseen singleton Prize posterior")
    print(f"  after accepted opening: {opening:.9%}")
    print(f"  after 1 additional non-target draw: {one_extra_miss:.9%}")
    print(f"  after 5 additional non-target draws: {five_extra_misses:.9%}")
    print(f"  after 10 additional non-target draws: {ten_extra_misses:.9%}")
    print(f"  if the singleton itself is visible: {seen_singleton:.9%}")
    print()

    print("Two-copy line, both copies still unseen")
    print(f"  failure after accepted opening: {two_copy_opening_failure:.9%}")
    print(f"  failure after 5 additional non-target draws: {two_copy_after_five_misses:.9%}")
    print()

    print("All Prize-belief checks passed.")


if __name__ == "__main__":
    main()
