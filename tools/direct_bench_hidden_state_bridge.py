"""Hidden-state bridge for single-target direct-to-Bench Trainer searches.

A Basic Pokemon placed publicly onto the Bench is an observable search target
even when the card text does not use the word "reveal". This bridge composes
that public signal with K1 Prize inference, the atomic direct-Bench Trainer
transaction, and an exact sampled post-shuffle top card.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from deck_search_shuffle_physical_belief import (
    actual_prize_group_counts,
    deck_prize_pool_profile,
)
from deck_search_shuffle_topology import (
    SearchableDeckPhysicalState,
    finish_shuffle_with_sampled_top,
)
from deck_search_target_signal import (
    TargetSelectionPolicy,
    resolve_revealed_search_target_shuffle,
    resolve_revealed_search_targets_shuffle,
)
from direct_bench_search_execution import DirectBenchPlacement, DirectBenchTarget
from direct_bench_search_profile_compiler import DirectBenchSearchProfile
from direct_bench_trainer_transaction import (
    DirectBenchTrainerExecutionState,
    DirectBenchTrainerTransaction,
    execute_direct_bench_trainer_transaction,
)
from identity_materialization import assert_conserved
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from stack_knockout_conservation import StackBoardMaterialState
from top_prize_physical_bridge import (
    TopPrizePhysicalState,
    actual_joint_groups,
    belief_truth_probability,
)
from typed_search_target_allocator import DemandChannel, TypedTargetAction


@dataclass(frozen=True)
class HiddenDirectBenchTrainerTransition:
    trainer_transaction: DirectBenchTrainerTransaction
    physical_before: SearchableDeckPhysicalState
    physical_after_search: SearchableDeckPhysicalState
    physical_after: TopPrizePhysicalState
    state_after: DirectBenchTrainerExecutionState
    beliefs_after: ObserverTopPrizeBeliefs
    selected_target_index: int


def _selected_single_target(
    targets: Sequence[DirectBenchTarget],
    action: TypedTargetAction,
) -> tuple[int, DirectBenchTarget]:
    bound = tuple(targets)
    if len(action.target_cost) != len(bound):
        raise ValueError("target_cost length does not match direct-Bench targets")
    if sum(action.target_cost) != 1:
        raise ValueError("hidden direct-Bench bridge currently requires one target")
    selected = [
        (index, target)
        for index, (target, cost) in enumerate(zip(bound, action.target_cost))
        if cost == 1
    ]
    if len(selected) != 1 or any(cost not in {0, 1} for cost in action.target_cost):
        raise ValueError("single-target action must consume one exact target copy")
    return selected[0]


def execute_hidden_direct_bench_trainer_transaction(
    physical: SearchableDeckPhysicalState,
    state: DirectBenchTrainerExecutionState,
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    profile: DirectBenchSearchProfile,
    action_card_class: str,
    demands: Sequence[DemandChannel],
    targets: Sequence[DirectBenchTarget],
    search_action: TypedTargetAction,
    placements: Sequence[DirectBenchPlacement],
    target_probability_by_composition: TargetSelectionPolicy,
    observed_target: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    sampled_top_card_class: str,
    sampled_top_card_name: str,
    sampled_top_instance_id: str,
    play_condition_met: bool | None = None,
) -> HiddenDirectBenchTrainerTransition:
    """Execute one public single-target direct-Bench Trainer search and shuffle."""

    if physical.ledger != state.material.ledger:
        raise ValueError("hidden and board states must share one physical ledger")
    if not prizes_by_observer:
        raise ValueError("at least one observer is required")

    selected_index, selected = _selected_single_target(targets, search_action)
    groups = prizes_by_observer[0][1].positions.groups
    for _observer_id, prizes in prizes_by_observer:
        if prizes.positions.groups != groups:
            raise ValueError("all observers must use the same modeled groups")
        if prizes.face_up != physical.face_up:
            raise ValueError("observer Prize visibility disagrees with physical state")

    exact_counts = actual_prize_group_counts(
        physical,
        group_by_card_class,
        groups,
    )
    pre_pool_counts, pre_pool_size = deck_prize_pool_profile(
        physical,
        group_by_card_class,
        groups,
    )
    target_group = group_by_card_class.get(selected.search_target.card_class)
    beliefs = resolve_revealed_search_target_shuffle(
        prizes_by_observer,
        actor_id=actor_id,
        actor_exact_prize_counts=exact_counts,
        target_probability_by_composition=target_probability_by_composition,
        observed_target=observed_target,
        observed_target_group=target_group,
        pre_search_group_pool_counts=pre_pool_counts,
        pre_search_pool_size=pre_pool_size,
    )

    transaction = execute_direct_bench_trainer_transaction(
        state,
        profile,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        placements=placements,
        play_condition_met=play_condition_met,
    )
    after_search = SearchableDeckPhysicalState(
        transaction.after.material.ledger,
        physical.prize_instance_ids,
        physical.face_up,
    )

    after_counts, after_size = deck_prize_pool_profile(
        after_search,
        group_by_card_class,
        groups,
    )
    expected_counts = dict(pre_pool_counts)
    if target_group is not None:
        expected_counts[target_group] -= 1
    if after_counts != expected_counts or after_size != pre_pool_size - 1:
        raise AssertionError(
            "direct-Bench movement disagrees with hidden-state pool update"
        )

    next_physical = finish_shuffle_with_sampled_top(
        after_search,
        card_class=sampled_top_card_class,
        card_name=sampled_top_card_name,
        instance_id=sampled_top_instance_id,
    )
    assert_conserved(physical.ledger, next_physical.ledger)

    board = transaction.after.material.board
    material = StackBoardMaterialState(next_physical.ledger, board)
    state_after = DirectBenchTrainerExecutionState(
        material=material,
        budget=transaction.after.budget,
        channels=transaction.after.channels,
    )

    top_group, prize_groups = actual_joint_groups(
        next_physical,
        group_by_card_class,
    )
    for observer_id, belief in beliefs.beliefs:
        if belief_truth_probability(
            belief,
            top_group=top_group,
            prize_groups=prize_groups,
        ) <= 0.0:
            raise AssertionError(
                f"observer {observer_id!r} assigns zero probability "
                "to exact post-transaction truth"
            )

    return HiddenDirectBenchTrainerTransition(
        trainer_transaction=transaction,
        physical_before=physical,
        physical_after_search=after_search,
        physical_after=next_physical,
        state_after=state_after,
        beliefs_after=beliefs,
        selected_target_index=selected_index,
    )



@dataclass(frozen=True)
class HiddenMultiDirectBenchTrainerTransition:
    trainer_transaction: DirectBenchTrainerTransaction
    physical_before: SearchableDeckPhysicalState
    physical_after_search: SearchableDeckPhysicalState
    physical_after: TopPrizePhysicalState
    state_after: DirectBenchTrainerExecutionState
    beliefs_after: ObserverTopPrizeBeliefs
    selected_target_indices: tuple[int, ...]


def execute_hidden_multi_direct_bench_trainer_transaction(
    physical: SearchableDeckPhysicalState,
    state: DirectBenchTrainerExecutionState,
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    profile: DirectBenchSearchProfile,
    action_card_class: str,
    demands: Sequence[DemandChannel],
    targets: Sequence[DirectBenchTarget],
    search_action: TypedTargetAction,
    placements: Sequence[DirectBenchPlacement],
    target_probability_by_composition: TargetSelectionPolicy,
    observed_target: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    sampled_top_card_class: str,
    sampled_top_card_name: str,
    sampled_top_instance_id: str,
    play_condition_met: bool | None = None,
) -> HiddenMultiDirectBenchTrainerTransition:
    """Execute a public multi-target direct-Bench Trainer search and shuffle."""

    if physical.ledger != state.material.ledger:
        raise ValueError("hidden and board states must share one physical ledger")
    if not prizes_by_observer:
        raise ValueError("at least one observer is required")

    bound = tuple(targets)
    if len(search_action.target_cost) != len(bound):
        raise ValueError("target_cost length does not match direct-Bench targets")
    if any(cost < 0 for cost in search_action.target_cost):
        raise ValueError("target_cost cannot be negative")
    selected_indices = tuple(
        index
        for index, cost in enumerate(search_action.target_cost)
        for _ in range(cost)
    )
    if not selected_indices:
        raise ValueError("multi-target hidden bridge requires at least one target")

    groups = prizes_by_observer[0][1].positions.groups
    for _observer_id, prizes in prizes_by_observer:
        if prizes.positions.groups != groups:
            raise ValueError("all observers must use the same modeled groups")
        if prizes.face_up != physical.face_up:
            raise ValueError("observer Prize visibility disagrees with physical state")

    exact_counts = actual_prize_group_counts(
        physical,
        group_by_card_class,
        groups,
    )
    pre_pool_counts, pre_pool_size = deck_prize_pool_profile(
        physical,
        group_by_card_class,
        groups,
    )
    removed_groups = tuple(
        group_by_card_class.get(bound[index].search_target.card_class)
        for index in selected_indices
    )
    beliefs = resolve_revealed_search_targets_shuffle(
        prizes_by_observer,
        actor_id=actor_id,
        actor_exact_prize_counts=exact_counts,
        target_probability_by_composition=target_probability_by_composition,
        observed_target=observed_target,
        removed_target_groups=removed_groups,
        pre_search_group_pool_counts=pre_pool_counts,
        pre_search_pool_size=pre_pool_size,
    )

    transaction = execute_direct_bench_trainer_transaction(
        state,
        profile,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        placements=placements,
        play_condition_met=play_condition_met,
    )
    after_search = SearchableDeckPhysicalState(
        transaction.after.material.ledger,
        physical.prize_instance_ids,
        physical.face_up,
    )

    after_counts, after_size = deck_prize_pool_profile(
        after_search,
        group_by_card_class,
        groups,
    )
    expected_counts = dict(pre_pool_counts)
    for target_group in removed_groups:
        if target_group is not None:
            expected_counts[target_group] -= 1
    if (
        after_counts != expected_counts
        or after_size != pre_pool_size - len(selected_indices)
    ):
        raise AssertionError(
            "multi-target direct-Bench movement disagrees with hidden-state pool update"
        )

    next_physical = finish_shuffle_with_sampled_top(
        after_search,
        card_class=sampled_top_card_class,
        card_name=sampled_top_card_name,
        instance_id=sampled_top_instance_id,
    )
    assert_conserved(physical.ledger, next_physical.ledger)

    material = StackBoardMaterialState(
        next_physical.ledger,
        transaction.after.material.board,
    )
    state_after = DirectBenchTrainerExecutionState(
        material=material,
        budget=transaction.after.budget,
        channels=transaction.after.channels,
    )

    top_group, prize_groups = actual_joint_groups(
        next_physical,
        group_by_card_class,
    )
    for observer_id, belief in beliefs.beliefs:
        if belief_truth_probability(
            belief,
            top_group=top_group,
            prize_groups=prize_groups,
        ) <= 0.0:
            raise AssertionError(
                f"observer {observer_id!r} assigns zero probability "
                "to exact post-transaction truth"
            )

    return HiddenMultiDirectBenchTrainerTransition(
        trainer_transaction=transaction,
        physical_before=physical,
        physical_after_search=after_search,
        physical_after=next_physical,
        state_after=state_after,
        beliefs_after=beliefs,
        selected_target_indices=selected_indices,
    )
