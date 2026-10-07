"""Reproduce the Computer Search versus Secret Box capacity comparison."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_domination import two_channel_connector_access_collapsed
from connector_output_capacity import two_channel_output_capacity_access


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


def main() -> None:
    expected = {
        5: (0.056630117841, 0.055217461004),
        10: (0.061885863494, 0.059156451677),
        15: (0.068826324002, 0.068673712788),
        16: (0.070289511045, 0.071257618506),
        20: (0.076078999885, 0.083523251612),
        25: (0.082628828443, 0.101856737385),
        30: (0.087818183764, 0.120934873452),
        35: (0.091346876715, 0.137838769407),
    }

    print("D | capacity-1 cost-2 | capacity-2 cost-3 | difference")
    for disposable, (one_expected, two_expected) in expected.items():
        one = two_channel_output_capacity_access(
            60,
            6,
            starter_cards=12,
            target_a_copies=3,
            target_b_copies=2,
            disposable_nonstarters=disposable,
            discard_cost=2,
            connector_capacity=1,
        )
        two = two_channel_output_capacity_access(
            60,
            6,
            starter_cards=12,
            target_a_copies=3,
            target_b_copies=2,
            disposable_nonstarters=disposable,
            discard_cost=3,
            connector_capacity=2,
        )
        reference = two_channel_connector_access_collapsed(
            60,
            6,
            starter_cards=12,
            target_a_copies=3,
            target_b_copies=2,
            disposable_nonstarters=disposable,
            discard_cost=2,
        )

        _assert_close(one.state_mass, 1.0)
        _assert_close(two.state_mass, 1.0)
        _assert_close(one.joint_access, one_expected)
        _assert_close(two.joint_access, two_expected)
        _assert_close(
            one.joint_access,
            reference.capacity_aware_gated_access,
        )

        print(
            f"{disposable:2d} | "
            f"{one.joint_access:.6%} | "
            f"{two.joint_access:.6%} | "
            f"{two.joint_access - one.joint_access:+.6%}"
        )

    if expected[15][1] >= expected[15][0]:
        raise AssertionError("expected capacity-1 connector to lead at D=15")
    if expected[16][1] <= expected[16][0]:
        raise AssertionError("expected capacity-2 connector to lead at D=16")

    print()
    print("Positive-payability crossover occurs between D=15 and D=16.")
    print("All output-capacity checks passed.")


if __name__ == "__main__":
    main()
