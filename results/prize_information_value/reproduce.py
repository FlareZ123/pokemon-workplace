"""Reproduce the initial Prize information-value examples."""

from __future__ import annotations

from itertools import combinations
from math import comb, isclose

from tools.prize_information_value import (
    Line,
    evaluate_prize_information,
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
    result = evaluate_prize_information(
        {"A": 1, "B": 1},
        [
            Line("A line", (("A", 1),)),
            Line("B line", (("B", 1),)),
        ],
    )

    fixed = 47 / 53
    adaptive = 1.0 - comb(51, 4) / comb(53, 6)

    _assert_close(result.k0_value, fixed)
    _assert_close(result.k1_value, adaptive)
    _assert_close(result.information_value, adaptive - fixed)

    print("Two independent singleton alternatives")
    print(f"  K0 fixed success: {result.k0_value:.9%}")
    print(f"  K1 adaptive success: {result.k1_value:.9%}")
    print(f"  information value: {result.information_value:.9%}")
    print()


def _three_singleton_alternatives() -> None:
    result = evaluate_prize_information(
        {"A": 1, "B": 1, "C": 1},
        [
            Line("A line", (("A", 1),)),
            Line("B line", (("B", 1),)),
            Line("C line", (("C", 1),)),
        ],
    )

    fixed = 47 / 53
    adaptive = 1.0 - comb(50, 3) / comb(53, 6)

    _assert_close(result.k0_value, fixed)
    _assert_close(result.k1_value, adaptive)

    print("Three independent singleton alternatives")
    print(f"  K0 fixed success: {result.k0_value:.9%}")
    print(f"  K1 adaptive success: {result.k1_value:.9%}")
    print(f"  information value: {result.information_value:.9%}")
    print()


def _shared_singleton_connector() -> None:
    result = evaluate_prize_information(
        {"A": 1, "B": 1, "C": 1},
        [
            Line("A via C", (("A", 1), ("C", 1))),
            Line("B via C", (("B", 1), ("C", 1))),
        ],
    )

    fixed = comb(51, 6) / comb(53, 6)
    adaptive = (comb(52, 6) - comb(50, 4)) / comb(53, 6)

    _assert_close(result.k0_value, fixed)
    _assert_close(result.k1_value, adaptive)

    print("Two alternatives sharing singleton connector C")
    print(f"  K0 fixed success: {result.k0_value:.9%}")
    print(f"  K1 adaptive success: {result.k1_value:.9%}")
    print(f"  information value: {result.information_value:.9%}")
    print()


def _two_copy_alternatives() -> None:
    result = evaluate_prize_information(
        {"A": 2, "B": 2},
        [
            Line("A line", (("A", 1),)),
            Line("B line", (("B", 1),)),
        ],
    )

    fixed = 1.0 - comb(51, 4) / comb(53, 6)
    adaptive = 1.0 - comb(49, 2) / comb(53, 6)

    _assert_close(result.k0_value, fixed)
    _assert_close(result.k1_value, adaptive)

    print("Two independent two-copy alternatives")
    print(f"  K0 fixed success: {result.k0_value:.9%}")
    print(f"  K1 adaptive success: {result.k1_value:.9%}")
    print(f"  information value: {result.information_value:.9%}")
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
