"""Observer-indexed joint beliefs for Prize/top-deck swaps."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import isclose

from prize_optional_swap_signal import condition_on_optional_swap_decision
from prize_position_belief import PrizeGroup
from prize_slot_visibility import PrizeSlotVisibilityBelief
from prize_top_swap_belief import (
    TopPrizeJointBelief,
    swap_joint_top_with_face_down_prize,
)


@dataclass(frozen=True)
class ObserverTopPrizeBeliefs:
    """One joint top/Prize belief per observer for the same public topology."""

    beliefs: tuple[tuple[str, TopPrizeJointBelief], ...]

    def __post_init__(self) -> None:
        if not self.beliefs:
            raise ValueError("at least one observer belief is required")

        observer_ids = tuple(observer_id for observer_id, _ in self.beliefs)
        if len(observer_ids) != len(set(observer_ids)):
            raise ValueError("observer IDs must be unique")

        reference = self.beliefs[0][1]
        for _observer_id, belief in self.beliefs[1:]:
            if belief.groups != reference.groups:
                raise ValueError("all observers must use the same groups")
            if belief.face_up != reference.face_up:
                raise ValueError(
                    "all observers must agree on public Prize visibility"
                )

    def belief_for(self, observer_id: str) -> TopPrizeJointBelief:
        for current_id, belief in self.beliefs:
            if current_id == observer_id:
                return belief
        raise KeyError(observer_id)


def independent_top_prize_belief(
    prizes: PrizeSlotVisibilityBelief,
    top_probabilities: Mapping[PrizeGroup, float],
) -> TopPrizeJointBelief:
    """Combine a Prize-position belief with an independent top-card prior."""

    if not top_probabilities:
        raise ValueError("top_probabilities must not be empty")

    total = sum(top_probabilities.values())
    if not isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("top probabilities must sum to one")

    modeled = set(prizes.positions.groups)
    for group, probability in top_probabilities.items():
        if probability < 0.0:
            raise ValueError("top probabilities must be non-negative")
        if group is not None and group not in modeled:
            raise ValueError("top group must be modeled or None")

    masses = []
    for top_group, top_probability in top_probabilities.items():
        if top_probability == 0.0:
            continue
        for prize_state, prize_probability in prizes.positions.masses:
            probability = top_probability * prize_probability
            if probability:
                masses.append(
                    ((top_group, prize_state), probability)
                )

    return TopPrizeJointBelief(
        prizes.positions.groups,
        prizes.face_up,
        tuple(sorted(masses, key=lambda row: repr(row[0]))),
    )


def resolve_optional_top_prize_swap(
    state: ObserverTopPrizeBeliefs,
    *,
    actor_id: str,
    actor_observed_top: PrizeGroup,
    swap_probability_by_top: Mapping[PrizeGroup, float],
    observed_swap: bool,
    position: int | None,
) -> ObserverTopPrizeBeliefs:
    """Resolve one public optional swap after a private top-card observation."""

    state.belief_for(actor_id)

    if observed_swap and position is None:
        raise ValueError("a performed swap requires a Prize position")
    if not observed_swap and position is not None:
        raise ValueError("a declined swap must not specify a Prize position")

    updated = []
    for observer_id, belief in state.beliefs:
        if observer_id == actor_id:
            conditioned = belief.condition_top(actor_observed_top)
        else:
            conditioned = condition_on_optional_swap_decision(
                belief,
                swap_probability_by_top=swap_probability_by_top,
                observed_swap=observed_swap,
            )

        if observed_swap:
            if position is None:
                raise AssertionError("validated swap position is missing")
            conditioned = swap_joint_top_with_face_down_prize(
                conditioned,
                position=position,
            )

        updated.append((observer_id, conditioned))

    return ObserverTopPrizeBeliefs(tuple(updated))


def condition_top_observations(
    state: ObserverTopPrizeBeliefs,
    *,
    visible_groups: Mapping[str, PrizeGroup],
) -> ObserverTopPrizeBeliefs:
    """Condition only observers who learn a top-card identity."""

    observer_ids = {observer_id for observer_id, _ in state.beliefs}
    if not set(visible_groups) <= observer_ids:
        raise ValueError("visible_groups contains an unknown observer")

    updated = []
    for observer_id, belief in state.beliefs:
        if observer_id in visible_groups:
            belief = belief.condition_top(visible_groups[observer_id])
        updated.append((observer_id, belief))

    return ObserverTopPrizeBeliefs(tuple(updated))
