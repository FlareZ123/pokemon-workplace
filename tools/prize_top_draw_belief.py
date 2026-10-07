"""Belief transition for drawing an uncertain top card correlated with Prizes."""

from __future__ import annotations

from dataclasses import dataclass

from prize_slot_visibility import PrizeSlotVisibilityBelief
from prize_top_swap_belief import TopPrizeJointBelief
from prize_position_belief import PrizeGroup


@dataclass(frozen=True)
class TopDrawBeliefResult:
    drawn_group: PrizeGroup
    observation_probability: float
    prizes_after_draw: PrizeSlotVisibilityBelief


def draw_observed_top(
    state: TopPrizeJointBelief,
    observed_group: PrizeGroup,
) -> TopDrawBeliefResult:
    """Condition on the drawn top group and return the correlated Prize posterior."""

    probability = state.top_probability(observed_group)
    if probability == 0.0:
        raise ValueError("top observation has zero probability under this belief")

    conditioned = state.condition_top(observed_group)
    return TopDrawBeliefResult(
        drawn_group=observed_group,
        observation_probability=probability,
        prizes_after_draw=conditioned.project_prizes(),
    )


def top_draw_outcomes(
    state: TopPrizeJointBelief,
) -> tuple[TopDrawBeliefResult, ...]:
    """Enumerate all grouped top-draw observations with nonzero probability."""

    candidates: tuple[PrizeGroup, ...] = (None,) + state.groups
    return tuple(
        draw_observed_top(state, group)
        for group in candidates
        if state.top_probability(group) > 0.0
    )
