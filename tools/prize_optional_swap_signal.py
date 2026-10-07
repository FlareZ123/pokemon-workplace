"""Bayesian signaling from an optional Prize/top-deck swap decision."""

from __future__ import annotations

from collections.abc import Mapping
from math import isclose

from prize_position_belief import PrizeGroup
from prize_top_swap_belief import TopPrizeJointBelief


def condition_on_optional_swap_decision(
    belief: TopPrizeJointBelief,
    *,
    swap_probability_by_top: Mapping[PrizeGroup, float],
    observed_swap: bool,
) -> TopPrizeJointBelief:
    """Condition an observer's joint belief on whether a swap was chosen.

    The policy maps each hidden top-card group to the probability that the
    acting player performs the optional swap after seeing that top card.
    """

    supported_top_groups = {
        top_group
        for (top_group, _), probability in belief.masses
        if probability > 0.0
    }
    if not supported_top_groups <= set(swap_probability_by_top):
        raise ValueError("policy must cover every supported top-card group")

    for probability in swap_probability_by_top.values():
        if not 0.0 <= probability <= 1.0:
            raise ValueError("swap probabilities must lie in [0, 1]")

    weighted: list[
        tuple[tuple[PrizeGroup, tuple[PrizeGroup, ...]], float]
    ] = []
    evidence = 0.0

    for joint_state, prior_probability in belief.masses:
        top_group, _ = joint_state
        swap_probability = swap_probability_by_top[top_group]
        likelihood = (
            swap_probability
            if observed_swap
            else 1.0 - swap_probability
        )
        probability = prior_probability * likelihood
        if probability == 0.0:
            continue
        weighted.append((joint_state, probability))
        evidence += probability

    if isclose(evidence, 0.0, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("observed decision has zero probability under policy")

    return TopPrizeJointBelief(
        belief.groups,
        belief.face_up,
        tuple(
            (joint_state, probability / evidence)
            for joint_state, probability in weighted
        ),
    )
