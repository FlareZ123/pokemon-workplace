"""Couple physical simultaneous Prize batches to observer-relative latent identities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from pending_prize_batch_identity_belief import (
    ObserverPendingPrizeBatchBeliefs,
    prepend_additional_pending_for_observers,
    project_completed_batch,
    resolve_pending_instance_visibility,
    stage_pending_prize_batch_for_observers,
)
from pending_prize_identity_belief import destination_visibility
from prize_pending_batch_order import PendingPrizeBatchOrder
from prize_pending_take import (
    PendingPrizeResolution,
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
class PrizeBatchObserverState:
    order: PendingPrizeBatchOrder
    beliefs: ObserverPendingPrizeBatchBeliefs
    actor_id: str
    group_by_card_class: Mapping[str, PrizeGroup]

    def __post_init__(self) -> None:
        physical_pending_ids = tuple(
            row.instance_id
            for row in self.order.state.pending
        )
        if physical_pending_ids != self.beliefs.pending_instance_ids:
            raise ValueError(
                "physical pending queue must align with latent belief queue"
            )
        if any(
            instance_id not in physical_pending_ids
            for instance_id in self.order.unresolved_batch_ids
        ):
            raise ValueError(
                "unresolved sibling batch must remain inside pending queue"
            )
        self.beliefs.belief_for(self.actor_id)


@dataclass(frozen=True)
class PrizeBatchObserverStage:
    before_physical: TopPrizePhysicalState
    beliefs_before: ObserverTopPrizeBeliefs
    after: PrizeBatchObserverState


@dataclass(frozen=True)
class PrizeBatchObserverResolution:
    before: PrizeBatchObserverState
    physical_resolution: PendingPrizeResolution
    destination_zone: str
    after_batch: PrizeBatchObserverState | None
    after_beliefs: (
        ObserverPendingPrizeBatchBeliefs | ObserverTopPrizeBeliefs
    )


def _validate_truth(
    physical: TopPrizePhysicalState,
    beliefs: ObserverTopPrizeBeliefs,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> None:
    top_group, prize_groups = actual_joint_groups(
        physical,
        group_by_card_class,
    )
    for observer_id, belief in beliefs.beliefs:
        probability = belief_truth_probability(
            belief,
            top_group=top_group,
            prize_groups=prize_groups,
        )
        if probability == 0.0:
            raise ValueError(
                f"observer {observer_id!r} assigns zero probability "
                "to exact physical truth"
            )


def stage_prize_batch_with_latent_observers(
    physical: TopPrizePhysicalState,
    beliefs: ObserverTopPrizeBeliefs,
    *,
    actor_id: str,
    positions: tuple[int, ...],
    group_by_card_class: Mapping[str, PrizeGroup],
) -> PrizeBatchObserverStage:
    """Stage one simultaneous Prize award without marginalizing selected IDs."""

    beliefs.belief_for(actor_id)
    for _observer_id, belief in beliefs.beliefs:
        if belief.face_up != physical.face_up:
            raise ValueError(
                "observer belief visibility disagrees with physical visibility"
            )
    _validate_truth(physical, beliefs, group_by_card_class)

    pending = stage_prize_takes(
        physical,
        positions=positions,
    )
    pending_ids = tuple(row.instance_id for row in pending.pending)
    observed_groups = tuple(
        group_by_card_class.get(
            physical.ledger.instance(instance_id).card_class
        )
        for instance_id in pending_ids
    )
    latent = stage_pending_prize_batch_for_observers(
        beliefs,
        positions=positions,
        pending_instance_ids=pending_ids,
        visible_groups={actor_id: observed_groups},
    )
    order = PendingPrizeBatchOrder.from_staged(pending)
    return PrizeBatchObserverStage(
        physical,
        beliefs,
        PrizeBatchObserverState(
            order,
            latent,
            actor_id,
            group_by_card_class,
        ),
    )


def resolve_batch_instance_destination(
    state: PrizeBatchObserverState,
    *,
    instance_id: str,
    destination_zone: str,
) -> PrizeBatchObserverResolution:
    """Choose one sibling, move it physically, and apply destination visibility."""

    reordered = state.order.choose_next(instance_id)
    instance = reordered.physical.ledger.instance(instance_id)
    observed_group = state.group_by_card_class.get(instance.card_class)
    observer_ids = tuple(
        observer_id
        for observer_id, _belief in state.beliefs.beliefs
    )
    visible = destination_visibility(
        observer_ids,
        actor_id=state.actor_id,
        destination_zone=destination_zone,
        observed_group=observed_group,
    )

    physical_resolution = resolve_next_pending_prize(
        reordered,
        destination_zone=destination_zone,
    )
    next_beliefs = resolve_pending_instance_visibility(
        state.beliefs,
        instance_id=instance_id,
        visible_groups=visible,
    )
    next_order = state.order.advance_after_resolution(
        physical_resolution.after,
        resolved_instance_id=instance_id,
    )

    if next_order is None:
        projected = project_completed_batch(next_beliefs)
        return PrizeBatchObserverResolution(
            state,
            physical_resolution,
            destination_zone,
            None,
            projected,
        )

    next_state = PrizeBatchObserverState(
        next_order,
        next_beliefs,
        state.actor_id,
        state.group_by_card_class,
    )
    return PrizeBatchObserverResolution(
        state,
        physical_resolution,
        destination_zone,
        next_state,
        next_beliefs,
    )

def prepend_additional_prize_with_latent_observers(
    state: PrizeBatchObserverState,
    *,
    position: int,
) -> PrizeBatchObserverState:
    """Prepend a nested additional Prize while preserving sibling barriers."""

    physical = state.order.state
    if not 0 <= position < len(physical.physical.prize_instance_ids):
        raise IndexError("Prize position out of range")
    if not state.order.unresolved_batch_ids:
        raise ValueError("no unresolved sibling batch remains")

    instance_id = physical.physical.prize_instance_ids[position]
    card_class = physical.physical.ledger.instance(instance_id).card_class
    observed_group = state.group_by_card_class.get(card_class)
    observer_ids = tuple(
        observer_id
        for observer_id, _belief in state.beliefs.beliefs
    )
    if physical.physical.face_up[position]:
        visible = {
            observer_id: observed_group
            for observer_id in observer_ids
        }
    else:
        visible = {state.actor_id: observed_group}

    next_physical = stage_additional_prize_front(
        physical,
        position=position,
    )
    next_beliefs = prepend_additional_pending_for_observers(
        state.beliefs,
        position=position,
        instance_id=instance_id,
        visible_groups=visible,
    )
    next_order = state.order.rebind(next_physical)
    return PrizeBatchObserverState(
        next_order,
        next_beliefs,
        state.actor_id,
        state.group_by_card_class,
    )


def resolve_nested_queue_head_destination(
    state: PrizeBatchObserverState,
    *,
    destination_zone: str,
) -> PrizeBatchObserverState:
    """Resolve a nested queue-head Prize before returning to sibling choice."""

    if not state.order.state.pending:
        raise ValueError("no pending Prize card remains")
    instance_id = state.order.state.pending[0].instance_id
    if instance_id in state.order.unresolved_batch_ids:
        raise ValueError(
            "queue head is an original sibling; use sibling resolution"
        )

    instance = state.order.state.physical.ledger.instance(instance_id)
    observed_group = state.group_by_card_class.get(instance.card_class)
    observer_ids = tuple(
        observer_id
        for observer_id, _belief in state.beliefs.beliefs
    )
    visible = destination_visibility(
        observer_ids,
        actor_id=state.actor_id,
        destination_zone=destination_zone,
        observed_group=observed_group,
    )
    physical_resolution = resolve_next_pending_prize(
        state.order.state,
        destination_zone=destination_zone,
    )
    next_beliefs = resolve_pending_instance_visibility(
        state.beliefs,
        instance_id=instance_id,
        visible_groups=visible,
    )
    next_order = state.order.rebind(physical_resolution.after)
    return PrizeBatchObserverState(
        next_order,
        next_beliefs,
        state.actor_id,
        state.group_by_card_class,
    )

