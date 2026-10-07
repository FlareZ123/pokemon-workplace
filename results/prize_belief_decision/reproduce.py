"""Reproduce belief-aware line evaluation after Prize mutations."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_belief_decision import evaluate_under_belief  # noqa: E402
from prize_belief_kernel import PrizeBelief  # noqa: E402
from prize_information_value import Line  # noqa: E402


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    groups = {
        "A": 1,
        "B": 1,
        "C": 1,
        "D": 1,
        "E": 1,
        "F": 1,
        "X": 1,
    }

    exact_before_swap = PrizeBelief.from_exact(
        {
            "A": 1,
            "B": 1,
            "C": 1,
            "D": 1,
            "E": 1,
            "F": 1,
            "X": 0,
        },
        prize_count=6,
    )

    after_unknown_swap = exact_before_swap.replace_unknown_position_with_known("X")

    lines = [
        Line("A line", (("A", 1),)),
        Line("B line", (("B", 1),)),
    ]

    result = evaluate_under_belief(groups, lines, after_unknown_swap)

    fixed = dict(result.fixed_line_values)
    _assert_close(fixed["A line"], 1 / 6)
    _assert_close(fixed["B line"], 1 / 6)
    _assert_close(result.fixed_value, 1 / 6)
    _assert_close(result.exact_information_value, 2 / 6)
    _assert_close(result.value_of_exact_information, 1 / 6)

    exact_after_swap = PrizeBelief.from_exact(
        {
            "A": 0,
            "B": 1,
            "C": 1,
            "D": 1,
            "E": 1,
            "F": 1,
            "X": 1,
        },
        prize_count=6,
    )
    reinspected = evaluate_under_belief(groups, lines, exact_after_swap)
    _assert_close(reinspected.fixed_value, 1.0)
    _assert_close(reinspected.value_of_exact_information, 0.0)

    print("After exact composition becomes a six-state swap posterior")
    print(f"  A-line fixed value: {fixed['A line']:.9%}")
    print(f"  B-line fixed value: {fixed['B line']:.9%}")
    print(f"  best commit-now value: {result.fixed_value:.9%}")
    print(f"  value after exact re-inspection: {result.exact_information_value:.9%}")
    print(f"  value of re-inspection: {result.value_of_exact_information:.9%}")
    print()

    print("After re-inspection reveals that A was the outgoing Prize")
    print(f"  best fixed value: {reinspected.fixed_value:.9%}")
    print(f"  remaining value of exact information: {reinspected.value_of_exact_information:.9%}")
    print()

    print("All belief-aware line-evaluation checks passed.")


if __name__ == "__main__":
    main()
