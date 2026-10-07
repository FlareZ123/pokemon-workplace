"""Atomic execution for a conservative Item/Supporter deck-search transaction.

This composes exact typed target selection, exact discard-cost selection,
exchangeable zone counts, play-lock channels, and the shared turn budget.

The played Trainer is moved to a temporary resolving zone before its
instructions are applied. This distinguishes the physical card being played
from other same-class copies that remain in hand.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    apply_discard_selection,
)
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from search_zone_transition import (
    SearchZoneTarget,
    apply_typed_search_action,
)
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from turn_action_budget import TurnAction, TurnActionBudget
from typed_search_target_allocator import (
    DemandChannel,
    TypedTargetAction,
    enumerate_typed_target_profiles,
)


RESOLVING_TRAINER_ZONE = "resolving_trainer"


@dataclass(frozen=True)
class TrainerSearchExecutionState:
    zones: ZoneCountState
    budget: TurnActionBudget = field(default_factory=TurnActionBudget)
    channels: PlayerChannels = field(default_factory=PlayerChannels)


@dataclass(frozen=True)
class TrainerSearchTransaction:
    before: TrainerSearchExecutionState
    after: TrainerSearchExecutionState
    discard_cost: int
    used_conditional_outputs: bool


def _validated_branch(
    profile: CompiledTrainerSearchProfile,
    demands: Sequence[DemandChannel],
    targets: Sequence[SearchZoneTarget],
    action: TypedTargetAction,
) -> tuple[int, bool]:
    target_groups = tuple(target.group for target in targets)
    demand_channels = tuple(demands)

    base = enumerate_typed_target_profiles(
        profile.base_outputs,
        target_groups,
        demand_channels,
    )
    if action in base.actions:
        return profile.required_discard_other_cards, False

    if (
        profile.conditional_outputs
        and profile.optional_discard_other_cards > 0
    ):
        all_outputs = profile.base_outputs + profile.conditional_outputs
        allocation = enumerate_typed_target_profiles(
            all_outputs,
            target_groups,
            demand_channels,
        )
        base_axis_count = len(profile.base_outputs)
        if (
            action in allocation.actions
            and any(action.axis_usage[base_axis_count:])
        ):
            return (
                profile.required_discard_other_cards
                + profile.optional_discard_other_cards,
                True,
            )

    raise ValueError("search action is not valid for this compiled profile")


def _discard_entire_hand(
    state: ZoneCountState,
) -> tuple[ZoneCountState, int]:
    hand_counts = tuple(
        (card_class, count)
        for card_class, zone, count in state.counts
        if zone == "hand"
    )
    after = state
    discarded = 0
    for card_class, count in hand_counts:
        after = after.move(
            card_class,
            "hand",
            "discard",
            amount=count,
        )
        discarded += count
    return after, discarded


def execute_trainer_search_transaction(
    state: TrainerSearchExecutionState,
    *,
    profile: CompiledTrainerSearchProfile,
    action_card_class: str,
    demands: Sequence[DemandChannel],
    targets: Sequence[SearchZoneTarget],
    search_action: TypedTargetAction,
    discard_candidates: Sequence[DiscardCandidate] = (),
    discard_selection: DiscardSelection | None = None,
    play_condition_met: bool | None = None,
) -> TrainerSearchTransaction:
    """Execute one validated compiled Item/Supporter search action atomically."""

    if not action_card_class:
        raise ValueError("action_card_class must be non-empty")
    if profile.action_class not in {"Item", "Supporter"}:
        raise ValueError(
            f"unsupported Trainer action class: {profile.action_class!r}"
        )
    if profile.play_condition is not None and play_condition_met is not True:
        raise ValueError("compiled play condition is not satisfied")
    if state.zones.count(action_card_class, "hand") < 1:
        raise ValueError("played Trainer card is not in hand")
    if any(
        zone == RESOLVING_TRAINER_ZONE
        for _card_class, zone, _count in state.zones.counts
    ):
        raise ValueError("state already contains a resolving Trainer")

    if profile.action_class == "Item":
        if not state.channels.item_play:
            raise ValueError("Item play is locked")
        next_budget = state.budget
    else:
        if not state.channels.supporter_play:
            raise ValueError("Supporter play is locked")
        next_budget = state.budget.consume(TurnAction.SUPPORTER)
        if next_budget is None:
            raise ValueError("Supporter action budget is exhausted")

    fixed_discard_cost, used_conditional = _validated_branch(
        profile,
        demands,
        targets,
        search_action,
    )

    working_zones = state.zones.move(
        action_card_class,
        "hand",
        RESOLVING_TRAINER_ZONE,
    )
    candidates = tuple(discard_candidates)

    if profile.discards_entire_hand:
        if candidates or discard_selection is not None:
            raise ValueError(
                "whole-hand discard is derived from the resolving hand snapshot"
            )
        working_zones, discard_cost = _discard_entire_hand(working_zones)
    else:
        discard_cost = fixed_discard_cost
        if discard_cost == 0:
            if discard_selection is not None and discard_selection.cost != 0:
                raise ValueError(
                    "discard selection supplied for a zero-cost action"
                )
        else:
            if discard_selection is None:
                raise ValueError("exact discard selection is required")
            if discard_selection.cost != discard_cost:
                raise ValueError(
                    f"discard selection costs {discard_selection.cost}, "
                    f"expected {discard_cost}"
                )
            working_zones = apply_discard_selection(
                working_zones,
                candidates,
                discard_selection,
            ).after

    searched = apply_typed_search_action(
        working_zones,
        targets,
        search_action,
    ).after

    after_zones = searched.move(
        action_card_class,
        RESOLVING_TRAINER_ZONE,
        "discard",
    )

    classes = {
        card_class
        for card_class, _zone, _count in state.zones.counts
    } | {
        card_class
        for card_class, _zone, _count in after_zones.counts
    }
    for card_class in classes:
        if state.zones.total(card_class) != after_zones.total(card_class):
            raise AssertionError(
                f"card total changed for {card_class!r}: "
                f"{state.zones.total(card_class)} -> {after_zones.total(card_class)}"
            )

    after = TrainerSearchExecutionState(
        zones=after_zones,
        budget=next_budget,
        channels=state.channels,
    )
    return TrainerSearchTransaction(
        before=state,
        after=after,
        discard_cost=discard_cost,
        used_conditional_outputs=used_conditional,
    )
