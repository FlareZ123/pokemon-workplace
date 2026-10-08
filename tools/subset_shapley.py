"""Exact Shapley attribution for finite subset-value tables."""

from __future__ import annotations

from fractions import Fraction
from math import factorial
from numbers import Rational
from typing import Sequence


def shapley_values(
    subset_values: Sequence[Rational],
) -> tuple[Fraction, ...]:
    """Return exact Shapley values for a bitmask-indexed coalition table.

    subset_values[mask] is the value assigned to coalition mask.
    The table length must be a power of two. Player i corresponds to bit
    1 << i.
    """

    size = len(subset_values)
    if size < 2 or size & (size - 1):
        raise ValueError("subset_values length must be a power of two >= 2")

    player_count = size.bit_length() - 1
    values = tuple(Fraction(value) for value in subset_values)
    denominator = factorial(player_count)
    result: list[Fraction] = []

    for player in range(player_count):
        bit = 1 << player
        contribution = Fraction(0)
        for coalition in range(size):
            if coalition & bit:
                continue
            members = coalition.bit_count()
            weight = Fraction(
                factorial(members)
                * factorial(player_count - members - 1),
                denominator,
            )
            contribution += weight * (
                values[coalition | bit] - values[coalition]
            )
        result.append(contribution)

    return tuple(result)
