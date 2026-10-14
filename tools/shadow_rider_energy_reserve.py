"""Exact Aichi Shadow Rider Treasure payment with Psychic Energy retention.

The earlier conditional dual-VMAX Treasure route has broad other-card counts.
Within those counts, physically allocated Basic Psychic Energy cards are
exchangeable, so the number in the observed hand is hypergeometric.
"""

from __future__ import annotations

from fractions import Fraction
from math import comb

from shadow_rider_treasure_cost_sensitivity import (
    treasure_two_vmax_hand_buckets,
)


def energy_tail(
    held_filler: int,
    *,
    total_filler: int,
    psychic_energy: int,
    at_least: int,
) -> Fraction:
    """Conditional probability at least k of held filler are Psychic Energy."""

    if not (0 <= psychic_energy <= total_filler):
        raise ValueError("Psychic count outside filler population")
    if not (0 <= held_filler <= total_filler):
        raise ValueError("held filler count outside population")
    if at_least < 0:
        raise ValueError("retained threshold cannot be negative")

    return sum(
        (
            Fraction(
                comb(psychic_energy, count)
                * comb(total_filler - psychic_energy, held_filler - count),
                comb(total_filler, held_filler),
            )
            for count in range(at_least, min(held_filler, psychic_energy) + 1)
            if 0 <= held_filler - count <= total_filler - psychic_energy
        ),
        Fraction(),
    )


def retained_energy_treasure_route(
    *,
    retain_after_payment: int,
    allow_spare_treasure_payment: bool = False,
    psychic_energy: int = 11,
    total_filler: int = 37,
    buckets: dict[tuple[int, int], Fraction] | None = None,
) -> Fraction:
    """Probability of two-VMAX Treasure line with retained Psychic in hand.

    This models the named Treasure -> Radiant Eternatus -> Climactic Gate
    route and an explicit discard policy. A spare second Treasure may pay
    the cost instead of Psychic Energy. Under that policy, all held Psychic
    Energy remains available for a later Underworld Door activation.

    Other possible discard classes, extra drawing, board/Bench dynamics,
    and actual following-turn play are excluded.
    """

    if retain_after_payment < 0:
        raise ValueError("retain_after_payment must be non-negative")
    if not 0 <= psychic_energy <= total_filler:
        raise ValueError("invalid Psychic Energy count")

    route_buckets = (
        treasure_two_vmax_hand_buckets() if buckets is None else buckets
    )
    total = Fraction()
    for (held_filler, held_treasures), route_mass in route_buckets.items():
        # Spending Psychic from hand leaves one less Psychic for next turn.
        # When at least two Treasures are already held, the extra Treasure
        # can instead pay the first Treasure's one-other-card cost.
        required_before_payment = (
            retain_after_payment
            if allow_spare_treasure_payment and held_treasures >= 2
            else retain_after_payment + 1
        )
        total += route_mass * energy_tail(
            held_filler,
            total_filler=total_filler,
            psychic_energy=psychic_energy,
            at_least=required_before_payment,
        )
    return total


def retained_energy_frontier(
    max_retained: int = 3,
) -> tuple[tuple[int, Fraction, Fraction], ...]:
    """Produce strict-Energy and Energy-or-spare-Treasure retention rates."""

    if max_retained < 0:
        raise ValueError("max_retained must be non-negative")
    buckets = treasure_two_vmax_hand_buckets()
    return tuple(
        (
            retained,
            retained_energy_treasure_route(
                retain_after_payment=retained,
                buckets=buckets,
            ),
            retained_energy_treasure_route(
                retain_after_payment=retained,
                allow_spare_treasure_payment=True,
                buckets=buckets,
            ),
        )
        for retained in range(max_retained + 1)
    )
