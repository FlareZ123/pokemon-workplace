"""Physical Prize-taking queue with E-31 before-hand timing."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from identity_materialization import assert_conserved, move_instance
from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_joint_position_removal import remove_prize_position_for_observers
from prize_position_belief import PrizeGroup
from top_prize_physical_bridge import (
    TopPrizePhysicalState,
    actual_joint_groups,
    belief_truth_probability,
)


@dataclass(frozen=True)
class PendingPrize:
    instance_id: str
    was_face_down: bool


@dataclass(frozen=True)
class PrizePendingTakeState:
    physical: TopPrizePhysicalState
    pending: tuple[PendingPrize, ...]

    def __post_init__(self) -> None:
        ids = tuple(row.instance_id for row in self.pending)
        if len(ids) != len(set(ids)):
            raise ValueError("pending Prize instance IDs must be unique")

        occupied = {self.physical.top_instance_id, *self.physical.prize_instance_ids}
        if occupied.intersection(ids):
            raise ValueError("pending instances cannot still occupy top/Prize slots")

        for row in self.pending:
            instance = self.physical.ledger.instance(row.instance_id)
            if instance.zone != "prize_pending":
                raise ValueError("pending Prize instances must be in prize_pending")


@dataclass(frozen=True)
class PendingPrizeResolution:
    before: PrizePendingTakeState
    after: PrizePendingTakeState
    resolved: PendingPrize
    destination_zone: str


@dataclass(frozen=True)
class PrizePendingObserverTransition:
    before_physical: TopPrizePhysicalState
    after_pending: PrizePendingTakeState
    beliefs_before: ObserverTopPrizeBeliefs
    beliefs_after: ObserverTopPrizeBeliefs


def stage_prize_takes(
    physical: TopPrizePhysicalState,
    *,
    positions: tuple[int, ...],
) -> PrizePendingTakeState:
    """Move selected Prize instances into an ordered pending queue."""

    if not positions:
        raise ValueError("at least one Prize position must be selected")
    if len(positions) != len(set(positions)):
        raise ValueError("Prize positions must be unique")
    if any(
        position < 0 or position >= len(physical.prize_instance_ids)
        for position in positions
    ):
        raise IndexError("Prize position out of range")

    selected = set(positions)
    pending = tuple(
        PendingPrize(
            physical.prize_instance_ids[position],
            not physical.face_up[position],
        )
        for position in positions
    )

    ledger = physical.ledger
    for row in pending:
        ledger = move_instance(
            ledger,
            row.instance_id,
            "prize_pending",
        )
    assert_conserved(physical.ledger, ledger)

    remaining_ids = tuple(
        instance_id
        for index, instance_id in enumerate(physical.prize_instance_ids)
        if index not in selected
    )
    remaining_face_up = tuple(
        is_face_up
        for index, is_face_up in enumerate(physical.face_up)
        if index not in selected
    )

    remaining = TopPrizePhysicalState(
        ledger,
        physical.top_instance_id,
        remaining_ids,
        remaining_face_up,
    )
    return PrizePendingTakeState(remaining, pending)


def resolve_next_pending_prize(
    state: PrizePendingTakeState,
    *,
    destination_zone: str = "hand",
    attached_to: str | None = None,
    board_object_id: str | None = None,
) -> PendingPrizeResolution:
    """Resolve exactly one pending Prize before continuing to the next."""

    if not state.pending:
        raise ValueError("no pending Prize card remains")

    resolved = state.pending[0]
    ledger = move_instance(
        state.physical.ledger,
        resolved.instance_id,
        destination_zone,
        attached_to=attached_to,
        board_object_id=board_object_id,
    )
    assert_conserved(state.physical.ledger, ledger)

    physical = TopPrizePhysicalState(
        ledger,
        state.physical.top_instance_id,
        state.physical.prize_instance_ids,
        state.physical.face_up,
    )
    next_state = PrizePendingTakeState(
        physical,
        state.pending[1:],
    )
    return PendingPrizeResolution(
        before=state,
        after=next_state,
        resolved=resolved,
        destination_zone=destination_zone,
    )


def _validate_truth_supported(
    physical: TopPrizePhysicalState,
    beliefs: ObserverTopPrizeBeliefs,
    group_by_card_class: Mapping[str, PrizeGroup],
    *,
    after_transition: bool,
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
        if probability > 0.0:
            continue
        message = (
            f"observer {observer_id!r} assigns zero probability "
            "to exact physical truth"
        )
        if after_transition:
            raise AssertionError(message)
        raise ValueError(message)


def stage_prize_takes_with_observers(
    physical: TopPrizePhysicalState,
    beliefs: ObserverTopPrizeBeliefs,
    *,
    actor_id: str,
    positions: tuple[int, ...],
    group_by_card_class: Mapping[str, PrizeGroup],
) -> PrizePendingObserverTransition:
    """Stage Prize cards and update the taker's private identity observations."""

    beliefs.belief_for(actor_id)
    for _observer_id, belief in beliefs.beliefs:
        if belief.face_up != physical.face_up:
            raise ValueError(
                "observer belief visibility disagrees with physical visibility"
            )

    _validate_truth_supported(
        physical,
        beliefs,
        group_by_card_class,
        after_transition=False,
    )

    if not positions:
        raise ValueError("at least one Prize position must be selected")
    if len(positions) != len(set(positions)):
        raise ValueError("Prize positions must be unique")
    if any(
        position < 0 or position >= len(physical.prize_instance_ids)
        for position in positions
    ):
        raise IndexError("Prize position out of range")

    current_beliefs = beliefs
    removed_original_positions: list[int] = []

    for original_position in positions:
        current_position = original_position - sum(
            prior_position < original_position
            for prior_position in removed_original_positions
        )
        instance_id = physical.prize_instance_ids[original_position]
        card_class = physical.ledger.instance(instance_id).card_class
        observed_group = group_by_card_class.get(card_class)

        current_beliefs = remove_prize_position_for_observers(
            current_beliefs,
            position=current_position,
            visible_groups={actor_id: observed_group},
        )
        removed_original_positions.append(original_position)

    pending = stage_prize_takes(
        physical,
        positions=positions,
    )

    for _observer_id, belief in current_beliefs.beliefs:
        if belief.face_up != pending.physical.face_up:
            raise AssertionError(
                "belief and physical Prize visibility diverged"
            )

    _validate_truth_supported(
        pending.physical,
        current_beliefs,
        group_by_card_class,
        after_transition=True,
    )

    return PrizePendingObserverTransition(
        before_physical=physical,
        after_pending=pending,
        beliefs_before=beliefs,
        beliefs_after=current_beliefs,
    )
