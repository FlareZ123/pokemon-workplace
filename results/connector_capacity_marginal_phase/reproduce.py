"""Reproduce the effective connector-capacity marginal phase."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_capacity_marginal_phase import (
    minimum_payable_success_slots,
    scan_symmetric_capacity_phase,
)
from multi_output_slot_marginals import fixed_size_multi_output_marginals


EXPECTED_INTERVALS = {
    2: {1: (), 2: ()},
    3: {1: (), 2: (), 3: ((17, 33),)},
    4: {1: (), 2: (), 3: ((10, 19),), 4: ((5, 38),)},
}

EXPECTED_PEAKS = {
    (2, 1): (30, 0.058576486028850815),
    (2, 2): (26, 0.2256298633118314),
    (3, 1): (40, 0.08601016234490792),
    (3, 2): (24, 0.3151382112774837),
    (3, 3): (24, 1.2680739254636444),
    (4, 2): (26, 0.319227454039164),
    (4, 3): (14, 1.1368599651438016),
    (4, 4): (18, 5.951119241553518),
}


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


def _point_at(phase, disposable: int):
    return phase.points[disposable]


def main() -> None:
    print(
        "channels | capacity | min paid-success slots | "
        "disposable-dominant D | peak D | peak ratio"
    )

    for channel_count in (2, 3, 4):
        for capacity in range(1, channel_count + 1):
            phase = scan_symmetric_capacity_phase(
                channel_count,
                capacity,
            )
            expected = EXPECTED_INTERVALS[channel_count][capacity]
            if phase.disposable_dominant_intervals != expected:
                raise AssertionError(
                    (
                        channel_count,
                        capacity,
                        phase.disposable_dominant_intervals,
                        expected,
                    )
                )

            expected_slots = (
                2 + 3 + max(0, channel_count - capacity)
            )
            if phase.minimum_payable_success_slots != expected_slots:
                raise AssertionError(
                    phase.minimum_payable_success_slots
                )
            if minimum_payable_success_slots(
                channel_count,
                capacity,
                3,
            ) != expected_slots:
                raise AssertionError("slot lower bound mismatch")

            for start, end in expected:
                if start > 0:
                    before = _point_at(phase, start - 1)
                    if (
                        before.add_disposable_gain
                        > before.add_direct_gain + 1e-15
                    ):
                        raise AssertionError(("before", before))
                first = _point_at(phase, start)
                last = _point_at(phase, end)
                if not (
                    first.add_disposable_gain
                    > first.add_direct_gain + 1e-15
                ):
                    raise AssertionError(("first", first))
                if not (
                    last.add_disposable_gain
                    > last.add_direct_gain + 1e-15
                ):
                    raise AssertionError(("last", last))
                if end < phase.max_disposable:
                    after = _point_at(phase, end + 1)
                    if (
                        after.add_disposable_gain
                        > after.add_direct_gain + 1e-15
                    ):
                        raise AssertionError(("after", after))

            if phase.max_disposable >= 20:
                point = _point_at(phase, 20)
                existing = fixed_size_multi_output_marginals(
                    60,
                    6,
                    starter_cards=12,
                    target_counts=(2,) * channel_count,
                    disposable_nonstarters=20,
                    discard_cost=3,
                    connector_capacity=capacity,
                )
                _assert_close(
                    point.baseline_joint_access,
                    existing.baseline_joint_access,
                )
                _assert_close(
                    point.add_direct_gain,
                    existing.add_target_gains[0],
                )
                _assert_close(
                    point.add_disposable_gain,
                    existing.add_disposable_gain,
                )

            if channel_count == 4 and capacity == 1:
                if phase.minimum_payable_success_slots != 8:
                    raise AssertionError("expected eight-slot lower bound")
                if max(
                    abs(point.add_disposable_gain)
                    for point in phase.points
                ) > 1e-15:
                    raise AssertionError(
                        "capacity-one disposable marginal should be zero"
                    )
                peak_d = "n/a"
                peak_ratio = "0"
            else:
                expected_peak = EXPECTED_PEAKS[
                    (channel_count, capacity)
                ]
                if (
                    phase.peak_ratio_point.disposable_nonstarters
                    != expected_peak[0]
                ):
                    raise AssertionError(
                        phase.peak_ratio_point.disposable_nonstarters
                    )
                _assert_close(
                    phase.peak_ratio_point.disposable_to_direct_ratio,
                    expected_peak[1],
                )
                peak_d = str(
                    phase.peak_ratio_point.disposable_nonstarters
                )
                peak_ratio = (
                    f"{phase.peak_ratio_point.disposable_to_direct_ratio:.6f}"
                )

            interval_text = (
                ", ".join(f"{a}-{b}" for a, b in expected)
                if expected
                else "none"
            )
            print(
                f"{channel_count:8d} | "
                f"{capacity:8d} | "
                f"{phase.minimum_payable_success_slots:22d} | "
                f"{interval_text:21s} | "
                f"{peak_d:6s} | "
                f"{peak_ratio}"
            )

    print()
    print("All connector capacity-phase checks passed.")


if __name__ == "__main__":
    main()
