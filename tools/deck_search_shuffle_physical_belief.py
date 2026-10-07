"""Compose physical deck-search/shuffle state with observer-relative beliefs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from deck_search_shuffle_belief import resolve_full_search_shuffle_for_observers
from deck_search_shuffle_topology import (
    SearchableDeckPhysicalState,
    finish_shuffle_with_sampled_top,
)
from identity_materialization import assert_conserved
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from top_prize_physical_bridge import (
    TopPrizePhysicalState,
    actual_joint_groups,
    belief_truth_probability,
)


@dataclass(frozen=True)
class PhysicalSearchShuffleTransition:
    """One exact post-shuffle top sample plus every observer posterior."""

    physical_before: SearchableDeckPhysicalState
    physical_after: TopPrizePhysicalState
    beliefs_after: ObserverTopPrizeBeliefs
    actor_exact_prize_counts: tuple[tuple[str, int], ...]
    group_pool_counts: tuple[tuple[str, int], ...]
    pool_size: int


def actual_prize_group_counts(
    state: SearchableDeckPhysicalState,
    group_by_card_class: Mapping[str, PrizeGroup],
    groups: Sequence[str],
) -> dict[str, int]:
    """Project exact physical Prize instances into modeled group counts."""

    resolved_groups = tuple(groups)
    if len(resolved_groups) != len(set(resolved_groups)):
        raise ValueError("groups must be unique")
    modeled = set(resolved_groups)
    counts = {group: 0 for group in resolved_groups}

    for instance_id in state.prize_instance_ids:
        card_class = state.ledger.instance(instance_id).card_class
        group = group_by_card_class.get(card_class)
        if group is None:
            continue
        if group not in modeled:
            raise ValueError("group_by_card_class contains an unknown group")
        counts[group] += 1

    return counts


def deck_prize_pool_profile(
    state: SearchableDeckPhysicalState,
    group_by_card_class: Mapping[str, PrizeGroup],
    groups: Sequence[str],
) -> tuple[dict[str, int], int]:
    """Count cards currently distributed between unordered deck and Prize."""

    resolved_groups = tuple(groups)
    if len(resolved_groups) != len(set(resolved_groups)):
        raise ValueError("groups must be unique")
    modeled = set(resolved_groups)
    group_counts = {group: 0 for group in resolved_groups}
    pool_size = 0

    for card_class, zone, count in state.ledger.exchangeable.counts:
        if zone not in {"deck", "prize"}:
            continue
        pool_size += count
        group = group_by_card_class.get(card_class)
        if group is None:
            continue
        if group not in modeled:
            raise ValueError("group_by_card_class contains an unknown group")
        group_counts[group] += count

    for instance in state.ledger.instances:
        if instance.zone not in {"deck", "prize"}:
            continue
        pool_size += 1
        group = group_by_card_class.get(instance.card_class)
        if group is None:
            continue
        if group not in modeled:
            raise ValueError("group_by_card_class contains an unknown group")
        group_counts[group] += 1

    if pool_size <= len(state.prize_instance_ids):
        raise ValueError("physical state must retain at least one deck card")

    return group_counts, pool_size


def resolve_physical_full_search_shuffle(
    physical: SearchableDeckPhysicalState,
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    sampled_top_card_class: str,
    sampled_top_card_name: str,
    sampled_top_instance_id: str,
) -> PhysicalSearchShuffleTransition:
    """Advance K1 information and one exact shuffled top sample together."""

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
    pool_counts, pool_size = deck_prize_pool_profile(
        physical,
        group_by_card_class,
        groups,
    )
    beliefs = resolve_full_search_shuffle_for_observers(
        prizes_by_observer,
        actor_id=actor_id,
        actor_exact_prize_counts=exact_counts,
        group_pool_counts=pool_counts,
        pool_size=pool_size,
    )

    next_physical = finish_shuffle_with_sampled_top(
        physical,
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
                "to exact post-shuffle truth"
            )

    return PhysicalSearchShuffleTransition(
        physical,
        next_physical,
        beliefs,
        tuple((group, exact_counts[group]) for group in groups),
        tuple((group, pool_counts[group]) for group in groups),
        pool_size,
    )
