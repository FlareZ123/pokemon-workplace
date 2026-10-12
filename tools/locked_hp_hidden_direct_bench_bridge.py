"""Single preflight for Item lock, Poffin printed HP, K1 and public targets.

Lock permission is checked before the searcher inspects the deck. A prohibited
hand Item does not create a new Prize observation or physical state transition.
The HP-bounded hidden bridge then owns the legal search and its information.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from card_action_metadata import CardActionMetadata
from deck_search_shuffle_topology import SearchableDeckPhysicalState
from deck_search_target_signal import TargetSelectionPolicy
from direct_bench_hidden_state_bridge import HiddenMultiDirectBenchTrainerTransition
from direct_bench_search_execution import DirectBenchPlacement, DirectBenchTarget
from direct_bench_trainer_transaction import DirectBenchTrainerExecutionState
from hp_bounded_direct_bench_transaction import HPBoundedDirectBenchProfile
from hp_bounded_hidden_direct_bench_bridge import (
    execute_hp_bounded_hidden_direct_bench_trainer_transaction,
)
from locked_hp_direct_bench_transaction import validate_locked_hp_hand_play
from pokemon_board_metadata import PokemonBoardMetadata
from pokemon_card_profile import PokemonCardProfile
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from source_scoped_action_restrictions import SourceScopedActionRestriction
from typed_search_target_allocator import DemandChannel, TypedTargetAction


def execute_locked_hp_hidden_direct_bench_transaction(
    physical: SearchableDeckPhysicalState,
    state: DirectBenchTrainerExecutionState,
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    profile: HPBoundedDirectBenchProfile,
    action_card_class: str,
    active_restrictions: Sequence[SourceScopedActionRestriction],
    action_metadata_by_id: Mapping[str, CardActionMetadata],
    demands: Sequence[DemandChannel],
    targets: Sequence[DirectBenchTarget],
    search_action: TypedTargetAction,
    placements: Sequence[DirectBenchPlacement],
    target_probability_by_composition: TargetSelectionPolicy,
    group_by_card_class: Mapping[str, PrizeGroup],
    sampled_top_card_class: str,
    sampled_top_card_name: str,
    sampled_top_instance_id: str,
    board_metadata_by_id: Mapping[str, PokemonBoardMetadata],
    card_profiles_by_id: Mapping[str, PokemonCardProfile],
) -> HiddenMultiDirectBenchTrainerTransition:
    """One lock-checked, source-authenticated, observed Poffin search."""

    validate_locked_hp_hand_play(
        state,
        profile,
        action_card_class=action_card_class,
        active_restrictions=active_restrictions,
        action_metadata_by_id=action_metadata_by_id,
    )
    return execute_hp_bounded_hidden_direct_bench_trainer_transaction(
        physical,
        state,
        prizes_by_observer,
        actor_id=actor_id,
        profile=profile,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        placements=placements,
        target_probability_by_composition=target_probability_by_composition,
        group_by_card_class=group_by_card_class,
        sampled_top_card_class=sampled_top_card_class,
        sampled_top_card_name=sampled_top_card_name,
        sampled_top_instance_id=sampled_top_instance_id,
        board_metadata_by_id=board_metadata_by_id,
        card_profiles_by_id=card_profiles_by_id,
    )
