"""Reproduce partial-inspection discard information values."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from partial_inspection_discard_value import PartialInspectionModel


def check(
    candidates: int,
    required: int,
    observed: int,
    expected_policy: float,
    expected_k1: float,
) -> None:
    model = PartialInspectionModel(
        unknown_pool=52,
        prize_count=6,
        candidate_classes=candidates,
        required_discards=required,
        observed_deck_cards=observed,
    )
    if abs(float(model.partial_policy_success) - expected_policy) > 1e-15:
        raise AssertionError(
            (candidates, required, observed, float(model.partial_policy_success))
        )
    if abs(float(model.full_k1_success) - expected_k1) > 1e-15:
        raise AssertionError(
            (candidates, required, observed, float(model.full_k1_success))
        )


def main() -> None:
    check(2, 1, 0, 0.8846153846153846, 0.9886877828054299)
    check(2, 1, 5, 0.8959276018099548, 0.9886877828054299)
    check(2, 1, 46, 0.9886877828054299, 0.9886877828054299)
    check(3, 1, 5, 0.9063348416289593, 0.9990950226244344)
    check(3, 2, 5, 0.7916289592760181, 0.9678733031674208)

    two = PartialInspectionModel(52, 6, 2, 1, 5)
    if not (
        two.no_inspection_success
        < two.partial_policy_success
        < two.full_k1_success
    ):
        raise AssertionError("top-five observation should have intermediate value")

    print(
        "m=2,d=1,q=5: "
        f"no_info={float(two.no_inspection_success):.9%}, "
        f"partial={float(two.partial_policy_success):.9%}, "
        f"K1={float(two.full_k1_success):.9%}"
    )
    print(
        "recovered_pp="
        f"{float(two.recovered_information_value) * 100:.9f}, "
        "residual_pp="
        f"{float(two.residual_information_value) * 100:.9f}"
    )
    print("All partial-inspection information checks passed.")


if __name__ == "__main__":
    main()
