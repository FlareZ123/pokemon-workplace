"""Belief transition for a full deck inspection followed by shuffle.

The searcher's deck inspection can collapse Prize-composition uncertainty while
other observers keep their prior. The next deck-top identity is sampled from
the remaining deck conditional on each Prize state, preserving correlation.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_position_belief import PrizeGroup, PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from prize_top_swap_belief import TopPrizeJointBelief


def condition_prize_composition(
    state: PrizeSlotVisibilityBelief,
    exact_group_counts: Mapping[str, int],
) -> PrizeSlotVisibilityBelief:
    """Condition one observer on the exact grouped Prize composition."""

    groups = state.positions.groups
    if set(exact_group_counts) != set(groups):
        raise ValueError("exact_group_counts must cover every modeled group")
    if any(count < 0 for count in exact_group_counts.values()):
        raise ValueError("exact group counts must be non-negative")
    if sum(exact_group_counts.values()) > state.positions.prize_count:
        raise ValueError("modeled Prize counts exceed the Prize count")

    target = tuple(exact_group_counts[group] for group in groups)
    kept = []
    total = 0.0
    for prize_state, probability in state.positions.masses:
        composition = tuple(
            sum(value == group for value in prize_state)
            for group in groups
        )
        if composition != target:
            continue
        kept.append((prize_state, probability))
        total += probability

    if total == 0.0:
        raise ValueError("exact Prize composition has zero prior probability")

    conditioned = PrizePositionBelief(
        groups,
        state.positions.prize_count,
        tuple(
            (prize_state, probability / total)
            for prize_state, probability in kept
        ),
    )
    return PrizeSlotVisibilityBelief(conditioned, state.face_up)


def post_shuffle_top_prize_belief(
    prizes: PrizeSlotVisibilityBelief,
    *,
    group_pool_counts: Mapping[str, int],
    pool_size: int,
) -> TopPrizeJointBelief:
    """Sample the new top card conditionally on every possible Prize state.

    pool_size is the number of cards currently distributed between the
    unordered deck and Prize zone. group_pool_counts gives the corresponding
    modeled-group counts in that same pool. Visible cards already removed from
    the deck must therefore be excluded by the caller.
    """

    groups = prizes.positions.groups
    prize_count = prizes.positions.prize_count

    if set(group_pool_counts) != set(groups):
        raise ValueError("group_pool_counts must cover every modeled group")
    if pool_size <= prize_count:
        raise ValueError("pool_size must leave at least one card in deck")
    if any(count < 0 for count in group_pool_counts.values()):
        raise ValueError("group pool counts must be non-negative")
    if sum(group_pool_counts.values()) > pool_size:
        raise ValueError("modeled group counts exceed pool_size")

    filler_pool = pool_size - sum(group_pool_counts.values())
    deck_size = pool_size - prize_count
    output: dict[
        tuple[PrizeGroup, tuple[PrizeGroup, ...]],
        float,
    ] = defaultdict(float)

    for prize_state, prize_probability in prizes.positions.masses:
        prized_counts = {
            group: sum(value == group for value in prize_state)
            for group in groups
        }
        filler_prized = sum(value is None for value in prize_state)

        deck_counts = {
            group: group_pool_counts[group] - prized_counts[group]
            for group in groups
        }
        filler_deck = filler_pool - filler_prized
        if any(count < 0 for count in deck_counts.values()) or filler_deck < 0:
            raise ValueError(
                "Prize belief contains a state impossible under pool counts"
            )
        if sum(deck_counts.values()) + filler_deck != deck_size:
            raise ValueError("Prize state and pool counts do not conserve deck size")

        for group, count in deck_counts.items():
            if count:
                output[(group, prize_state)] += (
                    prize_probability * count / deck_size
                )
        if filler_deck:
            output[(None, prize_state)] += (
                prize_probability * filler_deck / deck_size
            )

    return TopPrizeJointBelief(
        groups,
        prizes.face_up,
        tuple(sorted(output.items(), key=lambda row: repr(row[0]))),
    )


def resolve_full_search_shuffle_for_observers(
    prizes_by_observer: Sequence[tuple[str, PrizeSlotVisibilityBelief]],
    *,
    actor_id: str,
    actor_exact_prize_counts: Mapping[str, int],
    group_pool_counts: Mapping[str, int],
    pool_size: int,
) -> ObserverTopPrizeBeliefs:
    """Apply private full-deck inspection and public shuffle topology.

    The actor conditions on the exact Prize composition learned from inspecting
    their remaining deck. Other observers retain their existing Prize prior.
    Every observer then receives a new joint top/Prize belief whose top-card
    distribution is conditional on that observer's possible Prize states.
    """

    if not prizes_by_observer:
        raise ValueError("at least one observer is required")
    observer_ids = tuple(observer_id for observer_id, _ in prizes_by_observer)
    if len(observer_ids) != len(set(observer_ids)):
        raise ValueError("observer IDs must be unique")
    if actor_id not in observer_ids:
        raise ValueError("actor_id must identify an observer")

    updated = []
    for observer_id, prizes in prizes_by_observer:
        if observer_id == actor_id:
            prizes = condition_prize_composition(
                prizes,
                actor_exact_prize_counts,
            )
        updated.append(
            (
                observer_id,
                post_shuffle_top_prize_belief(
                    prizes,
                    group_pool_counts=group_pool_counts,
                    pool_size=pool_size,
                ),
            )
        )

    return ObserverTopPrizeBeliefs(tuple(updated))
