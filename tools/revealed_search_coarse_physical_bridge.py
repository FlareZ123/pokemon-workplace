"""Compose a physically exact revealed Trainer search with coarse observer evidence.

The physical transaction stays authoritative for the selected card's identity,
payment, Prize truth, and shuffled top. An observer whose modeled public label
merges different exact target groups retains their selected target as latent.
This semantic island uses exact-print identity groups as observable fine labels.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from card_class_namespace import CardClassNamespace
from deck_search_shuffle_physical_belief import (
    actual_prize_group_counts,
    deck_prize_pool_profile,
)
from deck_search_shuffle_topology import SearchableDeckPhysicalState
from deck_search_target_signal import TargetSelectionPolicy
from discard_cost_witness import DiscardCandidate, DiscardSelection
from private_search_latent_target_belief import ObserverLatentPrivateTargetBeliefs
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from revealed_target_coarsening import resolve_coarse_revealed_search_for_observers
from revealed_target_identity import public_reveal_label
from search_zone_transition import SearchZoneTarget
from top_prize_physical_bridge import actual_joint_groups
from trainer_search_hidden_state_bridge import (
    HiddenTrainerSearchTransition,
    execute_hidden_trainer_search_transaction,
)
from trainer_search_profile_compiler import CompiledTrainerSearchProfile
from trainer_search_transaction import TrainerSearchExecutionState
from typed_search_target_allocator import DemandChannel, TypedTargetAction

if TYPE_CHECKING:
    from card_identity import IdentityIndex


@dataclass(frozen=True)
class CoarseRevealedPhysicalSearchTransition:
    exact_transaction: HiddenTrainerSearchTransition
    observer_beliefs: ObserverLatentPrivateTargetBeliefs
    observed_public_label: str
    exact_target_group: str


def execute_coarse_revealed_trainer_search(
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
    public_label_by_target: Mapping[str, str],
    observed_public_label: str,
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
    print_identity_index: IdentityIndex | None = None,
) -> CoarseRevealedPhysicalSearchTransition:
    """One exact-print Trainer search, with observer-specific coarse beliefs."""
    if not prizes_by_observer:
        raise ValueError("at least one observer is required")
    matched = tuple(
        target for target, number in zip(targets, search_action.target_cost)
        if number
    )
    if (
        len(search_action.target_cost) != len(targets)
        or sum(search_action.target_cost) != 1
        or len(matched) != 1
        or any(number not in (0, 1) for number in search_action.target_cost)
    ):
        raise ValueError("one exact selected search target required")

    selected_target = matched[0]
    target_group = group_by_card_class.get(selected_target.card_class)
    if target_group is None:
        raise ValueError("selected target group must be explicitly modeled")

    actor_prizes = tuple(
        row for row in prizes_by_observer if row[0] == actor_id
    )
    if len(actor_prizes) != 1:
        raise ValueError("actor must have exactly one prior")

    groups = prizes_by_observer[0][1].positions.groups
    actor_exact_counts = actual_prize_group_counts(
        physical, group_by_card_class, groups
    )
    pool_counts, pool_size = deck_prize_pool_profile(
        physical, group_by_card_class, groups
    )
    # Materially execute the exact search under the actor's full observation.
    # The fine policy uses the exact-print group as its public label.
    exact = execute_hidden_trainer_search_transaction(
        physical,
        execution_state,
        actor_prizes,
        actor_id=actor_id,
        profile=profile,
        action_card_class=action_card_class,
        demands=demands,
        targets=targets,
        search_action=search_action,
        target_probability_by_composition=target_probability_by_composition,
        observed_target=target_group,
        group_by_card_class=group_by_card_class,
        target_card_name=target_card_name,
        target_instance_id=target_instance_id,
        sampled_top_card_class=sampled_top_card_class,
        sampled_top_card_name=sampled_top_card_name,
        sampled_top_instance_id=sampled_top_instance_id,
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=play_condition_met,
        pay_optional_discard=pay_optional_discard,
        observation_namespace=CardClassNamespace.EXACT_PRINT,
        print_identity_index=print_identity_index,
    )

    actual_target = exact.physical_after.ledger.instance(target_instance_id)
    exact_label = public_reveal_label(
        actual_target, CardClassNamespace.EXACT_PRINT
    )
    if exact_label != target_group:
        raise ValueError("exact-print target group disagrees with material ID")

    beliefs = resolve_coarse_revealed_search_for_observers(
        prizes_by_observer,
        actor_id=actor_id,
        actor_exact_prize_counts=actor_exact_counts,
        actor_selected_target_group=target_group,
        target_probability_by_composition=target_probability_by_composition,
        public_label_by_target=public_label_by_target,
        observed_public_label=observed_public_label,
        pre_search_group_pool_counts=pool_counts,
        pre_search_pool_size=pool_size,
    )

    top_group, prize_groups = actual_joint_groups(
        exact.physical_after, group_by_card_class
    )
    for observer_id, belief in beliefs.beliefs:
        truth_support = sum(
            probability
            for (observed_top, observed_prizes, latent_target), probability
            in belief.masses
            if (
                observed_top == top_group
                and observed_prizes == prize_groups
                and latent_target == target_group
            )
        )
        if truth_support <= 0.0:
            raise AssertionError(
                f"observer {observer_id!r} rejects exact physical world"
            )

    return CoarseRevealedPhysicalSearchTransition(
        exact_transaction=exact,
        observer_beliefs=beliefs,
        observed_public_label=observed_public_label,
        exact_target_group=target_group,
    )
