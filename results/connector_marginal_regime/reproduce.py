"""Reproduce the exact direct-out versus disposable slot regime scan."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_marginal_regime import scan_direct_vs_disposable


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


def main() -> None:
    summary = scan_direct_vs_disposable()

    if summary.states_scanned != 9728:
        raise AssertionError(summary.states_scanned)
    if summary.violations:
        raise AssertionError(
            f"unexpected disposable-dominant states: "
            f"{len(summary.violations)}"
        )

    point = summary.closest_point
    if (
        point.discard_cost,
        point.target_a_copies,
        point.target_b_copies,
        point.disposable_nonstarters,
    ) != (1, 1, 8, 0):
        raise AssertionError(point)

    _assert_close(
        point.add_target_a_gain,
        0.05751693574907456,
    )
    _assert_close(
        point.add_target_b_gain,
        0.005172529052666616,
    )
    _assert_close(
        point.add_disposable_gain,
        0.004706085793422313,
    )
    _assert_close(
        point.disposable_to_weaker_direct_ratio,
        0.9098229793404764,
    )

    print(f"States scanned: {summary.states_scanned}")
    print(f"Disposable-dominant states: {len(summary.violations)}")
    print(
        "Closest state: "
        f"cost={point.discard_cost}, "
        f"A={point.target_a_copies}, "
        f"B={point.target_b_copies}, "
        f"D={point.disposable_nonstarters}"
    )
    print(
        "+1 A / +1 B / +1 disposable gains: "
        f"{point.add_target_a_gain:.6%} / "
        f"{point.add_target_b_gain:.6%} / "
        f"{point.add_disposable_gain:.6%}"
    )
    print(
        "Disposable / weaker-direct ratio: "
        f"{point.disposable_to_weaker_direct_ratio:.6%}"
    )
    print("All connector marginal-regime checks passed.")


if __name__ == "__main__":
    main()
