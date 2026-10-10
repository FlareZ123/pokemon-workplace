"""Subset-output resilience and singleton-route coverage diagnostics.

The bitmask table aggregates binary successes on identical sampled states.
Singleton signatures record which one-bit masks succeed in those states.
"""

from fractions import Fraction
from math import comb, prod
from typing import Sequence


def singleton_or_counts(
    signature_counts: Sequence[int],
) -> tuple[int, ...]:
    """Count states covered by at least one enabled singleton route."""
    size = len(signature_counts)
    if size < 2 or size & (size - 1):
        raise ValueError("signature table must have power-of-two length >= 2")
    if any(count < 0 for count in signature_counts):
        raise ValueError("negative signature count")
    return tuple(
        sum(
            count for signature, count in enumerate(signature_counts)
            if signature & mask
        )
        for mask in range(size)
    )


def uniform_availability_coefficients(
    mask_success_counts: Sequence[int],
) -> tuple[int, ...]:
    """Expand expected count at independent common category availability q.

    The returned coefficients are ordered from q^0 to q^n.
    """
    size = len(mask_success_counts)
    if size < 2 or size & (size - 1):
        raise ValueError("mask table must have power-of-two length >= 2")
    if any(count < 0 for count in mask_success_counts):
        raise ValueError("negative success count")
    n = size.bit_length() - 1
    coefficients = [0] * (n + 1)
    for mask, value in enumerate(mask_success_counts):
        k = mask.bit_count()
        for degree in range(k, n + 1):
            coefficients[degree] += (
                value * comb(n - k, degree - k) * (-1) ** (degree - k)
            )
    return tuple(coefficients)


def expected_successes(
    mask_success_counts: Sequence[int],
    availability: Sequence[Fraction],
) -> Fraction:
    """Expected successes for independent availability per category."""
    size = len(mask_success_counts)
    n = size.bit_length() - 1
    if size < 2 or size != 1 << n or len(availability) != n:
        raise ValueError("mask table and category probability sizes differ")
    ps = tuple(Fraction(p) for p in availability)
    if any(p < 0 or p > 1 for p in ps):
        raise ValueError("availability probability outside [0,1]")
    return sum(
        (
            Fraction(value)
            * prod(
                ps[i] if mask & (1 << i) else (1 - ps[i])
                for i in range(n)
            )
            for mask, value in enumerate(mask_success_counts)
        ),
        Fraction(0),
    )


def synergy_counts(
    mask_success_counts: Sequence[int],
    signature_counts: Sequence[int],
) -> tuple[int, ...]:
    """Return the gain beyond the union of successful singleton routes."""
    if len(mask_success_counts) != len(signature_counts):
        raise ValueError("table lengths differ")
    baseline = singleton_or_counts(signature_counts)
    if sum(signature_counts) != mask_success_counts[-1]:
        raise ValueError("tables describe different successful state counts")
    surplus = tuple(
        actual - predicted
        for actual, predicted in zip(mask_success_counts, baseline)
    )
    if any(value < 0 for value in surplus):
        raise ValueError("single-category coverage exceeds full outcome")
    return surplus
