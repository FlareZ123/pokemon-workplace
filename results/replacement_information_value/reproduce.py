"""Reproduce replacement-multiplicity information-value results."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from replacement_information_value import ReplacementInformationModel


def check(
    replacements: tuple[int, ...],
    required: int,
    expected_k0: float,
    expected_k1: float,
) -> None:
    model = ReplacementInformationModel(
        unknown_pool=52,
        prize_count=6,
        replacement_copies=replacements,
        required_discards=required,
    )
    subset, blind = model.blind_optimal
    if abs(float(blind) - expected_k0) > 1e-15:
        raise AssertionError((replacements, required, subset, float(blind)))
    if abs(float(model.informed_success) - expected_k1) > 1e-15:
        raise AssertionError(
            (replacements, required, float(model.informed_success))
        )


def main() -> None:
    check((1, 1), 1, 0.8846153846153846, 0.9886877828054299)
    check((2, 2), 1, 0.9886877828054299, 0.9999445932219041)
    check((3, 3), 1, 0.9990950226244344, 0.9999999508805159)
    check((1, 1, 1), 2, 0.7805429864253394, 0.9678733031674208)
    check((2, 2, 2), 2, 0.9774309723889556, 0.9998338779046807)

    asymmetric = ReplacementInformationModel(
        unknown_pool=52,
        prize_count=6,
        replacement_copies=(1, 2, 3),
        required_discards=2,
    )
    subset, blind = asymmetric.blind_optimal
    if subset != (1, 2):
        raise AssertionError(subset)
    if blind != asymmetric.fixed_subset_success((1, 2)):
        raise AssertionError("optimal subset probability mismatch")
    if asymmetric.fixed_subset_success((0, 1)) >= blind:
        raise AssertionError("one-copy candidate should not enter optimal pair")
    if asymmetric.information_value <= Fraction(0, 1):
        raise AssertionError("asymmetric case should retain positive information value")

    print(
        "two candidates, one replacement each: "
        "gap=10.407239819 pp"
    )
    print(
        "two candidates, two replacements each: "
        "gap=1.125681042 pp"
    )
    print(
        "two candidates, three replacements each: "
        "gap=0.090492826 pp"
    )
    print(
        "three candidates, two required discards, one replacement each: "
        "gap=18.733031674 pp"
    )
    print(
        "three candidates, two required discards, two replacements each: "
        "gap=2.240290552 pp"
    )
    print("All replacement-information checks passed.")


if __name__ == "__main__":
    main()
