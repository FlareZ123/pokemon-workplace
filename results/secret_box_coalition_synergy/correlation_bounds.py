"""Sharp category-dependence bounds from the fixed Aichi coalition table.

All four output categories have identical marginal availability q, with
otherwise arbitrary joint correlation. Probabilities are exact Fractions.
"""

from fractions import Fraction
from reproduce import MASK_SUCCESS_COUNTS, SINGLETON_SIGNATURE_COUNTS
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from secret_box_coalition_synergy import (
    expected_successes,
    synergy_counts,
)

D = synergy_counts(MASK_SUCCESS_COUNTS, SINGLETON_SIGNATURE_COUNTS)


def upper_joint_distribution(q: Fraction) -> dict[int, Fraction]:
    """Attain E[D] = 1917 * min(q, 1-q) with uniform marginals."""
    if not 0 <= q <= 1:
        raise ValueError("q outside [0,1]")
    if q <= Fraction(1, 3):
        return {0: 1 - 3 * q, 1: q, 4: q, 10: q}
    if q <= Fraction(1, 2):
        return {1: 1 - 2 * q, 4: 1 - 2 * q, 5: 3 * q - 1, 10: q}
    return {5: 1 - q, 10: 1 - q, 15: 2 * q - 1}


def lower_joint_distribution(q: Fraction) -> dict[int, Fraction]:
    """All-or-none common availability gives zero coalition synergy."""
    if not 0 <= q <= 1:
        raise ValueError("q outside [0,1]")
    return {0: 1 - q, 15: q}


def validate_distribution(
    distribution: dict[int, Fraction],
    q: Fraction,
) -> Fraction:
    assert all(0 <= m < 16 for m in distribution)
    assert all(weight >= 0 for weight in distribution.values())
    assert sum(distribution.values(), Fraction(0)) == 1
    for bit in (1, 2, 4, 8):
        assert sum(
            (weight for mask, weight in distribution.items() if mask & bit),
            Fraction(0),
        ) == q
    return sum(
        (D[mask] * weight for mask, weight in distribution.items()),
        Fraction(0),
    )


def main() -> None:
    assert len(D) == 16
    assert D == (
        0, 0, 0, 0,
        0, 0, 42, 0,
        0, 0, 1_917, 0,
        42, 0, 42, 0,
    )

    # Two pointwise affine certificates upper-bound E[D] at any joint law:
    # D(mask) <= 42*1[Tool] + 1875*1[Stadium] <= expected 1917*q
    # D(mask) <= 1917*1[Item absent] <= expected 1917*(1-q).
    for mask, value in enumerate(D):
        assert value <= 42 * bool(mask & 2) + 1_875 * bool(mask & 8)
        assert value <= 1_917 * (not bool(mask & 1))

    samples = (
        Fraction(0), Fraction(1, 12), Fraction(1, 4),
        Fraction(1, 3), Fraction(2, 5), Fraction(1, 2),
        Fraction(3, 5), Fraction(2, 3), Fraction(3, 4),
        Fraction(11, 12), Fraction(1),
    )
    for q in samples:
        low = validate_distribution(lower_joint_distribution(q), q)
        high = validate_distribution(upper_joint_distribution(q), q)
        assert low == 0
        assert high == 1_917 * min(q, 1 - q)

    independent = expected_successes(D, (Fraction(1, 2),) * 4)
    assert independent == Fraction(2_043, 16)
    high = validate_distribution(
        upper_joint_distribution(Fraction(1, 2)),
        Fraction(1, 2),
    )
    assert high == Fraction(1_917, 2)
    assert high / independent == Fraction(1_704, 227)
    print("Sharp dependence-independent lower: 0")
    print("Sharp upper: 1917 * min(q, 1-q)")
    print("At q=1/2, independent extra expected states:", independent)
    print("At q=1/2, possible maximum extra expected states:", high)
    print("At q=1/2, upper/independent ratio:", high / independent)
    print("At q=1/2, conditional maximum pp:", float(high * 100 / 20_785))
    print("All sharp-correlation bound proofs and witnesses passed.")


if __name__ == "__main__":
    main()
