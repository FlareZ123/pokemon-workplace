"""Compose printed-HP-safe Item searches with multi-target K1/public inference.

Public observation is the sorted multiset of exact selected print IDs. That
label is derived from the physical action, preventing caller-defined public
signals from disagreeing with the Pokémon entering the Bench.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from deck_search_target_signal import TargetSelectionPolicy
from direct_bench_hidden_state_bridge import (
    HiddenMultiDirectBenchTrainerTransition,
    execute_hidden_multi_direct_bench_trainer_transaction,
)
from direct_bench_search_execution import DirectBenchPlacement, DirectBenchTarget
from direct_bench_trainer_transaction import DirectBenchTrainerExecutionState
from hp_bounded_direct_bench_transaction import (
    HPBoundedDirectBenchProfile,
    validate_hp_bounded_targets,
)
from pokemon_board_metadata import PokemonBoardMetadata
from pokemon_card_profile import PokemonCardProfile
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from typed_search_target_allocator import DemandChannel, TypedTargetAction


def selected_print_multiset_label(
    targets: Sequence[DirectBenchTarget],
    action: TypedTargetAction,
) -> str:
    """Public exact-print multiset, independent of physical Bench entry order."""

    if len(targets) != len(action.target_cost):
        raise ValueError("search action and targets disagree on target dimensions")
    if any(not isinstance(count, int) or count < 0 for count in action.target_cost):
        raise ValueError("selected target counts must be nonnegative integers")
    prints = sorted(
        target.search_target.card_class
        for target, count in zip(targets, action.target_cost)
        for _ in range(count)
    )
    if not prints:
        raise ValueError("at least one public searched target is required")
    return "|".join(prints)


def execute_hp_bounded_hidden_direct_bench_trainer_transaction(
    physical: SearchableDeckPhysicalState,
    state: DirectBenchTrainerExecutionState,
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    profile: HPBoundedDirectBenchProfile,
    action_card_class: str,
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
    """Run an eligible 1-or-2 Basic Poffin search with observer beliefs."""

    validate_hp_bounded_targets(
        profile,
        action_card_class=action_card_class,
        targets=targets,
        board_metadata_by_id=board_metadata_by_id,
        card_profiles_by_id=card_profiles_by_id,
    )
    observed = selected_print_multiset_label(targets, search_action)

    return execute_hidden_multi_direct_bench_trainer_transaction(
        physical,
        state,
        prizes_by_observer,
        actor_id=actor_id,
        profile=profile.direct,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        placements=placements,
        target_probability_by_composition=target_probability_by_composition,
        observed_target=observed,
        group_by_card_class=group_by_card_class,
        sampled_top_card_class=sampled_top_card_class,
        sampled_top_card_name=sampled_top_card_name,
        sampled_top_instance_id=sampled_top_instance_id,
    )
