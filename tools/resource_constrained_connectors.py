"""Exact deterministic connector allocation with shared resource capacities.

This module generalizes connector output profiles by adding explicit resource
costs. A physical connector copy can be unused or can realize one action profile.
Each action profile supplies target units and consumes shared state resources.

Examples of modeled resources can include disposable cards, remaining Supporter
plays, or Bench slack. Temporal ordering and changing capacities still belong in
a richer state-transition engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ResourceActionProfile:
    """One state-valid output and cost choice for a physical connector use."""

    output: tuple[int, ...]
    cost: tuple[int, ...]


@dataclass(frozen=True)
class ResourceConnectorType:
    """Copies of one connector with state-valid action profiles."""

    name: str
    copies: int
    profiles: tuple[ResourceActionProfile, ...]


@dataclass(frozen=True)
class ResourceConnectorResult:
    """Exact feasibility plus two progressively stronger naive comparisons."""

    exact_joint_feasible: bool
    raw_naive_joint_reachable: bool
    individually_cost_feasible_joint: bool
    minimum_unmet_units: int
    witness_actions: tuple[
        tuple[str, ResourceActionProfile],
        ...,
    ] | None


def _validate(
    demand: tuple[int, ...],
    resource_capacities: tuple[int, ...],
    connectors: Sequence[ResourceConnectorType],
) -> None:
    if not demand:
        raise ValueError("demand must contain at least one target channel")
    if min(demand) < 0:
        raise ValueError("demand values must be non-negative")
    if min(resource_capacities, default=0) < 0:
        raise ValueError("resource capacities must be non-negative")

    target_count = len(demand)
    resource_count = len(resource_capacities)
    for connector in connectors:
        if connector.copies < 0:
            raise ValueError("connector copies must be non-negative")
        if not connector.profiles:
            raise ValueError("connector profiles cannot be empty")
        for profile in connector.profiles:
            if len(profile.output) != target_count:
                raise ValueError("output length must match demand length")
            if len(profile.cost) != resource_count:
                raise ValueError(
                    "cost length must match resource capacity length"
                )
            if min(profile.output) < 0:
                raise ValueError("output values must be non-negative")
            if min(profile.cost, default=0) < 0:
                raise ValueError("cost values must be non-negative")
            if not any(profile.output):
                raise ValueError("each profile must supply a target unit")


def _cost_fits(
    cost: tuple[int, ...],
    resources: tuple[int, ...],
) -> bool:
    return all(
        required <= available
        for required, available in zip(cost, resources)
    )


def evaluate_resource_constrained_connectors(
    demand: Sequence[int],
    resource_capacities: Sequence[int],
    connectors: Sequence[ResourceConnectorType],
) -> ResourceConnectorResult:
    """Return exact joint feasibility under connector and resource capacities.

    raw_naive_joint_reachable asks whether every demanded target has at least one
    edge from an available connector profile and ignores profile costs.

    individually_cost_feasible_joint requires every demanded target to have at
    least one profile whose cost fits the full starting resource pool. It still
    tests targets independently, so the same connector copy and the same resource
    units may be reused across several target checks.

    exact_joint_feasible allocates physical connector copies and shared resources
    jointly through dynamic programming.
    """

    remaining_demand = tuple(demand)
    starting_resources = tuple(resource_capacities)
    connector_types = tuple(connectors)
    _validate(
        remaining_demand,
        starting_resources,
        connector_types,
    )

    raw_channels: list[bool] = []
    cost_channels: list[bool] = []
    for target_index, needed in enumerate(remaining_demand):
        if needed == 0:
            raw_channels.append(True)
            cost_channels.append(True)
            continue

        candidate_profiles = [
            profile
            for connector in connector_types
            if connector.copies > 0
            for profile in connector.profiles
            if profile.output[target_index] > 0
        ]
        raw_channels.append(bool(candidate_profiles))
        cost_channels.append(
            any(
                _cost_fits(
                    profile.cost,
                    starting_resources,
                )
                for profile in candidate_profiles
            )
        )

    raw_naive = all(raw_channels)
    individually_cost_feasible = all(cost_channels)

    state_type = tuple[
        tuple[int, ...],
        tuple[int, ...],
    ]
    states: dict[
        state_type,
        tuple[tuple[str, ResourceActionProfile], ...],
    ] = {
        (
            remaining_demand,
            starting_resources,
        ): ()
    }

    for connector in connector_types:
        for _ in range(connector.copies):
            next_states = dict(states)
            for (
                current_demand,
                current_resources,
            ), witness in states.items():
                for profile in connector.profiles:
                    if not _cost_fits(
                        profile.cost,
                        current_resources,
                    ):
                        continue

                    next_demand = tuple(
                        max(0, need - supplied)
                        for need, supplied in zip(
                            current_demand,
                            profile.output,
                        )
                    )
                    next_resources = tuple(
                        available - required
                        for available, required in zip(
                            current_resources,
                            profile.cost,
                        )
                    )
                    next_states.setdefault(
                        (
                            next_demand,
                            next_resources,
                        ),
                        witness + ((connector.name, profile),),
                    )
            states = next_states

    zero_demand = (0,) * len(remaining_demand)
    feasible_states = [
        (state, witness)
        for state, witness in states.items()
        if state[0] == zero_demand
    ]
    exact = bool(feasible_states)
    minimum_unmet = min(
        sum(state[0])
        for state in states
    )
    witness_actions = (
        feasible_states[0][1]
        if feasible_states
        else None
    )

    return ResourceConnectorResult(
        exact_joint_feasible=exact,
        raw_naive_joint_reachable=raw_naive,
        individually_cost_feasible_joint=individually_cost_feasible,
        minimum_unmet_units=minimum_unmet,
        witness_actions=witness_actions,
    )
