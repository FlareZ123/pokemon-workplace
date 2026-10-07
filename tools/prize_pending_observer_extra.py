"""Observer-aware additional Prize staging inside an E-31 pending window."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from observer_top_prize_beliefs import ObserverTopPrizeBeliefs
from prize_joint_position_removal import remove_prize_position_for_observers
from prize_pending_take import (
    PrizePendingTakeState,
    stage_additional_prize_front,
)
from prize_position_belief import PrizeGroup
from top_prize_physical_bridge import actual_joint_groups, belief_truth_probability


@dataclass(frozen=True)
class AdditionalPrizeObserverTransition:
    before: PrizePendingTakeState
    after: PrizePendingTakeState
    beliefs_before: ObserverTopPrizeBeliefs
    beliefs_after: ObserverTopPrizeBeliefs
    actor_id: str
    position: int


def _validate(
    state: PrizePendingTakeState,
    beliefs: ObserverTopPrizeBeliefs,
    group_by_card_class: Mapping[str, PrizeGroup],
    *,
    after_transition: bool,
) -> None:
    for _observer_id, belief in beliefs.beliefs:
        if belief.face_up != state.physical.face_up:
            raise ValueError(
                "observer belief visibility disagrees with physical visibility"
            )

    top_group, prize_groups = actual_joint_groups(
        state.physical,
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


def stage_additional_prize_front_with_observers(
    state: PrizePendingTakeState,
    beliefs: ObserverTopPrizeBeliefs,
    *,
    actor_id: str,
    position: int,
    group_by_card_class: Mapping[str, PrizeGroup],
) -> AdditionalPrizeObserverTransition:
    """Take one extra Prize, privately reveal it to the taker, and prepend it."""

    beliefs.belief_for(actor_id)
    _validate(
        state,
        beliefs,
        group_by_card_class,
        after_transition=False,
    )

    if not 0 <= position < len(state.physical.prize_instance_ids):
        raise IndexError("Prize position out of range")

    instance_id = state.physical.prize_instance_ids[position]
    card_class = state.physical.ledger.instance(instance_id).card_class
    observed_group = group_by_card_class.get(card_class)

    next_beliefs = remove_prize_position_for_observers(
        beliefs,
        position=position,
        visible_groups={actor_id: observed_group},
    )
    next_state = stage_additional_prize_front(
        state,
        position=position,
    )

    _validate(
        next_state,
        next_beliefs,
        group_by_card_class,
        after_transition=True,
    )
    return AdditionalPrizeObserverTransition(
        before=state,
        after=next_state,
        beliefs_before=beliefs,
        beliefs_after=next_beliefs,
        actor_id=actor_id,
        position=position,
    )
