"""Execute Trainer search transactions from live continuous and temporal sources."""

from __future__ import annotations

from collections.abc import Sequence

from active_source_scoped_restrictions import (
    ContinuousRestrictionSource,
    active_restrictions_for_player,
)
from attack_restriction_turn_windows import AttackRestrictionWindow
from card_action_metadata import CardActionMetadata
from discard_cost_witness import DiscardCandidate, DiscardSelection
from search_zone_transition import SearchZoneTarget
from source_scoped_trainer_transaction import (
    execute_source_scoped_trainer_retrieval_transaction,
    execute_source_scoped_trainer_search_transaction,
)
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
)
from typed_search_retrieval import TypedRetrievalAction
from typed_search_target_allocator import DemandChannel, TypedTargetAction


def execute_active_source_trainer_search_transaction(
    state: TrainerSearchExecutionState,
    *,
    player: str,
    profile: CompiledTrainerSearchProfile,
    action_metadata: CardActionMetadata,
    action_card_class: str,
    demands: Sequence[DemandChannel],
    targets: Sequence[SearchZoneTarget],
    search_action: TypedTargetAction,
    continuous_sources: Sequence[ContinuousRestrictionSource] = (),
    attack_windows: Sequence[AttackRestrictionWindow] = (),
    discard_candidates: Sequence[DiscardCandidate] = (),
    discard_selection: DiscardSelection | None = None,
    play_condition_met: bool | None = None,
    pay_optional_discard: bool | None = None,
    search_destination_zone: str = "hand",
) -> TrainerSearchTransaction:
    restrictions = active_restrictions_for_player(
        player,
        continuous_sources=continuous_sources,
        attack_windows=attack_windows,
    )
    return execute_source_scoped_trainer_search_transaction(
        state,
        profile=profile,
        action_metadata=action_metadata,
        active_restrictions=restrictions,
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


def execute_active_source_trainer_retrieval_transaction(
    state: TrainerSearchExecutionState,
    *,
    player: str,
    profile: CompiledTrainerSearchProfile,
    action_metadata: CardActionMetadata,
    action_card_class: str,
    targets: Sequence[SearchZoneTarget],
    retrieval_action: TypedRetrievalAction,
    continuous_sources: Sequence[ContinuousRestrictionSource] = (),
    attack_windows: Sequence[AttackRestrictionWindow] = (),
    discard_candidates: Sequence[DiscardCandidate] = (),
    discard_selection: DiscardSelection | None = None,
    play_condition_met: bool | None = None,
    pay_optional_discard: bool | None = None,
    search_destination_zone: str = "hand",
) -> TrainerSearchTransaction:
    restrictions = active_restrictions_for_player(
        player,
        continuous_sources=continuous_sources,
        attack_windows=attack_windows,
    )
    return execute_source_scoped_trainer_retrieval_transaction(
        state,
        profile=profile,
        action_metadata=action_metadata,
        active_restrictions=restrictions,
        action_card_class=action_card_class,
        targets=targets,
        retrieval_action=retrieval_action,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
        pay_optional_discard=pay_optional_discard,
        search_destination_zone=search_destination_zone,
    )
