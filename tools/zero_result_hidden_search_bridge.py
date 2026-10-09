"""Physically paid restricted Trainer search that reveals no selected target.

Some search effects permit choosing zero cards. A paid zero-result search still
inspects the deck and shuffles; the actor learns exact Prize composition and
the public no-target outcome can signal hidden state without removing a target
from the remaining deck-plus-Prize pool.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from deck_search_shuffle_belief import (
    condition_prize_composition,
    post_shuffle_top_prize_belief,
)
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
    condition_on_revealed_search_target,
)
from discard_cost_witness import DiscardCandidate, DiscardSelection
from identity_materialization import IdentityLedger, assert_conserved
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
    execute_trainer_retrieval_transaction,
)
from typed_search_retrieval import TypedRetrievalAction


NO_TARGET_OBSERVATION = "NO_TARGET"


@dataclass(frozen=True)
class ZeroResultHiddenSearchTransition:
    trainer_transaction: TrainerSearchTransaction
    physical_before: SearchableDeckPhysicalState
    physical_after_search: SearchableDeckPhysicalState
    physical_after: TopPrizePhysicalState
    beliefs_after: ObserverTopPrizeBeliefs


def execute_paid_zero_result_search(
    physical: SearchableDeckPhysicalState,
    execution_state: TrainerSearchExecutionState,
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    profile: CompiledTrainerSearchProfile,
    action_card_class: str,
    targets: Sequence[SearchZoneTarget],
    target_probability_by_composition: TargetSelectionPolicy,
    group_by_card_class: Mapping[str, PrizeGroup],
    sampled_top_card_class: str,
    sampled_top_card_name: str,
    sampled_top_instance_id: str,
    discard_candidates: Sequence[DiscardCandidate],
    discard_selection: DiscardSelection,
    play_condition_met: bool | None = None,
) -> ZeroResultHiddenSearchTransition:
    """Pay, search, select no card, learn K1, reveal empty result, shuffle."""
    if execution_state.zones != physical.ledger.exchangeable:
        raise ValueError("execution zones disagree with physical ledger")
    if any(
        instance.zone in {"deck", "hand", "resolving_trainer"}
        for instance in physical.ledger.instances
    ):
        raise ValueError("deck and hand must be exchangeable before search")
    if profile.required_discard_other_cards <= 0:
        raise ValueError("zero-result island requires a mandatory discard")
    if profile.discards_entire_hand or profile.conditional_outputs:
        raise ValueError("zero-result island excludes extra output side effects")
    if not prizes_by_observer:
        raise ValueError("at least one observer is required")
    ids = tuple(observer_id for observer_id, _ in prizes_by_observer)
    if len(ids) != len(set(ids)) or actor_id not in ids:
        raise ValueError("observer IDs must be unique and include actor")

    groups = prizes_by_observer[0][1].positions.groups
    for _, prior in prizes_by_observer:
        if prior.positions.groups != groups or prior.face_up != physical.face_up:
            raise ValueError("observer Prize groups and visibility must agree")

    actor_prizes = actual_prize_group_counts(
        physical, group_by_card_class, groups
    )
    pool_counts, pool_size = deck_prize_pool_profile(
        physical, group_by_card_class, groups
    )
    actor_key = tuple(actor_prizes[group] for group in groups)
    if target_probability_by_composition.get(actor_key, {}).get(
        NO_TARGET_OBSERVATION, 0.0
    ) <= 0.0:
        raise ValueError("actor no-target outcome impossible under policy")

    action = TypedRetrievalAction(
        target_cost=(0,) * len(targets),
        axis_usage=(0,) * len(profile.base_outputs),
    )
    transaction = execute_trainer_retrieval_transaction(
        execution_state,
        profile=profile,
        action_card_class=action_card_class,
        targets=targets,
        retrieval_action=action,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
    )
    if transaction.discard_cost <= 0:
        raise AssertionError("zero-result paid search did not change state")

    post_search = SearchableDeckPhysicalState(
        IdentityLedger(transaction.after.zones, physical.ledger.instances),
        physical.prize_instance_ids,
        physical.face_up,
    )
    after_pool_counts, after_pool_size = deck_prize_pool_profile(
        post_search, group_by_card_class, groups
    )
    if after_pool_counts != pool_counts or after_pool_size != pool_size:
        raise AssertionError("zero-result search moved a hidden deck card")

    updated = []
    for observer_id, prior in prizes_by_observer:
        if observer_id == actor_id:
            conditioned = condition_prize_composition(prior, actor_prizes)
        else:
            conditioned = condition_on_revealed_search_target(
                prior,
                target_probability_by_composition=target_probability_by_composition,
                observed_target=NO_TARGET_OBSERVATION,
            )
        updated.append((
            observer_id,
            post_shuffle_top_prize_belief(
                conditioned,
                group_pool_counts=pool_counts,
                pool_size=pool_size,
            ),
        ))
    beliefs = ObserverTopPrizeBeliefs(tuple(updated))

    next_physical = finish_shuffle_with_sampled_top(
        post_search,
        card_class=sampled_top_card_class,
        card_name=sampled_top_card_name,
        instance_id=sampled_top_instance_id,
    )
    assert_conserved(physical.ledger, next_physical.ledger)
    actual_top, actual_prizes = actual_joint_groups(
        next_physical, group_by_card_class
    )
    for observer_id, belief in beliefs.beliefs:
        if belief_truth_probability(
            belief,
            top_group=actual_top,
            prize_groups=actual_prizes,
        ) <= 0.0:
            raise AssertionError(
                f"observer {observer_id!r} rejects the exact physical state"
            )

    return ZeroResultHiddenSearchTransition(
        transaction,
        physical,
        post_search,
        next_physical,
        beliefs,
    )
