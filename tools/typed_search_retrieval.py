"""Enumerate exact typed search retrievals before strategic demand projection.

Search text determines which physical card classes may be retrieved and how many
copies each output axis can take. Strategic demand is a later evaluation layer.
Keeping those layers separate preserves optional side payloads that do not solve
an immediate declared need.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from trainer_search_profile_compiler import SearchOutput
from typed_search_target_allocator import (
    DemandChannel,
    TargetGroup,
    selector_from_label,
)


@dataclass(frozen=True)
class TypedRetrievalAction:
    """One exact physical retrieval choice across search-output axes."""

    target_cost: tuple[int, ...]
    axis_usage: tuple[int, ...]


@dataclass(frozen=True)
class RetrievalDemandProjection:
    """Strategic demand profiles obtainable from one physical retrieval."""

    profiles: tuple[tuple[int, ...], ...]
    full_demand_feasible: bool
    minimum_unmet_units: int


def _axis_limit(
    output: SearchOutput,
    targets: Sequence[TargetGroup],
    remaining: tuple[int, ...],
) -> int:
    selector = selector_from_label(output.label)
    available = sum(
        count
        for target, count in zip(targets, remaining)
        if selector.matches(target)
    )
    if output.max_units is None:
        return available
    return min(output.max_units, available)


def enumerate_typed_retrieval_actions(
    outputs: Sequence[SearchOutput],
    targets: Sequence[TargetGroup],
) -> tuple[TypedRetrievalAction, ...]:
    """Enumerate every legal restricted-search target selection, including zero."""

    output_axes = tuple(outputs)
    target_groups = tuple(targets)
    for output in output_axes:
        selector_from_label(output.label)

    initial_remaining = tuple(target.copies for target in target_groups)
    zero_usage = (0,) * len(output_axes)
    zero_distinct = tuple(frozenset() for _ in output_axes)

    states = {
        (
            initial_remaining,
            zero_usage,
            zero_distinct,
        )
    }

    for axis_index, output in enumerate(output_axes):
        selector = selector_from_label(output.label)
        next_axis_states = set()

        for remaining, usage, distinct_values in states:
            layer = {(remaining, usage, distinct_values)}
            next_axis_states.update(layer)

            for _ in range(_axis_limit(output, target_groups, remaining)):
                following = set()
                for current_remaining, current_usage, current_distinct in layer:
                    for target_index, target in enumerate(target_groups):
                        if current_remaining[target_index] <= 0:
                            continue
                        if not selector.matches(target):
                            continue

                        diversity_value = selector.diversity_value(target)
                        if selector.distinct_prefix is not None:
                            if diversity_value is None:
                                continue
                            if diversity_value in current_distinct[axis_index]:
                                continue

                        reduced = list(current_remaining)
                        reduced[target_index] -= 1
                        increased_usage = list(current_usage)
                        increased_usage[axis_index] += 1
                        next_distinct = list(current_distinct)
                        if diversity_value is not None:
                            next_distinct[axis_index] = (
                                next_distinct[axis_index]
                                | frozenset({diversity_value})
                            )
                        following.add(
                            (
                                tuple(reduced),
                                tuple(increased_usage),
                                tuple(next_distinct),
                            )
                        )

                if not following:
                    break
                next_axis_states.update(following)
                layer = following

        states = next_axis_states

    return tuple(
        sorted(
            {
                TypedRetrievalAction(
                    target_cost=tuple(
                        start - left
                        for start, left in zip(initial_remaining, remaining)
                    ),
                    axis_usage=usage,
                )
                for remaining, usage, _distinct_values in states
            },
            key=lambda action: (action.axis_usage, action.target_cost),
        )
    )


def project_retrieval_to_demands(
    action: TypedRetrievalAction,
    targets: Sequence[TargetGroup],
    demands: Sequence[DemandChannel],
) -> RetrievalDemandProjection:
    """Project one exact retrieval onto strategic demand without changing it."""

    target_groups = tuple(targets)
    demand_channels = tuple(demands)
    if len(action.target_cost) != len(target_groups):
        raise ValueError("target_cost length does not match targets")
    if not demand_channels:
        raise ValueError("demands cannot be empty")
    if any(value < 0 for value in action.target_cost):
        raise ValueError("target_cost cannot be negative")

    for selected, target in zip(action.target_cost, target_groups):
        if selected > target.copies:
            raise ValueError(
                f"retrieval selects {selected} copies of {target.name!r}, "
                f"but only {target.copies} are represented"
            )

    zero = (0,) * len(demand_channels)
    states = {zero}

    for target, selected in zip(target_groups, action.target_cost):
        for _ in range(selected):
            following = set(states)
            for supplied in states:
                for demand_index, demand in enumerate(demand_channels):
                    if supplied[demand_index] >= demand.copies:
                        continue
                    if not demand.selector.matches(target):
                        continue
                    increased = list(supplied)
                    increased[demand_index] += 1
                    following.add(tuple(increased))
            states = following

    profiles = tuple(sorted(states))
    full = tuple(demand.copies for demand in demand_channels)
    return RetrievalDemandProjection(
        profiles=profiles,
        full_demand_feasible=full in states,
        minimum_unmet_units=min(
            sum(max(0, needed - supplied) for needed, supplied in zip(full, profile))
            for profile in profiles
        ),
    )
