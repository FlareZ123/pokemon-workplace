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
    apply_typed_retrieval_action,
    apply_typed_search_action,
)
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from typed_search_retrieval import (
    TypedRetrievalAction,
    enumerate_typed_retrieval_actions,
)
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
    optional_discard_paid: bool = False


def _split_axis_usage(
    profile: CompiledTrainerSearchProfile,
    axis_usage: tuple[int, ...],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    base_count = len(profile.base_outputs)
    conditional_count = len(profile.conditional_outputs)
    if len(axis_usage) == base_count:
        return axis_usage, (0,) * conditional_count
    if len(axis_usage) == base_count + conditional_count:
        return (
            axis_usage[:base_count],
            axis_usage[base_count:],
        )
    raise ValueError("axis usage length does not match compiled search outputs")


def _resolve_optional_payment(
    profile: CompiledTrainerSearchProfile,
    conditional_usage: tuple[int, ...],
    pay_optional_discard: bool | None,
) -> bool:
    if profile.optional_discard_other_cards <= 0:
        if pay_optional_discard is True:
            raise ValueError("profile has no optional discard branch")
        if any(conditional_usage):
            raise ValueError("conditional outputs require an optional branch")
        return False

    paid = (
        any(conditional_usage)
        if pay_optional_discard is None
        else pay_optional_discard
    )
    if any(conditional_usage) and not paid:
        raise ValueError("conditional search output requires optional discard")
    return paid


def _validated_branch(
    profile: CompiledTrainerSearchProfile,
    demands: Sequence[DemandChannel],
    targets: Sequence[SearchZoneTarget],
    action: TypedTargetAction,
    *,
    pay_optional_discard: bool | None,
) -> tuple[int, bool, bool]:
    target_groups = tuple(target.group for target in targets)
    demand_channels = tuple(demands)
    base_usage, conditional_usage = _split_axis_usage(
        profile,
        action.axis_usage,
    )
    optional_paid = _resolve_optional_payment(
        profile,
        conditional_usage,
        pay_optional_discard,
    )

    base = enumerate_typed_target_profiles(
        profile.base_outputs,
        target_groups,
        demand_channels,
    )
    base_action = TypedTargetAction(
        output=action.output,
        target_cost=action.target_cost,
        axis_usage=base_usage,
    )
    base_valid = base_action in base.actions

    if not optional_paid:
        if base_valid:
            return (
                profile.required_discard_other_cards,
                False,
                False,
            )
        raise ValueError("search action is not valid for the base branch")

    all_outputs = profile.base_outputs + profile.conditional_outputs
    allocation = enumerate_typed_target_profiles(
        all_outputs,
        target_groups,
        demand_channels,
    )
    full_action = TypedTargetAction(
        output=action.output,
        target_cost=action.target_cost,
        axis_usage=base_usage + conditional_usage,
    )
    if full_action not in allocation.actions:
        raise ValueError("search action is not valid for the paid branch")

    return (
        profile.required_discard_other_cards
        + profile.optional_discard_other_cards,
        any(conditional_usage),
        True,
    )


def _validated_retrieval_branch(
    profile: CompiledTrainerSearchProfile,
    targets: Sequence[SearchZoneTarget],
    action: TypedRetrievalAction,
    *,
    pay_optional_discard: bool | None,
) -> tuple[int, bool, bool]:
    target_groups = tuple(target.group for target in targets)
    base_usage, conditional_usage = _split_axis_usage(
        profile,
        action.axis_usage,
    )
    optional_paid = _resolve_optional_payment(
        profile,
        conditional_usage,
        pay_optional_discard,
    )

    base = enumerate_typed_retrieval_actions(
        profile.base_outputs,
        target_groups,
    )
    base_action = TypedRetrievalAction(
        target_cost=action.target_cost,
        axis_usage=base_usage,
    )
    base_valid = base_action in base

    if not optional_paid:
        if not any(action.target_cost) and not profile.discards_entire_hand:
            raise ValueError("free zero-retrieval search has no represented effect")
        if base_valid:
            return (
                profile.required_discard_other_cards,
                False,
                False,
            )
        raise ValueError("retrieval action is not valid for the base branch")

    all_outputs = profile.base_outputs + profile.conditional_outputs
    retrievals = enumerate_typed_retrieval_actions(
        all_outputs,
        target_groups,
    )
    full_action = TypedRetrievalAction(
        target_cost=action.target_cost,
        axis_usage=base_usage + conditional_usage,
    )
    if full_action not in retrievals:
        raise ValueError("retrieval action is not valid for the paid branch")

    return (
        profile.required_discard_other_cards
        + profile.optional_discard_other_cards,
        any(conditional_usage),
        True,
    )


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


def _execute_transaction(
    state: TrainerSearchExecutionState,
    *,
    profile: CompiledTrainerSearchProfile,
    action_card_class: str,
    targets: Sequence[SearchZoneTarget],
    search_action: TypedTargetAction | TypedRetrievalAction,
    fixed_discard_cost: int,
    used_conditional: bool,
    retrieval_first: bool,
    discard_candidates: Sequence[DiscardCandidate],
    discard_selection: DiscardSelection | None,
    play_condition_met: bool | None,
) -> TrainerSearchTransaction:
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

    if retrieval_first:
        if not isinstance(search_action, TypedRetrievalAction):
            raise TypeError("retrieval-first transaction requires TypedRetrievalAction")
        searched = apply_typed_retrieval_action(
            working_zones,
            targets,
            search_action,
        ).after
    else:
        if not isinstance(search_action, TypedTargetAction):
            raise TypeError("demand-first transaction requires TypedTargetAction")
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
    """Execute one demand-first compiled Item/Supporter search action."""

    fixed_discard_cost, used_conditional = _validated_branch(
        profile,
        demands,
        targets,
        search_action,
    )
    return _execute_transaction(
        state,
        profile=profile,
        action_card_class=action_card_class,
        targets=targets,
        search_action=search_action,
        fixed_discard_cost=fixed_discard_cost,
        used_conditional=used_conditional,
        retrieval_first=False,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
    )


def execute_trainer_retrieval_transaction(
    state: TrainerSearchExecutionState,
    *,
    profile: CompiledTrainerSearchProfile,
    action_card_class: str,
    targets: Sequence[SearchZoneTarget],
    retrieval_action: TypedRetrievalAction,
    discard_candidates: Sequence[DiscardCandidate] = (),
    discard_selection: DiscardSelection | None = None,
    play_condition_met: bool | None = None,
) -> TrainerSearchTransaction:
    """Execute one retrieval-first action while preserving optional side outputs."""

    fixed_discard_cost, used_conditional = _validated_retrieval_branch(
        profile,
        targets,
        retrieval_action,
    )
    return _execute_transaction(
        state,
        profile=profile,
        action_card_class=action_card_class,
        targets=targets,
        search_action=retrieval_action,
        fixed_discard_cost=fixed_discard_cost,
        used_conditional=used_conditional,
        retrieval_first=True,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
    )
