"""Adapt conservative compiled typed Trainer searches into staged actions.

This bridge supports fixed-cost base and optional paid branches by delegating
branch validation to the exact Trainer search transaction layer. Whole-hand
discard effects remain outside this scalar staged-action representation.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence

from search_zone_transition import SearchZoneTarget
from staged_trainer_objectives import TrainerAcquisitionAction
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from trainer_search_transaction import validate_trainer_search_branch
from typed_search_target_allocator import DemandChannel, TypedTargetAction


def adapt_compiled_search_to_staged_action(
    profile: CompiledTrainerSearchProfile,
    demands: Sequence[DemandChannel],
    targets: Sequence[SearchZoneTarget],
    action: TypedTargetAction,
    *,
    copies: int = 1,
    play_condition_met: bool | None = None,
    pay_optional_discard: bool | None = None,
    name: str | None = None,
) -> TrainerAcquisitionAction:
    """Return one trusted staged action from an exact typed search branch."""

    if copies < 0:
        raise ValueError("copies must be non-negative")
    if profile.discards_entire_hand:
        raise ValueError("whole-hand discard cannot be represented by a fixed cost")
    if profile.play_condition is not None and play_condition_met is not True:
        raise ValueError("compiled play condition is not satisfied")

    bound_targets = tuple(targets)
    demand_channels = tuple(demands)
    branch = validate_trainer_search_branch(
        profile,
        demand_channels,
        bound_targets,
        action,
        pay_optional_discard=pay_optional_discard,
    )
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
        discard_cost=branch.discard_cost,
    )
