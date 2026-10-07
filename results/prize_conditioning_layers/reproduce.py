"""Reproduce the distinction between valid-start and exact-hand Prize conditioning."""

from __future__ import annotations

from itertools import combinations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_belief import singleton_prized_probability  # noqa: E402


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    cards = (
        "S0",
        "S1",
        "S2",
        "X",
        "F0",
        "F1",
        "F2",
        "F3",
        "F4",
        "F5",
    )
    starters = {"S0", "S1", "S2"}
    hand_size = 3
    prize_count = 2

    valid_states = []
    for hand in combinations(cards, hand_size):
        hand_set = set(hand)
        if not hand_set & starters:
            continue
        remaining = tuple(card for card in cards if card not in hand_set)
        for prizes in combinations(remaining, prize_count):
            valid_states.append((hand_set, set(prizes)))

    starter_target_ex_ante = sum(
        "S0" in prizes
        for _, prizes in valid_states
    ) / len(valid_states)
    nonstarter_target_ex_ante = sum(
        "X" in prizes
        for _, prizes in valid_states
    ) / len(valid_states)

    assert starter_target_ex_ante < prize_count / len(cards)
    assert nonstarter_target_ex_ante > prize_count / len(cards)

    exact_hand = {"S1", "F1", "F2"}
    exact_hand_states = [
        prizes
        for hand, prizes in valid_states
        if hand == exact_hand
    ]

    starter_given_hand = sum(
        "S0" in prizes
        for prizes in exact_hand_states
    ) / len(exact_hand_states)
    nonstarter_given_hand = sum(
        "X" in prizes
        for prizes in exact_hand_states
    ) / len(exact_hand_states)

    expected_given_hand = prize_count / (len(cards) - hand_size)
    _assert_close(starter_given_hand, expected_given_hand)
    _assert_close(nonstarter_given_hand, expected_given_hand)

    standard_absent_singleton = singleton_prized_probability(
        visible=False,
        visible_nonprize_cards=7,
        deck_size=60,
        prize_count=6,
    )
    _assert_close(standard_absent_singleton, 6 / 53)

    visible_singleton = singleton_prized_probability(
        visible=True,
        visible_nonprize_cards=7,
        deck_size=60,
        prize_count=6,
    )
    _assert_close(visible_singleton, 0.0)

    print("Small-deck ex-ante posterior after conditioning only on a valid start")
    print(f"  target starter Prized: {starter_target_ex_ante:.9%}")
    print(f"  target non-starter Prized: {nonstarter_target_ex_ante:.9%}")
    print()

    print("Condition on exact accepted hand {S1, F1, F2}")
    print(f"  absent target starter Prized: {starter_given_hand:.9%}")
    print(f"  absent target non-starter Prized: {nonstarter_given_hand:.9%}")
    print(f"  shared value P/(N-H): {expected_given_hand:.9%}")
    print()

    print("Standard 60-card exact-hand identity update")
    print(f"  any specific singleton absent from the 7-card hand: {standard_absent_singleton:.9%}")
    print(f"  singleton present in the hand: {visible_singleton:.9%}")
    print()

    print("All Prize-conditioning-layer checks passed.")


if __name__ == "__main__":
    main()
