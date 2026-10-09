"""Exact posterior bounds for uncertain optional Prize-trigger decisions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from itertools import product
from typing import Literal

from pending_prize_identity_belief import PendingPrizeJointBelief
from prize_position_belief import PrizeGroup


@dataclass(frozen=True)
class DeclinePosteriorBounds:
    lower: float
    upper: float
    lower_policy: tuple[tuple[PrizeGroup, float], ...]
    upper_policy: tuple[tuple[PrizeGroup, float], ...]


def bound_decline_posterior(
    belief: PendingPrizeJointBelief,
    *,
    use_probability_intervals: Mapping[PrizeGroup, tuple[float, float]],
    target_location: Literal["top", "pending"],
    target_group: PrizeGroup,
) -> DeclinePosteriorBounds:
    """Optimize P(target | decline) over independent activation-rate intervals."""

    if target_location not in {"top", "pending"}:
        raise ValueError("target_location must be top or pending")
    groups = sorted({
        world[2] for world, mass in belief.masses if mass > 0.0
    }, key=repr)
    if not set(groups) <= set(use_probability_intervals):
        raise ValueError("intervals must cover all supported pending groups")
    if any(
        not 0.0 <= low <= high <= 1.0
        for low, high in use_probability_intervals.values()
    ):
        raise ValueError("invalid activation probability interval")

    lo, hi = float("inf"), float("-inf")
    lo_policy = hi_policy = ()
    for endpoints in product(*(use_probability_intervals[g] for g in groups)):
        policy = dict(zip(groups, endpoints, strict=True))
        numerator = denominator = 0.0
        for world, mass in belief.masses:
            weight = mass * (1.0 - policy[world[2]])
            denominator += weight
            selected = world[0] if target_location == "top" else world[2]
            if selected == target_group:
                numerator += weight
        if denominator <= 0.0:
            continue
        posterior = numerator / denominator
        witness = tuple(zip(groups, endpoints, strict=True))
        if posterior < lo:
            lo, lo_policy = posterior, witness
        if posterior > hi:
            hi, hi_policy = posterior, witness

    if lo == float("inf"):
        raise ValueError("decline impossible under every admissible policy")
    return DeclinePosteriorBounds(lo, hi, lo_policy, hi_policy)
