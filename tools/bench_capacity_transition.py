from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class BenchOccupant:
    name: str
    role: str
    retention_value: float

    def __post_init__(self) -> None:
        if self.retention_value < 0:
            raise ValueError("retention_value must be non-negative")


@dataclass(frozen=True)
class CapacityTransition:
    old_capacity: int
    new_capacity: int
    retained: tuple[BenchOccupant, ...]
    discarded: tuple[BenchOccupant, ...]
    retained_value: float
    discarded_value: float


def resolve_capacity_transition(
    occupants: tuple[BenchOccupant, ...],
    *,
    old_capacity: int,
    new_capacity: int,
) -> CapacityTransition:
    """Choose a maximum-retention subset after Bench capacity contracts."""

    if old_capacity < 0 or new_capacity < 0:
        raise ValueError("capacities must be non-negative")
    if len(occupants) > old_capacity:
        raise ValueError("occupancy already exceeds old_capacity")

    keep_count = min(len(occupants), new_capacity)
    if keep_count == len(occupants):
        return CapacityTransition(
            old_capacity=old_capacity,
            new_capacity=new_capacity,
            retained=occupants,
            discarded=(),
            retained_value=sum(row.retention_value for row in occupants),
            discarded_value=0.0,
        )

    best_indices: tuple[int, ...] | None = None
    best_value = -1.0
    for indices in combinations(range(len(occupants)), keep_count):
        value = sum(occupants[index].retention_value for index in indices)
        if value > best_value:
            best_value = value
            best_indices = indices

    assert best_indices is not None
    retained_set = set(best_indices)
    retained = tuple(row for index, row in enumerate(occupants) if index in retained_set)
    discarded = tuple(row for index, row in enumerate(occupants) if index not in retained_set)
    return CapacityTransition(
        old_capacity=old_capacity,
        new_capacity=new_capacity,
        retained=retained,
        discarded=discarded,
        retained_value=sum(row.retention_value for row in retained),
        discarded_value=sum(row.retention_value for row in discarded),
    )


def minimum_role_losses(
    *,
    core_occupants: int,
    support_occupants: int,
    new_capacity: int,
) -> tuple[int, int]:
    """Closed-form losses when every core occupant outranks every support."""

    if min(core_occupants, support_occupants, new_capacity) < 0:
        raise ValueError("counts must be non-negative")
    excess = max(0, core_occupants + support_occupants - new_capacity)
    support_losses = min(support_occupants, excess)
    core_losses = excess - support_losses
    return core_losses, support_losses
