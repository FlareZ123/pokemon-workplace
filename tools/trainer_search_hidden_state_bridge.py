"""Compose atomic Trainer search execution with hidden-state updates."""

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
)
from discard_cost_witness import DiscardCandidate, DiscardSelection
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
)
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from search_zone_transition import SearchZoneTarget
from top_prize_physical_bridge import (
    TopPrizePhysicalState,
    actual_joint_groups,
    belief_truth_probability,
)
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    TrainerSearchTransaction,
    execute_trainer_search_transaction,
)
from typed_search_target_allocator import DemandChannel, TypedTargetAction


@dataclass(frozen=True)
class HiddenTrainerSearchTransition:
    """Atomic Trainer execution plus exact hidden-state consequences."""

    trainer_transaction: TrainerSearchTransaction
    physical_before: SearchableDeckPhysicalState
    physical_after_search: SearchableDeckPhysicalState
    physical_after: TopPrizePhysicalState
    beliefs_after: ObserverTopPrizeBeliefs
    selected_target_index: int
    target_instance_id: str


def _selected_single_target(
    targets: Sequence[SearchZoneTarget],
    action: TypedTargetAction,
) -> tuple[int, SearchZoneTarget]:
    bound_targets = tuple(targets)
    if len(action.target_cost) != len(bound_targets):
        raise ValueError("target_cost length does not match targets")
    if sum(action.target_cost) != 1:
        raise ValueError("hidden-state bridge currently requires one searched card")

    selected = [
        (index, target)
        for index, (target, cost) in enumerate(
            zip(bound_targets, action.target_cost)
        )
        if cost == 1
    ]
    if len(selected) != 1 or any(
        cost not in {0, 1}
        for cost in action.target_cost
    ):
        raise ValueError("single-target action must consume one exact target copy")
    return selected[0]


def _require_exchangeable_search_zones(
    physical: SearchableDeckPhysicalState,
) -> None:
    conflicting = tuple(
        instance.instance_id
        for instance in physical.ledger.instances
        if instance.zone in {"deck", "hand", "resolving_trainer"}
    )
    if conflicting:
        raise ValueError(
            "bridge requires deck and hand copies to be exchangeable before search"
        )


def execute_hidden_trainer_search_transaction(
    physical: SearchableDeckPhysicalState,
    execution_state: TrainerSearchExecutionState,
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    profile: CompiledTrainerSearchProfile,
    action_card_class: str,
    demands: Sequence[DemandChannel],
    targets: Sequence[SearchZoneTarget],
    search_action: TypedTargetAction,
    target_probability_by_composition: TargetSelectionPolicy,
    observed_target: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    target_card_name: str,
    target_instance_id: str,
    sampled_top_card_class: str,
    sampled_top_card_name: str,
    sampled_top_instance_id: str,
    discard_candidates: Sequence[DiscardCandidate] = (),
    discard_selection: DiscardSelection | None = None,
    play_condition_met: bool | None = None,
    pay_optional_discard: bool | None = None,
) -> HiddenTrainerSearchTransition:
    """Execute one revealed single-target Trainer search through shuffle.

    The aggregate Trainer transaction owns play permission, turn budget,
    discard payment, and typed target legality. Exact physical Prize instances
    remain outside that exchangeable ledger. After aggregate execution, the
    publicly known searched copy is materialized in hand and the shuffled top is
    materialized from the remaining deck.
    """

    if execution_state.zones != physical.ledger.exchangeable:
        raise ValueError(
            "Trainer execution zones must equal the physical exchangeable ledger"
        )
    _require_exchangeable_search_zones(physical)

    selected_index, selected_target = _selected_single_target(
        targets,
        search_action,
    )
    # This bridge represents a publicly revealed single card. Its observation
    # is the card's identity, not an independent, freely chosen policy label.
    if observed_target != target_card_name:
        raise ValueError(
            "public revealed target must match the searched card name"
        )

    if not prizes_by_observer:
        raise ValueError("at least one observer is required")
    groups = prizes_by_observer[0][1].positions.groups
    for _observer_id, prizes in prizes_by_observer:
        if prizes.positions.groups != groups:
            raise ValueError("all observers must use the same modeled groups")
        if prizes.face_up != physical.face_up:
            raise ValueError(
                "observer Prize visibility disagrees with physical state"
            )

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
    target_group = group_by_card_class.get(selected_target.card_class)

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

    trainer_transaction = execute_trainer_search_transaction(
        execution_state,
        profile=profile,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
        pay_optional_discard=pay_optional_discard,
    )

    ledger_after_aggregate = IdentityLedger(
        trainer_transaction.after.zones,
        physical.ledger.instances,
    )
    ledger_after_search = materialize(
        ledger_after_aggregate,
        card_class=selected_target.card_class,
        card_name=target_card_name,
        source_zone="hand",
        instance_id=target_instance_id,
    )
    after_search = SearchableDeckPhysicalState(
        ledger_after_search,
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
            "Trainer search movement disagrees with hidden-state pool update"
        )

    next_physical = finish_shuffle_with_sampled_top(
        after_search,
        card_class=sampled_top_card_class,
        card_name=sampled_top_card_name,
        instance_id=sampled_top_instance_id,
    )
    assert_conserved(physical.ledger, next_physical.ledger)

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

    return HiddenTrainerSearchTransition(
        trainer_transaction=trainer_transaction,
        physical_before=physical,
        physical_after_search=after_search,
        physical_after=next_physical,
        beliefs_after=beliefs,
        selected_target_index=selected_index,
        target_instance_id=target_instance_id,
    )
