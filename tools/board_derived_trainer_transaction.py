"""Execute Trainer search/retrieval transactions from canonical board lock state."""

from __future__ import annotations

from collections.abc import Sequence

from ability_lock_causal_state import AbilityLockCausalState
from active_source_trainer_transaction import (
    execute_active_source_trainer_retrieval_transaction,
    execute_active_source_trainer_search_transaction,
)
from attack_restriction_turn_windows import AttackRestrictionWindow
from board_derived_continuous_restrictions import (
    derive_continuous_restriction_sources,
)
from board_object_kernel import BoardState
from card_action_metadata import CardActionMetadata
from discard_cost_witness import DiscardCandidate, DiscardSelection
from search_zone_transition import SearchZoneTarget
from source_scoped_restriction_activation import RestrictionActivationProfile
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
)
from typed_search_retrieval import TypedRetrievalAction
from typed_search_target_allocator import DemandChannel, TypedTargetAction


def _derived_continuous_sources(
    *,
    player_board: BoardState,
    opponent_board: BoardState,
    restriction_profiles: Sequence[RestrictionActivationProfile],
    lock_state: AbilityLockCausalState,
    stadium_name: str | None,
    player_id: str,
    opponent_id: str,
):
    return derive_continuous_restriction_sources(
        player_board,
        opponent_board,
        profiles=restriction_profiles,
        lock_state=lock_state,
        stadium_name=stadium_name,
        player_id=player_id,
        opponent_id=opponent_id,
    )


def execute_board_derived_trainer_search_transaction(
    state: TrainerSearchExecutionState,
    *,
    player: str,
    player_board: BoardState,
    opponent_board: BoardState,
    restriction_profiles: Sequence[RestrictionActivationProfile],
    lock_state: AbilityLockCausalState,
    profile: CompiledTrainerSearchProfile,
    action_metadata: CardActionMetadata,
    action_card_class: str,
    demands: Sequence[DemandChannel],
    targets: Sequence[SearchZoneTarget],
    search_action: TypedTargetAction,
    stadium_name: str | None = None,
    player_id: str = "player",
    opponent_id: str = "opponent",
    attack_windows: Sequence[AttackRestrictionWindow] = (),
    discard_candidates: Sequence[DiscardCandidate] = (),
    discard_selection: DiscardSelection | None = None,
    play_condition_met: bool | None = None,
    pay_optional_discard: bool | None = None,
    search_destination_zone: str = "hand",
) -> TrainerSearchTransaction:
    """Execute a Trainer search after deriving continuous locks from boards."""

    if player not in {player_id, opponent_id}:
        raise ValueError("unknown player")
    continuous_sources = _derived_continuous_sources(
        player_board=player_board,
        opponent_board=opponent_board,
        restriction_profiles=restriction_profiles,
        lock_state=lock_state,
        stadium_name=stadium_name,
        player_id=player_id,
        opponent_id=opponent_id,
    )
    return execute_active_source_trainer_search_transaction(
        state,
        player=player,
        profile=profile,
        action_metadata=action_metadata,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        continuous_sources=continuous_sources,
        attack_windows=attack_windows,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
        pay_optional_discard=pay_optional_discard,
        search_destination_zone=search_destination_zone,
    )


def execute_board_derived_trainer_retrieval_transaction(
    state: TrainerSearchExecutionState,
    *,
    player: str,
    player_board: BoardState,
    opponent_board: BoardState,
    restriction_profiles: Sequence[RestrictionActivationProfile],
    lock_state: AbilityLockCausalState,
    profile: CompiledTrainerSearchProfile,
    action_metadata: CardActionMetadata,
    action_card_class: str,
    targets: Sequence[SearchZoneTarget],
    retrieval_action: TypedRetrievalAction,
    stadium_name: str | None = None,
    player_id: str = "player",
    opponent_id: str = "opponent",
    attack_windows: Sequence[AttackRestrictionWindow] = (),
    discard_candidates: Sequence[DiscardCandidate] = (),
    discard_selection: DiscardSelection | None = None,
    play_condition_met: bool | None = None,
    pay_optional_discard: bool | None = None,
    search_destination_zone: str = "hand",
) -> TrainerSearchTransaction:
    """Execute a Trainer retrieval after deriving continuous locks from boards."""

    if player not in {player_id, opponent_id}:
        raise ValueError("unknown player")
    continuous_sources = _derived_continuous_sources(
        player_board=player_board,
        opponent_board=opponent_board,
        restriction_profiles=restriction_profiles,
        lock_state=lock_state,
        stadium_name=stadium_name,
        player_id=player_id,
        opponent_id=opponent_id,
    )
    return execute_active_source_trainer_retrieval_transaction(
        state,
        player=player,
        profile=profile,
        action_metadata=action_metadata,
        action_card_class=action_card_class,
        targets=targets,
        retrieval_action=retrieval_action,
        continuous_sources=continuous_sources,
        attack_windows=attack_windows,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
        pay_optional_discard=pay_optional_discard,
        search_destination_zone=search_destination_zone,
    )
