"""Bind exact top/Prize card instances to observer-relative joint beliefs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    move_instance,
)
from observer_top_prize_beliefs import (
    ObserverTopPrizeBeliefs,
    resolve_optional_top_prize_swap,
)
from prize_position_belief import PrizeGroup
from prize_top_swap_belief import TopPrizeJointBelief


@dataclass(frozen=True)
class TopPrizePhysicalState:
    """Exact physical identities occupying the deck top and Prize slots."""

    ledger: IdentityLedger
    top_instance_id: str
    prize_instance_ids: tuple[str, ...]
    face_up: tuple[bool, ...]

    def __post_init__(self) -> None:
        if not self.top_instance_id:
            raise ValueError("top_instance_id must be non-empty")
        if len(self.prize_instance_ids) != len(self.face_up):
            raise ValueError("face_up must align with Prize positions")

        ids = (self.top_instance_id,) + self.prize_instance_ids
        if len(ids) != len(set(ids)):
            raise ValueError("top and Prize positions must use distinct instances")

        top = self.ledger.instance(self.top_instance_id)
        if top.zone != "deck_top":
            raise ValueError("top instance must be in deck_top")

        for instance_id in self.prize_instance_ids:
            prize = self.ledger.instance(instance_id)
            if prize.zone != "prize":
                raise ValueError("Prize instances must be in prize")


@dataclass(frozen=True)
class ObserverPhysicalSwapTransition:
    physical_before: TopPrizePhysicalState
    physical_after: TopPrizePhysicalState
    beliefs_before: ObserverTopPrizeBeliefs
    beliefs_after: ObserverTopPrizeBeliefs


def swap_exact_top_with_prize(
    state: TopPrizePhysicalState,
    *,
    position: int,
) -> TopPrizePhysicalState:
    """Swap one face-down Prize instance with the exact top-deck instance."""

    if not 0 <= position < len(state.prize_instance_ids):
        raise IndexError("Prize position out of range")
    if state.face_up[position]:
        raise ValueError("selected Prize position must be face down")

    incoming_top = state.top_instance_id
    outgoing_prize = state.prize_instance_ids[position]

    ledger = move_instance(state.ledger, incoming_top, "prize")
    ledger = move_instance(ledger, outgoing_prize, "deck_top")
    assert_conserved(state.ledger, ledger)

    prize_ids = list(state.prize_instance_ids)
    prize_ids[position] = incoming_top
    return TopPrizePhysicalState(
        ledger,
        outgoing_prize,
        tuple(prize_ids),
        state.face_up,
    )


def actual_joint_groups(
    state: TopPrizePhysicalState,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> tuple[PrizeGroup, tuple[PrizeGroup, ...]]:
    """Project exact physical truth into one strategic grouping."""

    def group_for(instance_id: str) -> PrizeGroup:
        card_class = state.ledger.instance(instance_id).card_class
        return group_by_card_class.get(card_class)

    return (
        group_for(state.top_instance_id),
        tuple(group_for(instance_id) for instance_id in state.prize_instance_ids),
    )


def belief_truth_probability(
    belief: TopPrizeJointBelief,
    *,
    top_group: PrizeGroup,
    prize_groups: tuple[PrizeGroup, ...],
) -> float:
    """Probability one observer assigns to the exact grouped physical truth."""

    if len(prize_groups) != belief.prize_count:
        raise ValueError("physical Prize groups do not match belief Prize count")

    return sum(
        probability
        for (current_top, current_prizes), probability in belief.masses
        if current_top == top_group and current_prizes == prize_groups
    )


def _validate_public_geometry(
    physical: TopPrizePhysicalState,
    beliefs: ObserverTopPrizeBeliefs,
) -> None:
    for _observer_id, belief in beliefs.beliefs:
        if belief.face_up != physical.face_up:
            raise ValueError(
                "observer belief visibility disagrees with physical visibility"
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


def resolve_observer_physical_optional_swap(
    physical: TopPrizePhysicalState,
    beliefs: ObserverTopPrizeBeliefs,
    *,
    actor_id: str,
    swap_probability_by_top: Mapping[PrizeGroup, float],
    observed_swap: bool,
    position: int | None,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> ObserverPhysicalSwapTransition:
    """Advance exact physical truth and every observer posterior together."""

    _validate_public_geometry(physical, beliefs)
    _validate_truth_supported(
        physical,
        beliefs,
        group_by_card_class,
        after_transition=False,
    )

    actor_observed_top, _ = actual_joint_groups(
        physical,
        group_by_card_class,
    )
    next_beliefs = resolve_optional_top_prize_swap(
        beliefs,
        actor_id=actor_id,
        actor_observed_top=actor_observed_top,
        swap_probability_by_top=swap_probability_by_top,
        observed_swap=observed_swap,
        position=position,
    )

    next_physical = physical
    if observed_swap:
        if position is None:
            raise AssertionError("validated swap position is missing")
        next_physical = swap_exact_top_with_prize(
            physical,
            position=position,
        )

    _validate_public_geometry(next_physical, next_beliefs)
    _validate_truth_supported(
        next_physical,
        next_beliefs,
        group_by_card_class,
        after_transition=True,
    )

    return ObserverPhysicalSwapTransition(
        physical_before=physical,
        physical_after=next_physical,
        beliefs_before=beliefs,
        beliefs_after=next_beliefs,
    )
