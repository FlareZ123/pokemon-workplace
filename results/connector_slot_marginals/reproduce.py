"""Reproduce connector slot-marginal calculations."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from connector_slot_marginals import connector_slot_marginals


def _assert_close(actual: float, expected: float) -> None:
    if not isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{actual!r} != {expected!r}")


def main() -> None:
    result = connector_slot_marginals(
        60,
        6,
        starter_cards=12,
        target_a_copies=3,
        target_b_copies=2,
        disposable_nonstarters=20,
        discard_cost=2,
    )

    _assert_close(
        result.baseline.capacity_aware_gated_access,
        0.07607899988452609,
    )
    _assert_close(
        result.baseline.naive_shared_connector_gated_access,
        0.1212041742533695,
    )

    expected = {
        "target A": (
            result.add_target_a,
            0.018782949412152348,
            0.015007886958661996,
        ),
        "target B": (
            result.add_target_b,
            0.02744034467550764,
            0.024051124732636526,
        ),
        "disposable": (
            result.add_disposable,
            0.001392384616581102,
            0.0036014322531173343,
        ),
    }

    print("Slot | realistic gain | connector-naive gain | naive / realistic")
    for label, (marginal, realistic, naive) in expected.items():
        _assert_close(marginal.realistic_gain, realistic)
        _assert_close(marginal.naive_gated_gain, naive)
        _assert_close(marginal.naive_bias, naive - realistic)
        _assert_close(
            marginal.naive_to_realistic_ratio,
            naive / realistic,
        )
        print(
            f"{label:10s} | "
            f"{marginal.realistic_gain:.6%} | "
            f"{marginal.naive_gated_gain:.6%} | "
            f"{marginal.naive_to_realistic_ratio:.6f}"
        )

    realistic_ratio = (
        result.add_target_b.realistic_gain
        / result.add_disposable.realistic_gain
    )
    naive_ratio = (
        result.add_target_b.naive_gated_gain
        / result.add_disposable.naive_gated_gain
    )
    _assert_close(realistic_ratio, 19.70744602370384)
    _assert_close(naive_ratio, 6.678211067782355)

    print()
    print(
        "Target-B / disposable marginal ratio: "
        f"realistic={realistic_ratio:.6f}, "
        f"connector-naive={naive_ratio:.6f}"
    )
    print("All connector slot-marginal checks passed.")


if __name__ == "__main__":
    main()
