"""Exact correlated-Prize Retreat payment count under low/high provider regimes.

All Energy classes share one behind-on-Prizes state. Independent uncertainty
per physical Counter/Reversal card would overcount impossible worlds.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import comb


@dataclass(frozen=True)
class CorrelatedPrizeEnergyGroup:
    key: str
    copies: int
    units_tied: int
    units_behind: int

    def __post_init__(self) -> None:
        if not self.key or self.copies < 0:
            raise ValueError("Invalid group identity or copy count")
        if not (1 <= self.units_tied <= self.units_behind):
            raise ValueError("Provider units must have positive monotone bounds")


@dataclass(frozen=True)
class CorrelatedPrizeRetreatCounts:
    robust_legal: int
    possible_legal: int
    robust_minimal: int
    worldwise_minimal_intersection: int
    dp_state_count: int

    @property
    def behind_only(self) -> int:
        return self.possible_legal - self.robust_legal

    @property
    def minimal_actions_lost_if_intersected_early(self) -> int:
        return self.robust_minimal - self.worldwise_minimal_intersection


def count_correlated_prize_payments(
    groups: tuple[CorrelatedPrizeEnergyGroup, ...],
    retreat_cost: int,
) -> CorrelatedPrizeRetreatCounts:
    """Count complete and minimal physical payment sets in both Prize worlds."""
    if retreat_cost < 0:
        raise ValueError("Retreat Cost cannot be negative")
    if len({g.key for g in groups}) != len(groups):
        raise ValueError("Group keys must be unique")
    if retreat_cost == 0:
        return CorrelatedPrizeRetreatCounts(1, 1, 1, 1, 1)

    # Tuple: selected copies, tied units, behind units, min tied, min behind.
    states: dict[tuple[int, int, int, int, int], int] = {
        (0, 0, 0, 0, 0): 1
    }
    peak = 1
    for group in groups:
        next_states: dict[tuple[int, int, int, int, int], int] = defaultdict(int)
        for (n, lo, hi, min_lo, min_hi), count in states.items():
            for k in range(min(group.copies, retreat_cost - n) + 1):
                if k:
                    new_min_lo = min(min_lo, group.units_tied) if min_lo else group.units_tied
                    new_min_hi = min(min_hi, group.units_behind) if min_hi else group.units_behind
                else:
                    new_min_lo, new_min_hi = min_lo, min_hi
                key = (
                    n + k, lo + k * group.units_tied,
                    hi + k * group.units_behind, new_min_lo, new_min_hi,
                )
                next_states[key] += count * comb(group.copies, k)
        states = dict(next_states)
        peak = max(peak, len(states))

    robust = possible = robust_min = both_min = 0
    for (n, lo, hi, min_lo, min_hi), count in states.items():
        if n == 0:
            continue
        if hi >= retreat_cost:
            possible += count
        if lo >= retreat_cost:
            robust += count
            if lo - min_lo < retreat_cost:
                robust_min += count
                if hi - min_hi < retreat_cost:
                    both_min += count

    return CorrelatedPrizeRetreatCounts(
        robust_legal=robust,
        possible_legal=possible,
        robust_minimal=robust_min,
        worldwise_minimal_intersection=both_min,
        dp_state_count=peak,
    )
