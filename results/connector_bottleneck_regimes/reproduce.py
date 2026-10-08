"""Reproduce the connector bottleneck-regime scan."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_bottleneck_regimes import scan_bottleneck_regimes
from connector_slot_marginals import connector_slot_marginals


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


EXPECTED = {
    1: {
        "minimum_gap": 0.008172981357681817,
        "minimum_gap_state": (1, 1, 0),
        "maximum_disposable_gain": 0.004446817979898182,
        "maximum_disposable_state": (4, 4, 0),
    },
    2: {
        "minimum_gap": 0.009376089893137204,
        "minimum_gap_state": (1, 1, 2),
        "maximum_disposable_gain": 0.002034205018141555,
        "maximum_disposable_state": (4, 4, 15),
    },
    3: {
        "minimum_gap": 0.009473194852463226,
        "minimum_gap_state": (1, 1, 5),
        "maximum_disposable_gain": 0.0020038781269483275,
        "maximum_disposable_state": (4, 4, 30),
    },
}


def _validate_full_solver(point) -> None:
    exact = connector_slot_marginals(
        60,
        6,
        starter_cards=12,
        target_a_copies=point.target_a_copies,
        target_b_copies=point.target_b_copies,
        disposable_nonstarters=point.disposable_nonstarters,
        discard_cost=point.discard_cost,
    )
    _assert_close(
        point.baseline_realistic_access,
        exact.baseline.capacity_aware_gated_access,
    )
    _assert_close(point.add_target_a_gain, exact.add_target_a.realistic_gain)
    _assert_close(point.add_target_b_gain, exact.add_target_b.realistic_gain)
    _assert_close(
        point.add_disposable_gain,
        exact.add_disposable.realistic_gain,
    )


def main() -> None:
    print(
        "cost | A wins | B wins | A/B ties | disposable wins | "
        "min direct-D gap | max D marginal"
    )

    for discard_cost in (1, 2, 3):
        summary = scan_bottleneck_regimes(discard_cost=discard_cost)

        if len(summary.points) != 576:
            raise AssertionError(len(summary.points))
        if summary.target_a_wins != 216:
            raise AssertionError(summary.target_a_wins)
        if summary.target_b_wins != 216:
            raise AssertionError(summary.target_b_wins)
        if summary.target_ties != 144:
            raise AssertionError(summary.target_ties)
        if summary.disposable_wins != 0:
            raise AssertionError(summary.disposable_wins)
        if summary.mixed_ties != 0:
            raise AssertionError(summary.mixed_ties)

        for point in summary.points:
            if point.target_a_copies < point.target_b_copies:
                expected_winner = "target_a"
            elif point.target_b_copies < point.target_a_copies:
                expected_winner = "target_b"
            else:
                expected_winner = "target_tie"
            if point.winner != expected_winner:
                raise AssertionError(
                    (point, expected_winner)
                )

        expected = EXPECTED[discard_cost]
        _assert_close(
            summary.minimum_direct_over_disposable_gap,
            expected["minimum_gap"],
        )
        min_state = (
            summary.minimum_gap_point.target_a_copies,
            summary.minimum_gap_point.target_b_copies,
            summary.minimum_gap_point.disposable_nonstarters,
        )
        if min_state != expected["minimum_gap_state"]:
            raise AssertionError(min_state)

        _assert_close(
            summary.maximum_disposable_gain,
            expected["maximum_disposable_gain"],
        )
        max_state = (
            summary.maximum_disposable_point.target_a_copies,
            summary.maximum_disposable_point.target_b_copies,
            summary.maximum_disposable_point.disposable_nonstarters,
        )
        if max_state != expected["maximum_disposable_state"]:
            raise AssertionError(max_state)

        # The dense scan uses the Prize-collapsed solver. Cross-check two
        # representative states against the original full Prize enumeration.
        _validate_full_solver(summary.minimum_gap_point)
        _validate_full_solver(summary.maximum_disposable_point)

        print(
            f"{discard_cost:4d} | "
            f"{summary.target_a_wins:6d} | "
            f"{summary.target_b_wins:6d} | "
            f"{summary.target_ties:8d} | "
            f"{summary.disposable_wins:15d} | "
            f"{summary.minimum_direct_over_disposable_gap:.6%} | "
            f"{summary.maximum_disposable_gain:.6%}"
        )

    print()
    print("All connector bottleneck-regime checks passed.")


if __name__ == "__main__":
    main()
