"""Adapt compiled Trainer search text to state-valid connector profiles.

This module is the bridge between the conservative text compiler in
trainer_search_profile_compiler.py and the deterministic resource allocator in
resource_constrained_connectors.py.

It deliberately keeps literal search labels. A caller that wants subtype
reasoning such as "Trainer card" satisfying an "Item card" requirement must
provide a separately validated semantic layer rather than receiving that
relationship implicitly here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Sequence

from lock_state_kernel import PlayerChannels
from resource_constrained_connectors import (
    ResourceActionProfile,
    ResourceConnectorType,
)
from trainer_search_profile_compiler import (
    CompiledTrainerSearchProfile,
    SearchOutput,
)
from typed_search_target_allocator import (
    DemandChannel,
    TargetGroup,
    enumerate_typed_target_profiles,
)


RESOURCE_NAMES = (
    "discardable_cards",
    "supporter_plays",
    "stadium_plays",
)


@dataclass(frozen=True)
class TypedTrainerSearchAdaptation:
    """Typed connector plus the shared capacities required to evaluate it."""

    connector: ResourceConnectorType
    resource_capacities: tuple[int, ...]
    resource_names: tuple[str, ...]


@dataclass(frozen=True)
class TrainerSearchState:
    """State variables needed to compile one search card into legal actions."""

    target_counts: tuple[tuple[str, int], ...] = ()
    discardable_cards: int = 0
    supporter_plays_remaining: int = 1
    stadium_plays_remaining: int = 1
    channels: PlayerChannels = field(default_factory=PlayerChannels)
    whole_hand_discard_count: int | None = None

    def target_count(self, label: str) -> int:
        return dict(self.target_counts).get(label, 0)

    @property
    def resource_capacities(self) -> tuple[int, int, int]:
        return (
            self.discardable_cards,
            self.supporter_plays_remaining,
            self.stadium_plays_remaining,
        )


def _action_class_allowed(
    action_class: str,
    state: TrainerSearchState,
) -> bool:
    if action_class == "Item":
        return state.channels.item_play
    if action_class == "Pokémon Tool":
        return state.channels.tool_play
    if action_class == "Supporter":
        return (
            state.channels.supporter_play
            and state.supporter_plays_remaining > 0
        )
    if action_class == "Stadium":
        return (
            state.channels.stadium_play
            and state.stadium_plays_remaining > 0
        )
    raise ValueError(
        f"Unsupported compiled Trainer action class: {action_class}"
    )


def _action_cost(
    profile: CompiledTrainerSearchProfile,
    state: TrainerSearchState,
    *,
    extra_discard: int = 0,
) -> tuple[int, int, int] | None:
    if profile.discards_entire_hand:
        if state.whole_hand_discard_count is None:
            return None
        discard_cost = state.whole_hand_discard_count
    else:
        discard_cost = profile.required_discard_other_cards

    cost = (
        discard_cost + extra_discard,
        int(profile.action_class == "Supporter"),
        int(profile.action_class == "Stadium"),
    )
    if any(
        required > available
        for required, available in zip(
            cost,
            state.resource_capacities,
        )
    ):
        return None
    return cost


def _axis_limit(
    output: SearchOutput,
    state: TrainerSearchState,
) -> int:
    available = state.target_count(output.label)
    if output.max_units is None:
        return available
    return min(available, output.max_units)


def _output_choices(
    outputs: Sequence[SearchOutput],
    demand_channels: Sequence[str],
    state: TrainerSearchState,
):
    """Yield nonzero exact-label output vectors and per-axis selections."""

    channels = tuple(demand_channels)
    ranges = tuple(
        range(_axis_limit(output, state) + 1)
        for output in outputs
    )

    for selected in product(*ranges):
        if not any(selected):
            continue

        selected_by_label: dict[str, int] = {}
        for output, count in zip(outputs, selected):
            selected_by_label[output.label] = (
                selected_by_label.get(output.label, 0)
                + count
            )
        if any(
            count > state.target_count(label)
            for label, count in selected_by_label.items()
        ):
            continue

        vector = [0] * len(channels)
        for output, count in zip(outputs, selected):
            for index, channel in enumerate(channels):
                if output.label == channel:
                    vector[index] += count

        if any(vector):
            yield tuple(vector), selected


def adapt_compiled_search_profile(
    profile: CompiledTrainerSearchProfile,
    demand_channels: Sequence[str],
    state: TrainerSearchState,
    *,
    copies: int = 1,
    play_condition_met: bool | None = None,
) -> ResourceConnectorType | None:
    """Compile one card into state-valid resource-constrained actions.

    Search quantities are optional down to zero for the restricted deck-search
    families covered by the compiler, so each legal nonzero subset is emitted as
    its own output profile.

    For a conditional-additional search such as Guzma & Hala, the base branch is
    emitted at its ordinary cost. The paid branch is emitted only when at least
    one conditional output is selected. This adapter values search output only;
    a model that assigns independent positive value to discarding cards should
    represent that benefit as another state transition.
    """

    if copies < 0:
        raise ValueError("copies must be non-negative")
    if copies == 0:
        return None
    if not demand_channels:
        raise ValueError("demand_channels cannot be empty")
    if not _action_class_allowed(profile.action_class, state):
        return None
    if (
        profile.play_condition is not None
        and play_condition_met is not True
    ):
        return None

    actions: set[ResourceActionProfile] = set()

    base_cost = _action_cost(profile, state)
    if base_cost is not None:
        for output, _ in _output_choices(
            profile.base_outputs,
            demand_channels,
            state,
        ):
            actions.add(
                ResourceActionProfile(
                    output=output,
                    cost=base_cost,
                )
            )

    if (
        profile.conditional_outputs
        and profile.optional_discard_other_cards > 0
    ):
        conditional_cost = _action_cost(
            profile,
            state,
            extra_discard=profile.optional_discard_other_cards,
        )
        if conditional_cost is not None:
            all_outputs = (
                profile.base_outputs
                + profile.conditional_outputs
            )
            base_axis_count = len(profile.base_outputs)
            for output, selected in _output_choices(
                all_outputs,
                demand_channels,
                state,
            ):
                if not any(selected[base_axis_count:]):
                    continue
                actions.add(
                    ResourceActionProfile(
                        output=output,
                        cost=conditional_cost,
                    )
                )

    if not actions:
        return None

    ordered_actions = tuple(
        sorted(
            actions,
            key=lambda action: (
                action.cost,
                action.output,
            ),
        )
    )
    return ResourceConnectorType(
        name=profile.name,
        copies=copies,
        profiles=ordered_actions,
    )


def adapt_compiled_search_profile_typed(
    profile: CompiledTrainerSearchProfile,
    demands: Sequence[DemandChannel],
    targets: Sequence[TargetGroup],
    state: TrainerSearchState,
    *,
    copies: int = 1,
    play_condition_met: bool | None = None,
) -> TypedTrainerSearchAdaptation | None:
    """Compile one card using semantic selectors and physical target depletion.

    The returned resource vector begins with the ordinary state resources
    (discardable cards, Supporter plays, Stadium plays) and appends one capacity
    for each physical target group. ResourceActionProfile costs therefore carry
    target depletion into the shared connector solver, including across several
    copies of the same connector.
    """

    if copies < 0:
        raise ValueError("copies must be non-negative")
    if copies == 0:
        return None

    demand_channels = tuple(demands)
    target_groups = tuple(targets)
    if not demand_channels:
        raise ValueError("demands cannot be empty")
    if not _action_class_allowed(profile.action_class, state):
        return None
    if (
        profile.play_condition is not None
        and play_condition_met is not True
    ):
        return None

    resource_capacities = (
        state.resource_capacities
        + tuple(target.copies for target in target_groups)
    )
    resource_names = (
        RESOURCE_NAMES
        + tuple(
            f"target:{index}:{target.name}"
            for index, target in enumerate(target_groups)
        )
    )

    actions: set[ResourceActionProfile] = set()

    base_cost = _action_cost(profile, state)
    if base_cost is not None:
        base_allocation = enumerate_typed_target_profiles(
            profile.base_outputs,
            target_groups,
            demand_channels,
        )
        for action in base_allocation.actions:
            actions.add(
                ResourceActionProfile(
                    output=action.output,
                    cost=base_cost + action.target_cost,
                )
            )

    if (
        profile.conditional_outputs
        and profile.optional_discard_other_cards > 0
    ):
        conditional_cost = _action_cost(
            profile,
            state,
            extra_discard=profile.optional_discard_other_cards,
        )
        if conditional_cost is not None:
            all_outputs = (
                profile.base_outputs
                + profile.conditional_outputs
            )
            base_axis_count = len(profile.base_outputs)
            allocation = enumerate_typed_target_profiles(
                all_outputs,
                target_groups,
                demand_channels,
            )
            for action in allocation.actions:
                if not any(action.axis_usage[base_axis_count:]):
                    continue
                actions.add(
                    ResourceActionProfile(
                        output=action.output,
                        cost=conditional_cost + action.target_cost,
                    )
                )

    if not actions:
        return None

    connector = ResourceConnectorType(
        name=profile.name,
        copies=copies,
        profiles=tuple(
            sorted(
                actions,
                key=lambda action: (
                    action.cost,
                    action.output,
                ),
            )
        ),
    )
    return TypedTrainerSearchAdaptation(
        connector=connector,
        resource_capacities=resource_capacities,
        resource_names=resource_names,
    )
