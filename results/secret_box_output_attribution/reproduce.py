"""Reproduce redundancy-aware Secret Box output attribution."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from subset_shapley import shapley_values


MASK_SUCCESS_COUNTS = (
    0, 20_783, 2_313, 20_783,
    20_703, 20_785, 20_785, 20_785,
    623, 20_783, 4_849, 20_783,
    20_745, 20_785, 20_785, 20_785,
)

EXPECTED = (
    Fraction(117_035, 12),
    Fraction(11_287, 12),
    Fraction(116_651, 12),
    Fraction(4_447, 12),
)


def main() -> None:
    additive = tuple(
        sum(
            weight
            for index, weight in enumerate((2, 3, 5))
            if mask & (1 << index)
        )
        for mask in range(8)
    )
    if shapley_values(additive) != (
        Fraction(2),
        Fraction(3),
        Fraction(5),
    ):
        raise AssertionError("additive Shapley regression failed")

    redundant_or = (0, 1, 1, 1)
    if shapley_values(redundant_or) != (
        Fraction(1, 2),
        Fraction(1, 2),
    ):
        raise AssertionError("redundant OR regression failed")

    values = shapley_values(MASK_SUCCESS_COUNTS)
    if values != EXPECTED:
        raise AssertionError(f"{values!r} != {EXPECTED!r}")
    if sum(values) != MASK_SUCCESS_COUNTS[-1]:
        raise AssertionError("Shapley efficiency identity failed")

    names = ("Item", "Tool", "Supporter", "Stadium")
    incremental = MASK_SUCCESS_COUNTS[-1]
    trials = 500_000
    for name, value in zip(names, values):
        share = float(value / incremental)
        total_gain_pp = float(value / trials * 100)
        print(
            f"{name}: exact={value}, "
            f"incremental_share={share:.9%}, "
            f"overall_gain_credit={total_gain_pp:.9f} pp"
        )

    print(f"sum={sum(values)}")
    print("All Secret Box output-attribution checks passed.")


if __name__ == "__main__":
    main()
