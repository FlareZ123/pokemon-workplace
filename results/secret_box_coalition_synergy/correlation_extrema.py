"""Exact marginal-constraint LP bounds for observed output-mask synergy."""

from fractions import Fraction
from math import prod
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from category_availability_extrema import sharp_expectation_bounds
from secret_box_coalition_synergy import (
    expected_successes,
    synergy_counts,
)
from reproduce import MASK_SUCCESS_COUNTS, SINGLETON_SIGNATURE_COUNTS


D = synergy_counts(MASK_SUCCESS_COUNTS, SINGLETON_SIGNATURE_COUNTS)


def verify_witness(
    scores: tuple[int, ...],
    marginals: tuple[Fraction, ...],
    bound: tuple[Fraction, dict[int, Fraction]],
) -> None:
    value, distribution = bound
    assert sum(distribution.values(), Fraction(0)) == 1
    assert all(p > 0 for p in distribution.values())
    assert len(distribution) <= 5
    assert all(0 <= mask < 16 for mask in distribution)
    for i, marginal in enumerate(marginals):
        assert sum(
            (p for mask, p in distribution.items() if mask & (1 << i)),
            Fraction(0),
        ) == marginal
    assert sum(
        (scores[mask] * p for mask, p in distribution.items()),
        Fraction(0),
    ) == value


def main() -> None:
    assert D == (
        0, 0, 0, 0,
        0, 0, 42, 0,
        0, 0, 1_917, 0,
        42, 0, 42, 0,
    )
    for q in (
        Fraction(0), Fraction(1, 4), Fraction(1, 2),
        Fraction(3, 4), Fraction(1),
    ):
        p = (q,) * 4
        least, greatest = sharp_expectation_bounds(D, p)
        assert least[0] == 0
        assert greatest[0] == 1_917 * min(q, 1-q)
        verify_witness(D, p, least)
        verify_witness(D, p, greatest)

    asymmetric = (
        Fraction(1, 4), Fraction(3, 4),
        Fraction(1, 3), Fraction(2, 3),
    )
    least, greatest = sharp_expectation_bounds(D, asymmetric)
    verify_witness(D, asymmetric, least)
    verify_witness(D, asymmetric, greatest)
    assert least[0] == 7
    assert greatest[0] == Fraction(2_563, 2)

    # Pointwise affine lower certificate; average gives 42*(p_T+p_St-1-p_I).
    for mask, score in enumerate(D):
        assert score >= 42 * (
            bool(mask & 2) + bool(mask & 8)
            - 1 - bool(mask & 1)
        )
    assert 42 * (asymmetric[1] + asymmetric[3] - 1 - asymmetric[0]) == 7
    independent = expected_successes(D, asymmetric)
    assert independent == Fraction(3_911, 8)

    additive = tuple(
        sum((4, 7, 10, 13)[i] for i in range(4) if mask & (1 << i))
        for mask in range(16)
    )
    least_add, greatest_add = sharp_expectation_bounds(additive, asymmetric)
    invariant = sum(
        (w * p for w, p in zip((4, 7, 10, 13), asymmetric)),
        Fraction(0),
    )
    assert least_add[0] == greatest_add[0] == invariant

    deterministic = (Fraction(0), Fraction(1), Fraction(0), Fraction(1))
    least_det, greatest_det = sharp_expectation_bounds(D, deterministic)
    assert least_det[0] == greatest_det[0] == 1_917

    print("Equal marginals: sharp bound [0, 1917*min(q,1-q)] verified")
    print("Asymmetric marginals:", asymmetric)
    print("Asymmetric exact minimum:", least[0], "witness:", least[1])
    print("Asymmetric exact maximum:", greatest[0], "witness:", greatest[1])
    print("Asymmetric independent:", independent)
    print("Asymmetric forced lower certificate:", 7)
    print("Additive marginal-only expectation:", invariant)
    print("All exact marginal-correlation extreme checks passed.")


if __name__ == "__main__":
    main()
