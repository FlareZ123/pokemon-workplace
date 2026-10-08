"""Effective-output-capacity phase scan for multi-channel connectors.

This module studies when one more currently disposable card has greater local
joint-access value than one more direct out as the effective output capacity
of a multi-axis connector changes.

The intended Secret Box slice uses discard cost 3. Effective capacity may be
below the card's printed four output categories when only some missing target
channels map to distinct eligible categories.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence

from multi_channel_connector import multi_channel_connector_access


@dataclass(frozen=True)
class CapacityPhasePoint:
    """One fixed-size marginal comparison at a disposable-card count."""

    disposable_nonstarters: int
    baseline_joint_access: float
    add_direct_gain: float
    add_disposable_gain: float

    @property
    def disposable_to_direct_ratio(self) -> float:
        if self.add_direct_gain == 0.0:
            return float("inf")
        return self.add_disposable_gain / self.add_direct_gain


@dataclass(frozen=True)
class CapacityPhase:
    """One effective connector-capacity slice."""

    channel_count: int
    connector_capacity: int
    discard_cost: int
    target_copies_per_channel: int
    max_disposable: int
    minimum_payable_success_slots: int
    points: tuple[CapacityPhasePoint, ...]
    disposable_dominant_intervals: tuple[tuple[int, int], ...]
    peak_ratio_point: CapacityPhasePoint


def minimum_payable_success_slots(
    channel_count: int,
    connector_capacity: int,
    discard_cost: int,
) -> int:
    """Return the lower-bound hand slots for a paid connector success."""

    if channel_count <= 0:
        raise ValueError("channel_count must be positive")
    if connector_capacity <= 0:
        raise ValueError("connector_capacity must be positive")
    if discard_cost < 0:
        raise ValueError("discard_cost must be non-negative")

    unsatisfied_by_connector = max(0, channel_count - connector_capacity)
    return 1 + 1 + discard_cost + unsatisfied_by_connector


def _dominant_intervals(
    points: Sequence[CapacityPhasePoint],
    *,
    tolerance: float,
) -> tuple[tuple[int, int], ...]:
    intervals: list[tuple[int, int]] = []
    start: int | None = None

    for index, point in enumerate(points):
        dominant = (
            point.add_disposable_gain
            > point.add_direct_gain + tolerance
        )
        if dominant and start is None:
            start = point.disposable_nonstarters

        is_last = index == len(points) - 1
        if start is not None and (not dominant or is_last):
            if dominant and is_last:
                end = point.disposable_nonstarters
            else:
                end = points[index - 1].disposable_nonstarters
            intervals.append((start, end))
            start = None

    return tuple(intervals)


def scan_symmetric_capacity_phase(
    channel_count: int,
    connector_capacity: int,
    *,
    target_copies_per_channel: int = 2,
    discard_cost: int = 3,
    deck_size: int = 60,
    prize_count: int = 6,
    starter_cards: int = 12,
    opening_hand_size: int = 7,
    tolerance: float = 1e-15,
) -> CapacityPhase:
    """Scan every fixed-size disposable count with one filler slot left."""

    if target_copies_per_channel <= 0:
        raise ValueError("target_copies_per_channel must be positive")
    if connector_capacity > channel_count:
        raise ValueError("connector_capacity cannot exceed channel_count")

    targets = (target_copies_per_channel,) * channel_count
    max_disposable = (
        deck_size - starter_cards - sum(targets) - 2
    )
    if max_disposable < 0:
        raise ValueError("composition leaves no protected filler slot")

    @lru_cache(maxsize=None)
    def joint_access(
        target_counts: tuple[int, ...],
        disposable: int,
    ) -> float:
        return multi_channel_connector_access(
            deck_size,
            prize_count,
            starter_cards=starter_cards,
            target_counts=target_counts,
            disposable_nonstarters=disposable,
            discard_cost=discard_cost,
            connector_capacity=connector_capacity,
            opening_hand_size=opening_hand_size,
        ).joint_access

    changed_targets = (
        (target_copies_per_channel + 1,)
        + targets[1:]
    )

    points: list[CapacityPhasePoint] = []
    for disposable in range(max_disposable + 1):
        baseline = joint_access(targets, disposable)
        direct = joint_access(changed_targets, disposable)
        disposable_access = joint_access(targets, disposable + 1)
        points.append(
            CapacityPhasePoint(
                disposable_nonstarters=disposable,
                baseline_joint_access=baseline,
                add_direct_gain=direct - baseline,
                add_disposable_gain=disposable_access - baseline,
            )
        )

    point_tuple = tuple(points)
    peak = max(
        point_tuple,
        key=lambda point: point.disposable_to_direct_ratio,
    )
    return CapacityPhase(
        channel_count=channel_count,
        connector_capacity=connector_capacity,
        discard_cost=discard_cost,
        target_copies_per_channel=target_copies_per_channel,
        max_disposable=max_disposable,
        minimum_payable_success_slots=minimum_payable_success_slots(
            channel_count,
            connector_capacity,
            discard_cost,
        ),
        points=point_tuple,
        disposable_dominant_intervals=_dominant_intervals(
            point_tuple,
            tolerance=tolerance,
        ),
        peak_ratio_point=peak,
    )
