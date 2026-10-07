"""Scan one-slot direct-out versus discardability marginals exactly."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable

from connector_domination import two_channel_connector_access_collapsed


@dataclass(frozen=True)
class MarginalRegimePoint:
    """One scanned state and its three one-slot realistic marginals."""

    discard_cost: int
    target_a_copies: int
    target_b_copies: int
    disposable_nonstarters: int
    add_target_a_gain: float
    add_target_b_gain: float
    add_disposable_gain: float

    @property
    def weaker_direct_gain(self) -> float:
        return min(self.add_target_a_gain, self.add_target_b_gain)

    @property
    def disposable_to_weaker_direct_ratio(self) -> float:
        if self.weaker_direct_gain == 0.0:
            return float("inf")
        return self.add_disposable_gain / self.weaker_direct_gain


@dataclass(frozen=True)
class MarginalRegimeSummary:
    """Summary of a finite exact parameter scan."""

    states_scanned: int
    violations: tuple[MarginalRegimePoint, ...]
    closest_point: MarginalRegimePoint


def scan_direct_vs_disposable(
    *,
    deck_size: int = 60,
    prize_count: int = 6,
    starter_cards: int = 12,
    opening_hand_size: int = 7,
    target_out_min: int = 1,
    target_out_max: int = 8,
    discard_costs: Iterable[int] = (1, 2, 3, 4),
) -> MarginalRegimeSummary:
    """Scan whether +1 disposable ever beats either +1 direct target out.

    Each state reserves at least one protected non-starter filler card so all
    three one-slot substitutions are fixed-deck-size replacements.
    """

    costs = tuple(discard_costs)
    if target_out_min <= 0 or target_out_max < target_out_min:
        raise ValueError("invalid target-out range")
    if not costs or min(costs) < 0:
        raise ValueError("discard_costs must be non-empty and non-negative")

    @lru_cache(maxsize=None)
    def realistic_access(
        cost: int,
        target_a: int,
        target_b: int,
        disposable: int,
    ) -> float:
        return two_channel_connector_access_collapsed(
            deck_size,
            prize_count,
            starter_cards=starter_cards,
            target_a_copies=target_a,
            target_b_copies=target_b,
            disposable_nonstarters=disposable,
            discard_cost=cost,
            opening_hand_size=opening_hand_size,
        ).capacity_aware_gated_access

    violations: list[MarginalRegimePoint] = []
    closest: MarginalRegimePoint | None = None
    states_scanned = 0

    for cost in costs:
        for target_a in range(target_out_min, target_out_max + 1):
            for target_b in range(target_out_min, target_out_max + 1):
                max_disposable = (
                    deck_size
                    - starter_cards
                    - target_a
                    - target_b
                    - 2
                )
                if max_disposable < 0:
                    continue

                for disposable in range(max_disposable + 1):
                    baseline = realistic_access(
                        cost, target_a, target_b, disposable
                    )
                    point = MarginalRegimePoint(
                        discard_cost=cost,
                        target_a_copies=target_a,
                        target_b_copies=target_b,
                        disposable_nonstarters=disposable,
                        add_target_a_gain=(
                            realistic_access(
                                cost,
                                target_a + 1,
                                target_b,
                                disposable,
                            )
                            - baseline
                        ),
                        add_target_b_gain=(
                            realistic_access(
                                cost,
                                target_a,
                                target_b + 1,
                                disposable,
                            )
                            - baseline
                        ),
                        add_disposable_gain=(
                            realistic_access(
                                cost,
                                target_a,
                                target_b,
                                disposable + 1,
                            )
                            - baseline
                        ),
                    )
                    states_scanned += 1

                    if (
                        point.add_disposable_gain
                        > point.add_target_a_gain + 1e-15
                        or point.add_disposable_gain
                        > point.add_target_b_gain + 1e-15
                    ):
                        violations.append(point)

                    if (
                        closest is None
                        or point.disposable_to_weaker_direct_ratio
                        > closest.disposable_to_weaker_direct_ratio
                    ):
                        closest = point

    if closest is None:
        raise ValueError("scan produced no states")

    return MarginalRegimeSummary(
        states_scanned=states_scanned,
        violations=tuple(violations),
        closest_point=closest,
    )
