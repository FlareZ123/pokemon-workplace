"""Reproduce a pre-search belief-driven policy switch."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from prize_information_value import Line, evaluate_prize_information  # noqa: E402


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual} != {expected}")


def evaluate(unknown_cards: int, robust_utility: float = 0.86):
    return evaluate_prize_information(
        {"A": 1},
        [
            Line("singleton A", (("A", 1),), utility=1.0),
            Line("robust B", (), utility=robust_utility),
        ],
        unknown_cards=unknown_cards,
        prize_count=6,
    )


def main() -> None:
    robust_utility = 0.86
    threshold = 6 / (1 - robust_utility)
    _assert_close(threshold, 42.85714285714285)

    rows = []
    for extra_non_target_observations in (0, 5, 10, 11, 13):
        unknown_cards = 53 - extra_non_target_observations
        result = evaluate(unknown_cards, robust_utility)
        singleton_expected = 1 - 6 / unknown_cards
        _assert_close(dict(result.fixed_line_values)["singleton A"], singleton_expected)
        _assert_close(dict(result.fixed_line_values)["robust B"], robust_utility)
        rows.append(
            (
                extra_non_target_observations,
                unknown_cards,
                singleton_expected,
                result.best_k0_line,
                result.k0_value,
                result.k1_value,
                result.information_value,
            )
        )

    assert rows[2][3] == "singleton A"
    assert rows[3][3] == "robust B"

    print(f"Robust line utility: {robust_utility:.3f}")
    print(f"Analytic singleton-choice threshold U*: {threshold:.9f}")
    print()
    print("misses | unseen U | singleton EV | K0 best | K0 value | K1 value | VPI")
    for row in rows:
        misses, unseen, singleton_ev, best, k0, k1, vpi = row
        print(
            f"{misses:6d} | {unseen:8d} | {singleton_ev:12.9%} | "
            f"{best:11s} | {k0:9.6%} | {k1:9.6%} | {vpi:9.6%}"
        )

    print()
    print("All belief-driven policy-switch checks passed.")


if __name__ == "__main__":
    main()
