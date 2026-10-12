"""Exact three ordered hidden card-group positions without replacement.

The positions are abstract top-of-deck, acquired tagged card, and another
hand card. Their distribution is unconditional on the rest of the game.
"""

from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from itertools import product

from prize_unknown_hand_composition import LatentHandCompositionBelief


def exact_three_position_group_masses(
    group_counts: Mapping[str, int],
) -> dict[tuple[str, str, str], Fraction]:
    """Compute the joint group distribution for three distinct shuffled copies."""
    if not group_counts or any(
        not isinstance(n, int) or n < 0 for n in group_counts.values()
    ):
        raise ValueError("group counts must be nonnegative integers")
    total = sum(group_counts.values())
    if total < 3:
        raise ValueError("at least three physical cards are required")
    groups = tuple(group_counts)
    masses = {}
    for triple in product(groups, repeat=3):
        remaining = dict(group_counts)
        probability = Fraction(1)
        for group in triple:
            available = remaining[group]
            if not available:
                probability = Fraction(0)
                break
            probability *= Fraction(available, sum(remaining.values()))
            remaining[group] -= 1
        if probability:
            masses[triple] = probability
    assert sum(masses.values()) == 1
    return masses


def exact_three_position_hand_belief(
    group_counts: Mapping[str, int],
) -> LatentHandCompositionBelief:
    """Produce compatible (top, empty remaining Prizes, tag, other) beliefs."""
    groups = tuple(group_counts)
    masses = exact_three_position_group_masses(group_counts)
    return LatentHandCompositionBelief(
        groups,
        (),
        tuple(
            (
                (
                    top, (), tag,
                    tuple(int(group == other) for group in groups),
                ),
                float(probability),
            )
            for (top, tag, other), probability in sorted(masses.items())
        ),
    )
