"""Adapt conservative compiled typed Trainer searches into staged actions.

This bridge intentionally supports only fixed base branches with a known integer
discard cost. Conditional additional-search branches and whole-hand discard
effects remain in their exact transaction layer until their branch metadata can
be carried without ambiguity.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence

from search_zone_transition import SearchZoneTarget
from staged_trainer_objectives import TrainerAcquisitionAction
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from typed_search_target_allocator import (
    DemandChannel,
    TypedTargetAction,
    enumerate_typed_target_profiles,
)


def adapt_compiled_search_to_staged_action(
    profile: CompiledTrainerSearchProfile,
    demands: Sequence[DemandChannel],
    targets: Sequence[SearchZoneTarget],
    action: TypedTargetAction,
    *,
    copies: int = 1,
    play_condition_met: bool | None = None,
    name: str | None = None,
) -> TrainerAcquisitionAction:
    """Return one trusted staged action from an exact typed base search action."""

    if copies < 0:
        raise ValueError("copies must be non-negative")
    if profile.conditional_outputs or profile.optional_discard_other_cards:
        raise ValueError("conditional search branches are not supported")
    if profile.discards_entire_hand:
        raise ValueError("whole-hand discard cannot be represented by a fixed cost")
    if profile.play_condition is not None and play_condition_met is not True:
        raise ValueError("compiled play condition is not satisfied")

    bound_targets = tuple(targets)
    target_groups = tuple(target.group for target in bound_targets)
    demand_channels = tuple(demands)
    allocation = enumerate_typed_target_profiles(
        profile.base_outputs,
        target_groups,
        demand_channels,
    )
    if action not in allocation.actions:
        raise ValueError("typed action is not valid for the compiled base profile")
    if len(action.target_cost) != len(bound_targets):
        raise ValueError("target cost length does not match targets")

    selected: defaultdict[str, int] = defaultdict(int)
    for target, count in zip(bound_targets, action.target_cost):
        if count < 0:
            raise ValueError("target cost cannot be negative")
        if count:
            selected[target.card_class] += count

    if not selected:
        raise ValueError("staged acquisition action must retrieve at least one card")

    return TrainerAcquisitionAction(
        name=name or profile.name,
        action_class=profile.action_class,
        copies=copies,
        hand_outputs=tuple(sorted(selected.items())),
        discard_cost=profile.required_discard_other_cards,
    )
