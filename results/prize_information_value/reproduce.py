"""Reproduce the initial Prize information-value examples."""

from __future__ import annotations

from itertools import combinations
from math import comb, isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_information_value import (  # noqa: E402
    Line,
    all_lines_blocked_probability,
    evaluate_prize_information,
    minimal_failure_states,
    prize_state_probabilities,
)


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def _validate_small_population() -> None:
    """Check grouped state probabilities against labeled Prize enumeration."""
    group_sizes = {"A": 1, "B": 2, "C": 1}
    unknown_cards = 8
    prize_count = 2

    labels = ["A1", "B1", "B2", "C1", "F1", "F2", "F3", "F4"]
    brute: dict[tuple[int, int, int], float] = {}
    total = comb(unknown_cards, prize_count)

    for prize_indices in combinations(range(unknown_cards), prize_count):
        chosen = {labels[index] for index in prize_indices}
        state = (
            int("A1" in chosen),
            int("B1" in chosen) + int("B2" in chosen),
            int("C1" in chosen),
        )
        brute[state] = brute.get(state, 0.0) + 1.0 / total

    modeled = {
        (state["A"], state["B"], state["C"]): probability
        for state, probability in prize_state_probabilities(
            group_sizes,
            unknown_cards=unknown_cards,
            prize_count=prize_count,
        )
    }

    if set(brute) != set(modeled):
        raise AssertionError("grouped state support differs from brute-force enumeration")
    for state, probability in brute.items():
        _assert_close(modeled[state], probability)


def _two_singleton_alternatives() -> None:
    group_sizes = {"A": 1, "B": 1}
    lines = [
        Line("A line", (("A", 1),)),
        Line("B line", (("B", 1),)),
    ]
    result = evaluate_prize_information(group_sizes, lines)

    fixed = 47 / 53
    adaptive = 1.0 - comb(51, 4) / comb(53, 6)

    _assert_close(result.k0_value, fixed)
    _assert_close(result.k1_value, adaptive)
    _assert_close(result.information_value, adaptive - fixed)
    _assert_close(all_lines_blocked_probability(group_sizes, lines), 1.0 - adaptive)
    assert minimal_failure_states(group_sizes, lines) == [{"A": 1, "B": 1}]

    print("Two independent singleton alternatives")
    print(f"  K0 fixed success: {result.k0_value:.9%}")
    print(f"  K1 adaptive success: {result.k1_value:.9%}")
    print(f"  information value: {result.information_value:.9%}")
    print(f"  minimal cut sets: {minimal_failure_states(group_sizes, lines)}")
    print()


def _three_singleton_alternatives() -> None:
    group_sizes = {"A": 1, "B": 1, "C": 1}
    lines = [
        Line("A line", (("A", 1),)),
        Line("B line", (("B", 1),)),
        Line("C line", (("C", 1),)),
    ]
    result = evaluate_prize_information(group_sizes, lines)

    fixed = 47 / 53
    adaptive = 1.0 - comb(50, 3) / comb(53, 6)

    _assert_close(result.k0_value, fixed)
    _assert_close(result.k1_value, adaptive)
    _assert_close(all_lines_blocked_probability(group_sizes, lines), 1.0 - adaptive)
    assert minimal_failure_states(group_sizes, lines) == [{"A": 1, "B": 1, "C": 1}]

    print("Three independent singleton alternatives")
    print(f"  K0 fixed success: {result.k0_value:.9%}")
    print(f"  K1 adaptive success: {result.k1_value:.9%}")
    print(f"  information value: {result.information_value:.9%}")
    print(f"  minimal cut sets: {minimal_failure_states(group_sizes, lines)}")
    print()


def _shared_singleton_connector() -> None:
    group_sizes = {"A": 1, "B": 1, "C": 1}
    lines = [
        Line("A via C", (("A", 1), ("C", 1))),
        Line("B via C", (("B", 1), ("C", 1))),
    ]
    result = evaluate_prize_information(group_sizes, lines)

    fixed = comb(51, 6) / comb(53, 6)
    adaptive = (comb(52, 6) - comb(50, 4)) / comb(53, 6)

    _assert_close(result.k0_value, fixed)
    _assert_close(result.k1_value, adaptive)
    _assert_close(all_lines_blocked_probability(group_sizes, lines), 1.0 - adaptive)
    assert minimal_failure_states(group_sizes, lines) == [
        {"A": 0, "B": 0, "C": 1},
        {"A": 1, "B": 1, "C": 0},
    ]

    print("Two alternatives sharing singleton connector C")
    print(f"  K0 fixed success: {result.k0_value:.9%}")
    print(f"  K1 adaptive success: {result.k1_value:.9%}")
    print(f"  information value: {result.information_value:.9%}")
    print(f"  minimal cut sets: {minimal_failure_states(group_sizes, lines)}")
    print()


def _two_copy_alternatives() -> None:
    group_sizes = {"A": 2, "B": 2}
    lines = [
        Line("A line", (("A", 1),)),
        Line("B line", (("B", 1),)),
    ]
    result = evaluate_prize_information(group_sizes, lines)

    fixed = 1.0 - comb(51, 4) / comb(53, 6)
    adaptive = 1.0 - comb(49, 2) / comb(53, 6)

    _assert_close(result.k0_value, fixed)
    _assert_close(result.k1_value, adaptive)
    _assert_close(all_lines_blocked_probability(group_sizes, lines), 1.0 - adaptive)
    assert minimal_failure_states(group_sizes, lines) == [{"A": 2, "B": 2}]

    print("Two independent two-copy alternatives")
    print(f"  K0 fixed success: {result.k0_value:.9%}")
    print(f"  K1 adaptive success: {result.k1_value:.9%}")
    print(f"  information value: {result.information_value:.9%}")
    print(f"  minimal cut sets: {minimal_failure_states(group_sizes, lines)}")
    print()


def main() -> None:
    _validate_small_population()
    _two_singleton_alternatives()
    _three_singleton_alternatives()
    _shared_singleton_connector()
    _two_copy_alternatives()
    print("All Prize-information checks passed.")


if __name__ == "__main__":
    main()
