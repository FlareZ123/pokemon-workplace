"""Detect incompatible per-instance destinations from simultaneous KO effects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class DestinationAssignment:
    effect_id: str
    instance_id: str
    destination_zone: str

    def __post_init__(self) -> None:
        if not self.effect_id:
            raise ValueError("effect_id must be non-empty")
        if not self.instance_id:
            raise ValueError("instance_id must be non-empty")
        if not self.destination_zone:
            raise ValueError("destination_zone must be non-empty")


@dataclass(frozen=True)
class DestinationConflict:
    instance_id: str
    assignments: tuple[DestinationAssignment, ...]

    def __post_init__(self) -> None:
        if not self.instance_id:
            raise ValueError("instance_id must be non-empty")
        if len({row.destination_zone for row in self.assignments}) < 2:
            raise ValueError("conflict requires at least two distinct destinations")


def destination_conflicts(
    programs: Mapping[str, Mapping[str, str]],
) -> tuple[DestinationConflict, ...]:
    """Return same-instance assignments that disagree on destination zone."""

    by_instance: dict[str, list[DestinationAssignment]] = {}
    for effect_id, assignments in programs.items():
        if not effect_id:
            raise ValueError("effect_id must be non-empty")
        for instance_id, destination_zone in assignments.items():
            row = DestinationAssignment(
                effect_id,
                instance_id,
                destination_zone,
            )
            by_instance.setdefault(instance_id, []).append(row)

    conflicts = []
    for instance_id, rows in sorted(by_instance.items()):
        zones = {row.destination_zone for row in rows}
        if len(zones) < 2:
            continue
        conflicts.append(
            DestinationConflict(
                instance_id,
                tuple(sorted(rows, key=lambda row: row.effect_id)),
            )
        )
    return tuple(conflicts)


def merge_compatible_programs(
    programs: Mapping[str, Mapping[str, str]],
) -> dict[str, str] | None:
    """Merge effect assignments only when every shared instance agrees."""

    if destination_conflicts(programs):
        return None

    merged: dict[str, str] = {}
    for assignments in programs.values():
        merged.update(assignments)
    return merged
