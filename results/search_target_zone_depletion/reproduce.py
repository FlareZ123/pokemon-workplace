"""Reproduce and validate exact setup-conditioned search-target depletion."""

from __future__ import annotations

from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from conditioned_searchability import conditioned_searchability  # noqa: E402


ABS_TOLERANCE = 1e-12


def exhaustive_small(
    deck_size: int,
    forced_starters: int,
    target_copies: tuple[int, ...],
    *,
    opening_hand_size: int,
    prize_count: int,
    pre_search_draws: int,
) -> float:
    """Enumerate labeled cards and return the exact conditional probability."""
    labels: list[str] = []
    for index, copies in enumerate(target_copies):
        labels.extend([f"T{index}"] * copies)
    labels.extend(["S"] * forced_starters)
    labels.extend(["F"] * (deck_size - len(labels)))

    cards = tuple(range(deck_size))
    exposed_count = prize_count + pre_search_draws
    valid_states = 0
    successful_states = 0

    for hand in combinations(cards, opening_hand_size):
        if not any(labels[index] == "S" for index in hand):
            continue

        hand_set = set(hand)
        after_hand = tuple(
            index
            for index in cards
            if index not in hand_set
        )

        for exposed in combinations(after_hand, exposed_count):
            exposed_set = set(exposed)
            valid_states += 1

            remaining = tuple(
                index
                for index in after_hand
                if index not in exposed_set
            )
            if all(
                any(labels[index] == f"T{target}" for index in remaining)
                for target in range(len(target_copies))
            ):
                successful_states += 1

    return successful_states / valid_states


def validate() -> None:
    small = dict(
        deck_size=10,
        forced_starters=2,
        target_copies=(2, 1),
        opening_hand_size=2,
        prize_count=2,
        pre_search_draws=1,
    )
    exact = conditioned_searchability(**small)
    brute = exhaustive_small(**small)
    if not isclose(exact, brute, rel_tol=0.0, abs_tol=ABS_TOLERANCE):
        raise AssertionError((exact, brute))

    expected = {
        (1,): 0.7716248595566182,
        (2,): 0.9509406113150052,
        (2, 2): 0.9037142689348611,
        (2, 1): 0.7324139736285623,
        (2, 2, 2, 1): 0.658509587514953,
    }
    for profile, target in expected.items():
        actual = conditioned_searchability(
            60,
            14,
            profile,
            opening_hand_size=7,
            prize_count=6,
            pre_search_draws=1,
        )
        if not isclose(
            actual,
            target,
            rel_tol=0.0,
            abs_tol=ABS_TOLERANCE,
        ):
            raise AssertionError((profile, actual, target))


def main() -> None:
    validate()

    profiles = (
        (1,),
        (2,),
        (3,),
        (4,),
        (2, 2),
        (2, 1),
        (3, 2),
        (4, 1),
        (2, 2, 2, 1),
    )
    print("profile | all required groups remain searchable")
    for profile in profiles:
        probability = conditioned_searchability(
            60,
            14,
            profile,
            opening_hand_size=7,
            prize_count=6,
            pre_search_draws=1,
        )
        print(f"{str(profile):18s} | {100 * probability:.6f}%")


if __name__ == "__main__":
    main()
