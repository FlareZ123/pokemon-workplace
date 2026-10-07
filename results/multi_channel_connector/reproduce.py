"""Reproduce multi-channel one-output versus Secret Box-like access."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from multi_channel_connector import multi_channel_connector_access


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


def _first_positive_crossover(channel_count: int) -> int:
    targets = (2,) * channel_count
    max_disposable = 60 - 12 - sum(targets) - 1
    for disposable in range(max_disposable + 1):
        one = multi_channel_connector_access(
            60,
            6,
            starter_cards=12,
            target_counts=targets,
            disposable_nonstarters=disposable,
            discard_cost=2,
            connector_capacity=1,
        )
        multi = multi_channel_connector_access(
            60,
            6,
            starter_cards=12,
            target_counts=targets,
            disposable_nonstarters=disposable,
            discard_cost=3,
            connector_capacity=channel_count,
        )
        if multi.joint_access > one.joint_access + 1e-15:
            return disposable
    raise AssertionError("no positive crossover found")


def main() -> None:
    expected = {
        2: (
            0.037993300152223186,
            0.055643064911662904,
            0.0665519390431932,
        ),
        3: (
            0.005751808746216717,
            0.008652151613076545,
            0.03420250478741763,
        ),
        4: (
            0.0006823260233079601,
            0.0009131990873366033,
            0.0288512109606193,
        ),
    }

    print("Channels | direct | capacity-1 cost-2 | multi-output cost-3")
    for channel_count, values in expected.items():
        targets = (2,) * channel_count
        one = multi_channel_connector_access(
            60,
            6,
            starter_cards=12,
            target_counts=targets,
            disposable_nonstarters=20,
            discard_cost=2,
            connector_capacity=1,
        )
        multi = multi_channel_connector_access(
            60,
            6,
            starter_cards=12,
            target_counts=targets,
            disposable_nonstarters=20,
            discard_cost=3,
            connector_capacity=channel_count,
        )
        _assert_close(one.state_mass, 1.0)
        _assert_close(multi.state_mass, 1.0)
        _assert_close(one.direct_joint_access, values[0])
        _assert_close(one.joint_access, values[1])
        _assert_close(multi.joint_access, values[2])

        print(
            f"{channel_count:8d} | "
            f"{one.direct_joint_access:.6%} | "
            f"{one.joint_access:.6%} | "
            f"{multi.joint_access:.6%}"
        )

    crossovers = {
        2: _first_positive_crossover(2),
        3: _first_positive_crossover(3),
        4: _first_positive_crossover(4),
    }
    if crossovers != {2: 13, 3: 4, 4: 3}:
        raise AssertionError(crossovers)

    print()
    print(f"First positive crossovers: {crossovers}")
    print("All multi-channel connector checks passed.")


if __name__ == "__main__":
    main()
