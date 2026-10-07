"""Reproduce partial Prize-information value for two singleton lines."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from partial_prize_information import (  # noqa: E402
    marginal_value_per_additional_inspected_prize,
    two_singleton_value_after_k_inspections,
)
from prize_belief_decision import (  # noqa: E402
    expected_value_after_one_random_prize_inspection,
)
from prize_belief_kernel import PrizeBelief  # noqa: E402
from prize_information_value import Line  # noqa: E402


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    unknown_cards = 53
    prize_count = 6

    belief = PrizeBelief.from_hypergeometric(
        {"A": 1, "B": 1},
        pool_size=unknown_cards,
        prize_count=prize_count,
    )
    group_sizes = {"A": 1, "B": 1}
    lines = [
        Line("A line", (("A", 1),)),
        Line("B line", (("B", 1),)),
    ]

    one_peek = expected_value_after_one_random_prize_inspection(
        group_sizes,
        lines,
        belief,
    )
    _assert_close(one_peek.current_value, 47 / 53)
    _assert_close(one_peek.post_inspection_value, 47 / 52)
    _assert_close(
        one_peek.inspection_value,
        47 / 52 - 47 / 53,
    )

    increment = marginal_value_per_additional_inspected_prize(
        unknown_cards,
        prize_count,
    )
    _assert_close(increment, 47 / (53 * 52))

    values = [
        two_singleton_value_after_k_inspections(
            unknown_cards,
            prize_count,
            k,
        )
        for k in range(prize_count + 1)
    ]

    for k, value in enumerate(values):
        _assert_close(
            value,
            47 * (52 + k) / (53 * 52),
        )
        if k:
            _assert_close(value - values[k - 1], increment)

    full_information = 1.0 - (6 * 5) / (53 * 52)
    _assert_close(values[-1], full_information)

    print("Two independent singleton lines")
    print("inspected Prizes | expected adaptive availability")
    for k, value in enumerate(values):
        print(f"{k:16d} | {value:.9%}")

    print()
    print(f"Per additional inspected Prize: {increment:.9%}")
    print(f"One-Prize generic belief evaluator: {one_peek.post_inspection_value:.9%}")
    print(f"All-six exact information value: {values[-1]:.9%}")
    print()
    print("All partial Prize-information checks passed.")


if __name__ == "__main__":
    main()
