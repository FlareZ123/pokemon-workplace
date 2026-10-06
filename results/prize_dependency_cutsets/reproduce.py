"""Reproduce structural Prize cut-set examples."""

from __future__ import annotations

from math import comb, isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_information_value import (  # noqa: E402
    Line,
    all_lines_blocked_probability,
    minimal_failure_states,
)


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def main() -> None:
    independent_groups = {"A": 1, "B": 1}
    independent_lines = [
        Line("A line", (("A", 1),)),
        Line("B line", (("B", 1),)),
    ]
    independent_cutsets = minimal_failure_states(independent_groups, independent_lines)
    independent_failure = all_lines_blocked_probability(independent_groups, independent_lines)
    assert independent_cutsets == [{"A": 1, "B": 1}]
    _assert_close(independent_failure, comb(51, 4) / comb(53, 6))

    shared_groups = {"A": 1, "B": 1, "C": 1}
    shared_lines = [
        Line("A via C", (("A", 1), ("C", 1))),
        Line("B via C", (("B", 1), ("C", 1))),
    ]
    shared_cutsets = minimal_failure_states(shared_groups, shared_lines)
    shared_failure = all_lines_blocked_probability(shared_groups, shared_lines)
    assert shared_cutsets == [
        {"A": 0, "B": 0, "C": 1},
        {"A": 1, "B": 1, "C": 0},
    ]
    shared_success = (comb(52, 6) - comb(50, 4)) / comb(53, 6)
    _assert_close(shared_failure, 1.0 - shared_success)

    redundant_groups = {"A": 2, "B": 2}
    redundant_lines = [
        Line("A line", (("A", 1),)),
        Line("B line", (("B", 1),)),
    ]
    redundant_cutsets = minimal_failure_states(redundant_groups, redundant_lines)
    redundant_failure = all_lines_blocked_probability(redundant_groups, redundant_lines)
    assert redundant_cutsets == [{"A": 2, "B": 2}]
    _assert_close(redundant_failure, comb(49, 2) / comb(53, 6))

    print("Independent singleton alternatives")
    print(f"  minimal cut sets: {independent_cutsets}")
    print(f"  all-lines-blocked probability: {independent_failure:.9%}")
    print()

    print("Alternatives sharing singleton C")
    print(f"  minimal cut sets: {shared_cutsets}")
    print(f"  all-lines-blocked probability: {shared_failure:.9%}")
    print()

    print("Independent two-copy alternatives")
    print(f"  minimal cut sets: {redundant_cutsets}")
    print(f"  all-lines-blocked probability: {redundant_failure:.9%}")
    print()

    print("All Prize cut-set checks passed.")


if __name__ == "__main__":
    main()
