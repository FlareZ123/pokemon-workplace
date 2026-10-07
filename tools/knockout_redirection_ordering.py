"""Resolve already-ordered Knock Out destination programs per physical instance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ResolvedDestination:
    instance_id: str
    destination_zone: str
    effect_id: str

    def __post_init__(self) -> None:
        if not self.instance_id:
            raise ValueError("instance_id must be non-empty")
        if not self.destination_zone:
            raise ValueError("destination_zone must be non-empty")
        if not self.effect_id:
            raise ValueError("effect_id must be non-empty")


def resolve_ordered_programs(
    programs: Mapping[str, Mapping[str, str]],
    ordered_effect_ids: Sequence[str],
) -> tuple[ResolvedDestination, ...] | None:
    """Resolve destination-only KO effects in a caller-supplied order.

    The caller owns trigger eligibility and ordering authority. This layer only
    models the physical consequence once that order is known.

    For each physical instance, the earliest effect that explicitly assigns a
    destination determines its resolved zone. A later effect cannot redirect
    an instance that the earlier effect has already moved out of the pending KO
    relation.
    """

    program_ids = tuple(programs)
    requested = tuple(ordered_effect_ids)
    if len(requested) != len(set(requested)):
        return None
    if len(requested) != len(program_ids) or set(requested) != set(program_ids):
        return None

    resolved: dict[str, ResolvedDestination] = {}
    for effect_id in requested:
        assignments = programs[effect_id]
        for instance_id, destination_zone in assignments.items():
            if not instance_id or not destination_zone:
                raise ValueError("destination programs require non-empty values")
            if instance_id in resolved:
                continue
            resolved[instance_id] = ResolvedDestination(
                instance_id,
                destination_zone,
                effect_id,
            )

    return tuple(
        resolved[instance_id]
        for instance_id in sorted(resolved)
    )


def resolved_route_map(
    resolutions: Sequence[ResolvedDestination],
) -> dict[str, str]:
    """Convert resolved provenance rows to the existing KO router input."""

    instance_ids = tuple(row.instance_id for row in resolutions)
    if len(instance_ids) != len(set(instance_ids)):
        raise ValueError("resolved instance IDs must be unique")
    return {
        row.instance_id: row.destination_zone
        for row in resolutions
    }
