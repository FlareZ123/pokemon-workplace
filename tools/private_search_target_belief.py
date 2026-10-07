"""Belief transition for a private unrestricted search target followed by shuffle.

A private target leaves the deck physically while other observers do not learn
its identity. Their post-shuffle top distribution must therefore marginalize
over target-selection policy instead of using one exact post-search pool.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from math import isclose

from deck_search_shuffle_belief import condition_prize_composition
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from prize_top_swap_belief import TopPrizeJointBelief


PrizeComposition = tuple[int, ...]
PrivateTargetPolicy = Mapping[PrizeComposition, Mapping[PrizeGroup, float]]


def _composition(state: tuple[PrizeGroup, ...], groups: Sequence[str]) -> PrizeComposition:
    return tuple(sum(value == group for value in state) for group in groups)


def post_private_search_top_prize_belief(
    prizes: PrizeSlotVisibilityBelief,
    *,
    pre_search_group_pool_counts: Mapping[str, int],
    pre_search_pool_size: int,
    target_probability_by_composition: PrivateTargetPolicy,
) -> TopPrizeJointBelief:
    """Marginalize a hidden searched-card identity before sampling shuffled top."""

    groups = prizes.positions.groups
    prize_count = prizes.positions.prize_count
    if set(pre_search_group_pool_counts) != set(groups):
        raise ValueError("pool counts must cover every modeled group")
    if pre_search_pool_size <= prize_count + 1:
        raise ValueError("private search must leave at least one card in deck")
    if sum(pre_search_group_pool_counts.values()) > pre_search_pool_size:
        raise ValueError("modeled pool counts exceed pool size")

    filler_pool = pre_search_pool_size - sum(pre_search_group_pool_counts.values())
    output: dict[tuple[PrizeGroup, tuple[PrizeGroup, ...]], float] = defaultdict(float)

    for prize_state, prize_probability in prizes.positions.masses:
        composition = _composition(prize_state, groups)
        if composition not in target_probability_by_composition:
            raise ValueError("private target policy must cover every supported Prize composition")
        policy = target_probability_by_composition[composition]
        if not policy:
            raise ValueError("private target policy rows must be non-empty")
        if any(probability < 0.0 or probability > 1.0 for probability in policy.values()):
            raise ValueError("target probabilities must lie in [0, 1]")
        if not isclose(sum(policy.values()), 1.0, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError("target probabilities must sum to one")

        prized_counts = {
            group: sum(value == group for value in prize_state)
            for group in groups
        }
        filler_prized = sum(value is None for value in prize_state)
        deck_counts = {
            group: pre_search_group_pool_counts[group] - prized_counts[group]
            for group in groups
        }
        filler_deck = filler_pool - filler_prized
        if any(value < 0 for value in deck_counts.values()) or filler_deck < 0:
            raise ValueError("Prize state is impossible under pre-search pool")

        deck_size = pre_search_pool_size - prize_count
        if sum(deck_counts.values()) + filler_deck != deck_size:
            raise AssertionError("deck counts do not conserve pool size")

        for target_group, target_probability in policy.items():
            if target_probability == 0.0:
                continue
            if target_group is None:
                available = filler_deck
            else:
                if target_group not in deck_counts:
                    raise ValueError("target policy contains an unknown modeled group")
                available = deck_counts[target_group]
            if available <= 0:
                raise ValueError("target policy assigns mass to a group absent from deck")

            after_counts = dict(deck_counts)
            after_filler = filler_deck
            if target_group is None:
                after_filler -= 1
            else:
                after_counts[target_group] -= 1

            remaining = deck_size - 1
            for top_group, count in after_counts.items():
                if count:
                    output[(top_group, prize_state)] += (
                        prize_probability * target_probability * count / remaining
                    )
            if after_filler:
                output[(None, prize_state)] += (
                    prize_probability * target_probability * after_filler / remaining
                )

    return TopPrizeJointBelief(
        groups, prizes.face_up, tuple(sorted(output.items(), key=lambda row: repr(row[0])))
    )


def resolve_private_search_target_shuffle_for_observers(
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    actor_exact_prize_counts: Mapping[str, int],
    actor_selected_target_group: PrizeGroup,
    pre_search_group_pool_counts: Mapping[str, int],
    pre_search_pool_size: int,
    target_probability_by_composition: PrivateTargetPolicy,
) -> ObserverTopPrizeBeliefs:
    """Give the actor exact K1/target knowledge and marginalize target for others."""

    if not prizes_by_observer:
        raise ValueError("at least one observer is required")
    ids = tuple(observer_id for observer_id, _ in prizes_by_observer)
    if len(ids) != len(set(ids)):
        raise ValueError("observer IDs must be unique")
    if actor_id not in ids:
        raise ValueError("actor_id must identify an observer")

    reference = prizes_by_observer[0][1]
    groups = reference.positions.groups
    for _observer_id, prizes in prizes_by_observer:
        if prizes.positions.groups != groups or prizes.face_up != reference.face_up:
            raise ValueError("observers must share public Prize geometry")

    actor_key = tuple(actor_exact_prize_counts[group] for group in groups)
    actor_row = target_probability_by_composition.get(actor_key)
    if actor_row is None or actor_row.get(actor_selected_target_group, 0.0) <= 0.0:
        raise ValueError("actor selected target has zero probability under policy")

    updated = []
    for observer_id, prizes in prizes_by_observer:
        if observer_id == actor_id:
            exact = condition_prize_composition(prizes, actor_exact_prize_counts)
            policy: PrivateTargetPolicy = {actor_key: {actor_selected_target_group: 1.0}}
            belief = post_private_search_top_prize_belief(
                exact,
                pre_search_group_pool_counts=pre_search_group_pool_counts,
                pre_search_pool_size=pre_search_pool_size,
                target_probability_by_composition=policy,
            )
        else:
            belief = post_private_search_top_prize_belief(
                prizes,
                pre_search_group_pool_counts=pre_search_group_pool_counts,
                pre_search_pool_size=pre_search_pool_size,
                target_probability_by_composition=target_probability_by_composition,
            )
        updated.append((observer_id, belief))

    return ObserverTopPrizeBeliefs(tuple(updated))
