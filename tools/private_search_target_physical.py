"""Physical bridge for a private arbitrary-card search followed by shuffle."""

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
from deck_search_target_signal_physical import move_exact_search_target_to_hand
from identity_materialization import assert_conserved
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from private_search_target_belief import (
    PrivateTargetPolicy,
    resolve_private_search_target_shuffle_for_observers,
)
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from top_prize_physical_bridge import (
    TopPrizePhysicalState,
    actual_joint_groups,
    belief_truth_probability,
)


@dataclass(frozen=True)
class PhysicalPrivateSearchShuffleTransition:
    physical_before: SearchableDeckPhysicalState
    physical_after_target: SearchableDeckPhysicalState
    physical_after: TopPrizePhysicalState
    beliefs_after: ObserverTopPrizeBeliefs
    target_instance_id: str
    actor_exact_prize_counts: tuple[tuple[str, int], ...]
    pre_search_group_pool_counts: tuple[tuple[str, int], ...]
    pre_search_pool_size: int


def resolve_physical_private_search_shuffle(
    physical: SearchableDeckPhysicalState,
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    target_probability_by_composition: PrivateTargetPolicy,
    group_by_card_class: Mapping[str, PrizeGroup],
    target_card_class: str,
    target_card_name: str,
    target_instance_id: str,
    sampled_top_card_class: str,
    sampled_top_card_name: str,
    sampled_top_instance_id: str,
) -> PhysicalPrivateSearchShuffleTransition:
    """Move one exact private target while preserving observer-relative beliefs."""

    if not prizes_by_observer:
        raise ValueError("at least one observer is required")
    groups = prizes_by_observer[0][1].positions.groups
    for _observer_id, prizes in prizes_by_observer:
        if prizes.positions.groups != groups:
            raise ValueError("all observers must use the same modeled groups")
        if prizes.face_up != physical.face_up:
            raise ValueError("observer Prize visibility disagrees with physical state")

    exact_counts = actual_prize_group_counts(
        physical, group_by_card_class, groups
    )
    pre_pool_counts, pre_pool_size = deck_prize_pool_profile(
        physical, group_by_card_class, groups
    )
    target_group = group_by_card_class.get(target_card_class)

    beliefs = resolve_private_search_target_shuffle_for_observers(
        prizes_by_observer,
        actor_id=actor_id,
        actor_exact_prize_counts=exact_counts,
        actor_selected_target_group=target_group,
        pre_search_group_pool_counts=pre_pool_counts,
        pre_search_pool_size=pre_pool_size,
        target_probability_by_composition=target_probability_by_composition,
    )

    after_target = move_exact_search_target_to_hand(
        physical,
        card_class=target_card_class,
        card_name=target_card_name,
        instance_id=target_instance_id,
    )
    after_counts, after_size = deck_prize_pool_profile(
        after_target, group_by_card_class, groups
    )
    expected_counts = dict(pre_pool_counts)
    if target_group is not None:
        expected_counts[target_group] -= 1
    if after_counts != expected_counts or after_size != pre_pool_size - 1:
        raise AssertionError(
            "private target movement disagrees with exact physical pool update"
        )

    next_physical = finish_shuffle_with_sampled_top(
        after_target,
        card_class=sampled_top_card_class,
        card_name=sampled_top_card_name,
        instance_id=sampled_top_instance_id,
    )
    assert_conserved(physical.ledger, next_physical.ledger)

    top_group, prize_groups = actual_joint_groups(
        next_physical, group_by_card_class
    )
    for observer_id, belief in beliefs.beliefs:
        if belief_truth_probability(
            belief, top_group=top_group, prize_groups=prize_groups
        ) <= 0.0:
            raise AssertionError(
                f"observer {observer_id!r} assigns zero probability "
                "to exact post-private-search truth"
            )

    return PhysicalPrivateSearchShuffleTransition(
        physical_before=physical,
        physical_after_target=after_target,
        physical_after=next_physical,
        beliefs_after=beliefs,
        target_instance_id=target_instance_id,
        actor_exact_prize_counts=tuple((group, exact_counts[group]) for group in groups),
        pre_search_group_pool_counts=tuple((group, pre_pool_counts[group]) for group in groups),
        pre_search_pool_size=pre_pool_size,
    )
