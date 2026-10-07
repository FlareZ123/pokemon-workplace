"""Exact connector allocation with ordered, replenishable shared resources.

A profile pays its resource cost from the pre-action state, then adds its
resource production. Physical connector copies are finite, so exhaustive
state search is bounded. Resource dimensions are abstract and can represent
discardable-card stock or another replenishable integer capacity.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Sequence


@dataclass(frozen=True)
class TemporalActionProfile:
    """One action choice with target output and resource delta."""

    output: tuple[int, ...]
    cost: tuple[int, ...]
    production: tuple[int, ...]


@dataclass(frozen=True)
class TemporalConnectorType:
    """Exchangeable copies of a connector with state-valid profiles."""

    name: str
    copies: int
    profiles: tuple[TemporalActionProfile, ...]


@dataclass(frozen=True)
class TemporalConnectorResult:
    """Exact feasibility and one action-order witness when feasible."""

    feasible: bool
    minimum_unmet_units: int
    witness_actions: tuple[tuple[str, TemporalActionProfile], ...] | None
    ending_resources: tuple[int, ...] | None


def _validate(
    demand: tuple[int, ...],
    resources: tuple[int, ...],
    connectors: tuple[TemporalConnectorType, ...],
) -> None:
    if not demand:
        raise ValueError("demand must contain at least one target channel")
    if min(demand) < 0:
        raise ValueError("demand values must be non-negative")
    if min(resources, default=0) < 0:
        raise ValueError("resource values must be non-negative")

    for connector in connectors:
        if connector.copies < 0:
            raise ValueError("connector copies must be non-negative")
        if not connector.profiles:
            raise ValueError("connector profiles cannot be empty")
        for profile in connector.profiles:
            if len(profile.output) != len(demand):
                raise ValueError("output length must match demand length")
            if len(profile.cost) != len(resources):
                raise ValueError("cost length must match resource length")
            if len(profile.production) != len(resources):
                raise ValueError("production length must match resource length")
            if min(profile.output) < 0:
                raise ValueError("output values must be non-negative")
            if min(profile.cost, default=0) < 0:
                raise ValueError("cost values must be non-negative")
            if min(profile.production, default=0) < 0:
                raise ValueError("production values must be non-negative")
            if (
                not any(profile.output)
                and not any(profile.cost)
                and not any(profile.production)
            ):
                raise ValueError("profile must change target or resource state")


def evaluate_temporal_resource_connectors(
    demand: Sequence[int],
    starting_resources: Sequence[int],
    connectors: Sequence[TemporalConnectorType],
) -> TemporalConnectorResult:
    """Search connector order while actions consume and produce resources.

    An action is legal only when all of its costs fit the resource state before
    that action. Its production becomes available only after the cost is paid.
    Each connector copy can be used at most once.
    """

    demand0 = tuple(demand)
    resources0 = tuple(starting_resources)
    connector_types = tuple(connectors)
    _validate(demand0, resources0, connector_types)
    counts0 = tuple(connector.copies for connector in connector_types)

    @lru_cache(maxsize=None)
    def search(
        counts: tuple[int, ...],
        current_demand: tuple[int, ...],
        resources: tuple[int, ...],
    ) -> tuple[
        int,
        tuple[tuple[str, TemporalActionProfile], ...],
        tuple[int, ...],
    ]:
        if not any(current_demand):
            return 0, (), resources

        best_unmet = sum(current_demand)
        best_witness: tuple[tuple[str, TemporalActionProfile], ...] = ()
        best_resources = resources

        for index, connector in enumerate(connector_types):
            if counts[index] == 0:
                continue

            for profile in connector.profiles:
                if any(
                    required > available
                    for required, available in zip(profile.cost, resources)
                ):
                    continue

                next_counts = list(counts)
                next_counts[index] -= 1
                next_demand = tuple(
                    max(0, needed - supplied)
                    for needed, supplied in zip(current_demand, profile.output)
                )
                next_resources = tuple(
                    available - required + produced
                    for available, required, produced in zip(
                        resources, profile.cost, profile.production
                    )
                )

                unmet, suffix, ending_resources = search(
                    tuple(next_counts),
                    next_demand,
                    next_resources,
                )
                if unmet < best_unmet:
                    best_unmet = unmet
                    best_witness = ((connector.name, profile),) + suffix
                    best_resources = ending_resources
                    if unmet == 0:
                        return 0, best_witness, best_resources

        return best_unmet, best_witness, best_resources

    unmet, witness, ending_resources = search(counts0, demand0, resources0)
    return TemporalConnectorResult(
        feasible=unmet == 0,
        minimum_unmet_units=unmet,
        witness_actions=witness if unmet == 0 else None,
        ending_resources=ending_resources if unmet == 0 else None,
    )
