"""Exact physical Prize queue and correlated per-observer pending beliefs.

Use this bridge when a taken Prize may later reveal its identity. The older
stage_prize_takes_with_observers() projects removed IDs immediately and is
appropriate only when that marginalization cannot erase future evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from pending_prize_batch_belief import (
    ObserverPendingPrizeBatchBeliefs,
    resolve_next_pending_batch_visibility,
    stage_additional_pending_prize_front_belief,
    stage_pending_prize_batch,
)
from pending_prize_identity_belief import destination_visibility
from prize_pending_take import (
    PrizePendingTakeState,
    resolve_next_pending_prize,
    stage_additional_prize_front,
    stage_prize_takes,
)
from prize_position_belief import PrizeGroup
from top_prize_physical_bridge import (
    TopPrizePhysicalState,
    actual_joint_groups,
    belief_truth_probability,
)


@dataclass(frozen=True)
class PhysicalPendingBatchBeliefs:
    pending: PrizePendingTakeState
    observers: ObserverPendingPrizeBatchBeliefs

    def __post_init__(self) -> None:
        physical_ids = tuple(row.instance_id for row in self.pending.pending)
        belief_ids = self.observers.beliefs[0][1].pending_ids
        if physical_ids != belief_ids:
            raise ValueError("physical and belief queue orders disagree")
        for _, belief in self.observers.beliefs:
            if belief.face_up != self.pending.physical.face_up:
                raise ValueError("physical and belief Prize visibility disagrees")


def _group(
    physical: TopPrizePhysicalState,
    instance_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> PrizeGroup:
    card_class = physical.ledger.instance(instance_id).card_class
    return group_by_card_class.get(card_class)


def _assert_pending_truth(
    state: PhysicalPendingBatchBeliefs,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> None:
    physical = state.pending.physical
    top, prizes = actual_joint_groups(physical, group_by_card_class)
    pending_groups = tuple(
        _group(physical, row.instance_id, group_by_card_class)
        for row in state.pending.pending
    )
    for observer_id, belief in state.observers.beliefs:
        probability = sum(
            mass for (possible_top, possible_prizes, possible_pending), mass
            in belief.masses
            if (possible_top, possible_prizes, possible_pending)
            == (top, prizes, pending_groups)
        )
        if probability <= 0:
            raise AssertionError(
                f"observer {observer_id!r} assigns zero probability to physical truth"
            )


def stage_physical_pending_batch(
    physical: TopPrizePhysicalState,
    beliefs: ObserverTopPrizeBeliefs,
    *,
    actor_id: str,
    positions: tuple[int, ...],
    group_by_card_class: Mapping[str, PrizeGroup],
) -> PhysicalPendingBatchBeliefs:
    """Take selected original slots, retaining every unresolved identity."""
    beliefs.belief_for(actor_id)
    top, prizes = actual_joint_groups(physical, group_by_card_class)
    for observer_id, belief in beliefs.beliefs:
        if belief.face_up != physical.face_up:
            raise ValueError("physical and observer visibility disagree")
        if belief_truth_probability(
            belief, top_group=top, prize_groups=prizes,
        ) <= 0:
            raise ValueError(
                f"observer {observer_id!r} rules out exact physical truth"
            )

    pending = stage_prize_takes(physical, positions=positions)
    ids = tuple(row.instance_id for row in pending.pending)
    true_groups = {
        identifier: _group(physical, identifier, group_by_card_class)
        for identifier in ids
    }
    visible: dict[str, dict[str, PrizeGroup]] = {
        actor_id: dict(true_groups),
    }
    for observer_id, _ in beliefs.beliefs:
        for index, identifier in zip(positions, ids):
            if physical.face_up[index]:
                visible.setdefault(observer_id, {})[identifier] = true_groups[identifier]

    latent = stage_pending_prize_batch(
        beliefs, positions=positions, pending_ids=ids, visible_groups=visible,
    )
    state = PhysicalPendingBatchBeliefs(pending, latent)
    _assert_pending_truth(state, group_by_card_class)
    return state


def stage_physical_additional_pending_front(
    state: PhysicalPendingBatchBeliefs,
    *,
    actor_id: str,
    position: int,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> PhysicalPendingBatchBeliefs:
    """Mirror an additional Prize inserted at the head of the physical queue."""
    state.observers.belief_for(actor_id)
    physical = state.pending.physical
    new_pending = stage_additional_prize_front(state.pending, position=position)
    new_id = new_pending.pending[0].instance_id
    group = _group(physical, new_id, group_by_card_class)
    visible = {actor_id: group}
    if physical.face_up[position]:
        visible = {observer_id: group for observer_id, _ in state.observers.beliefs}
    latent = stage_additional_pending_prize_front_belief(
        state.observers,
        position=position,
        instance_id=new_id,
        visible_groups=visible,
    )
    result = PhysicalPendingBatchBeliefs(new_pending, latent)
    _assert_pending_truth(result, group_by_card_class)
    return result


def resolve_physical_next_pending_batch(
    state: PhysicalPendingBatchBeliefs,
    *,
    actor_id: str,
    destination_zone: str,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> PhysicalPendingBatchBeliefs:
    """Resolve one queue head with the visibility of its actual destination."""
    if not state.pending.pending:
        raise ValueError("no pending Prize card")
    state.observers.belief_for(actor_id)
    card_id = state.pending.pending[0].instance_id
    true_group = _group(state.pending.physical, card_id, group_by_card_class)
    visible = destination_visibility(
        tuple(name for name, _ in state.observers.beliefs),
        actor_id=actor_id,
        destination_zone=destination_zone,
        observed_group=true_group,
    )
    latent = resolve_next_pending_batch_visibility(
        state.observers,
        instance_id=card_id,
        visible_groups=visible,
    )
    physical_resolution = resolve_next_pending_prize(
        state.pending,
        destination_zone=destination_zone,
    )
    result = PhysicalPendingBatchBeliefs(physical_resolution.after, latent)
    _assert_pending_truth(result, group_by_card_class)
    return result
