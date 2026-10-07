"""Exact recovery probabilities for rulebook-backed Special Condition coin tests."""

from __future__ import annotations

from fractions import Fraction
from math import inf


def all_heads_probability(
    coin_count: int,
    *,
    heads_probability: Fraction = Fraction(1, 2),
) -> Fraction:
    if coin_count < 1:
        raise ValueError("coin_count must be positive")
    if not Fraction(0) <= heads_probability <= Fraction(1):
        raise ValueError("heads_probability must be between 0 and 1")
    return heads_probability ** coin_count


def asleep_recovery_probability(
    *,
    coin_count: int = 1,
    heads_probability: Fraction = Fraction(1, 2),
) -> Fraction:
    """Recovery probability when waking requires every flipped coin to be heads."""

    return all_heads_probability(
        coin_count,
        heads_probability=heads_probability,
    )


def burn_recovery_probability(
    *,
    heads_probability: Fraction = Fraction(1, 2),
    recovery_suppressed: bool = False,
) -> Fraction:
    if not Fraction(0) <= heads_probability <= Fraction(1):
        raise ValueError("heads_probability must be between 0 and 1")
    if recovery_suppressed:
        return Fraction(0)
    return heads_probability


def expected_checks_to_coin_recovery(probability: Fraction) -> Fraction | float:
    """Mean geometric waiting time for an unchanged per-Checkup recovery chance."""

    if not Fraction(0) <= probability <= Fraction(1):
        raise ValueError("probability must be between 0 and 1")
    if probability == 0:
        return inf
    return Fraction(1, 1) / probability
