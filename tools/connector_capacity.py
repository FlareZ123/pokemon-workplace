"""Capacity-aware connector feasibility for simultaneous resource channels.

A connector type has one or more outcome profiles. Each profile is a vector of
resource units one physical use can satisfy across the modeled channels.

Examples:
- one any-card search across three channels has profiles (1,0,0), (0,1,0),
  and (0,0,1);
- one multi-axis search can have a profile such as (1,1,1).

The solver is deterministic and state-local. Costs, timing, and whether an
outcome profile is currently legal should be resolved before constructing the
connector types passed here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ConnectorType:
    """Copies of one connector with state-valid outcome profiles."""

    name: str
    copies: int
    profiles: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class ConnectorCapacityResult:
    """Exact state-local feasibility under finite connector capacity."""

    exact_joint_feasible: bool
    naive_joint_reachable: bool
    minimum_unmet_units: int
    reachable_channels: tuple[bool, ...]
    witness_profiles: tuple[tuple[str, tuple[int, ...]], ...] | None


def _validate(
    demand: tuple[int, ...],
    connectors: Sequence[ConnectorType],
) -> None:
    if not demand:
        raise ValueError("demand must contain at least one channel")
    if min(demand) < 0:
        raise ValueError("demand values must be non-negative")

    channel_count = len(demand)
    for connector in connectors:
        if connector.copies < 0:
            raise ValueError("connector copies must be non-negative")
        if not connector.profiles:
            raise ValueError("each connector type must have at least one profile")
        for profile in connector.profiles:
            if len(profile) != channel_count:
                raise ValueError("profile length must match demand length")
            if min(profile) < 0:
                raise ValueError("profile values must be non-negative")
            if not any(profile):
                raise ValueError("profiles must satisfy at least one resource unit")


def evaluate_connector_capacity(
    demand: Sequence[int],
    connectors: Sequence[ConnectorType],
) -> ConnectorCapacityResult:
    """Evaluate exact joint feasibility and naive per-channel reachability.

    Each physical connector copy can be unused or can realize exactly one of its
    listed profiles. The dynamic program tracks remaining demand and retains one
    witness sequence for each reachable remainder state.

    Naive joint reachability deliberately ignores shared capacity. It marks a
    demanded channel reachable whenever at least one available connector profile
    touches that channel, then tests channels independently.
    """

    remaining_demand = tuple(demand)
    connector_types = tuple(connectors)
    _validate(remaining_demand, connector_types)

    channel_count = len(remaining_demand)
    reachable_channels = []
    for channel in range(channel_count):
        if remaining_demand[channel] == 0:
            reachable_channels.append(True)
            continue

        reachable_channels.append(
            any(
                connector.copies > 0
                and any(
                    profile[channel] > 0
                    for profile in connector.profiles
                )
                for connector in connector_types
            )
        )

    naive_joint = all(reachable_channels)

    states: dict[
        tuple[int, ...],
        tuple[tuple[str, tuple[int, ...]], ...],
    ] = {
        remaining_demand: ()
    }

    for connector in connector_types:
        for _ in range(connector.copies):
            next_states = dict(states)
            for remaining, witness in states.items():
                for profile in connector.profiles:
                    next_remaining = tuple(
                        max(0, need - supplied)
                        for need, supplied in zip(
                            remaining,
                            profile,
                        )
                    )
                    next_states.setdefault(
                        next_remaining,
                        witness + ((connector.name, profile),),
                    )
            states = next_states

    zero = (0,) * channel_count
    exact = zero in states
    minimum_unmet = min(
        sum(remaining)
        for remaining in states
    )
    witness = states.get(zero)

    return ConnectorCapacityResult(
        exact_joint_feasible=exact,
        naive_joint_reachable=naive_joint,
        minimum_unmet_units=minimum_unmet,
        reachable_channels=tuple(reachable_channels),
        witness_profiles=witness,
    )
