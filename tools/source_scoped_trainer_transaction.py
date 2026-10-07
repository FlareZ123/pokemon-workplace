"""Gate Trainer search transactions with source-scoped action permissions."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from card_action_metadata import CardActionMetadata
from discard_cost_witness import DiscardCandidate, DiscardSelection
from search_zone_transition import SearchZoneTarget
from source_scoped_action_restrictions import SourceScopedActionRestriction
from source_scoped_channel_projection import action_allowed, project_source_scoped_permissions
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
    execute_trainer_retrieval_transaction,
    execute_trainer_search_transaction,
)
from typed_search_retrieval import TypedRetrievalAction
from typed_search_target_allocator import DemandChannel, TypedTargetAction


_ACTION_CLASS_TO_KIND = {"Item": "item", "Supporter": "supporter"}


def _permission_gated_state(
    state: TrainerSearchExecutionState,
    profile: CompiledTrainerSearchProfile,
    action_metadata: CardActionMetadata,
    restrictions: Sequence[SourceScopedActionRestriction],
) -> TrainerSearchExecutionState:
    expected_kind = _ACTION_CLASS_TO_KIND.get(profile.action_class)
    if expected_kind is None:
        raise ValueError(f"unsupported Trainer action class: {profile.action_class!r}")
    if action_metadata.card_id != profile.card_id:
        raise ValueError("action metadata does not match compiled Trainer print")
    if action_metadata.card_kind != expected_kind:
        raise ValueError("action metadata kind disagrees with Trainer profile")
    projection = project_source_scoped_permissions(
        restrictions,
        base_channels=state.channels,
    )
    if not action_allowed(projection, action_metadata.attempt("hand")):
        raise ValueError("Trainer play is unavailable under current restrictions")
    return replace(state, channels=projection.channels)


def _restore_base_channels(
    transaction: TrainerSearchTransaction,
    original_state: TrainerSearchExecutionState,
) -> TrainerSearchTransaction:
    return replace(
        transaction,
        before=original_state,
        after=replace(transaction.after, channels=original_state.channels),
    )


def execute_source_scoped_trainer_search_transaction(
    state: TrainerSearchExecutionState,
    *,
    profile: CompiledTrainerSearchProfile,
    action_metadata: CardActionMetadata,
    active_restrictions: Sequence[SourceScopedActionRestriction] = (),
    action_card_class: str,
    demands: Sequence[DemandChannel],
    targets: Sequence[SearchZoneTarget],
    search_action: TypedTargetAction,
    discard_candidates: Sequence[DiscardCandidate] = (),
    discard_selection: DiscardSelection | None = None,
    play_condition_met: bool | None = None,
    pay_optional_discard: bool | None = None,
    search_destination_zone: str = "hand",
) -> TrainerSearchTransaction:
    gated = _permission_gated_state(state, profile, action_metadata, active_restrictions)
    transaction = execute_trainer_search_transaction(
        gated,
        profile=profile,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
        pay_optional_discard=pay_optional_discard,
        search_destination_zone=search_destination_zone,
    )
    return _restore_base_channels(transaction, state)


def execute_source_scoped_trainer_retrieval_transaction(
    state: TrainerSearchExecutionState,
    *,
    profile: CompiledTrainerSearchProfile,
    action_metadata: CardActionMetadata,
    active_restrictions: Sequence[SourceScopedActionRestriction] = (),
    action_card_class: str,
    targets: Sequence[SearchZoneTarget],
    retrieval_action: TypedRetrievalAction,
    discard_candidates: Sequence[DiscardCandidate] = (),
    discard_selection: DiscardSelection | None = None,
    play_condition_met: bool | None = None,
    pay_optional_discard: bool | None = None,
    search_destination_zone: str = "hand",
) -> TrainerSearchTransaction:
    gated = _permission_gated_state(state, profile, action_metadata, active_restrictions)
    transaction = execute_trainer_retrieval_transaction(
        gated,
        profile=profile,
        action_card_class=action_card_class,
        targets=targets,
        retrieval_action=retrieval_action,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
        pay_optional_discard=pay_optional_discard,
        search_destination_zone=search_destination_zone,
    )
    return _restore_base_channels(transaction, state)
