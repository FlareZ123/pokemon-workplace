from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from tools.prize_belief_kernel import PrizeBelief
from tools.prize_information_value import Line, evaluate_prize_information
from tools.search_action_legality import SearchResolution


@dataclass(frozen=True)
class SearchInformationProjection:
    """Project one resolved search onto information and material dimensions."""

    observation_applied: bool
    material_action_available: bool
    prior_belief: PrizeBelief
    posterior_belief: PrizeBelief


def project_search_information(
    resolution: SearchResolution,
    prior_belief: PrizeBelief,
    exact_prize_groups: Mapping[str, int],
    *,
    material_action_available: bool,
) -> SearchInformationProjection:
    """Apply exact Prize observation only when the deck-inspection step executed.

    The material planner can independently report no useful output. That does not
    erase an observation already produced by a legal constrained search.
    """

    if resolution.inspected_full_deck and not resolution.legal:
        raise ValueError("an illegal search resolution cannot inspect the deck")

    if not resolution.inspected_full_deck:
        return SearchInformationProjection(
            observation_applied=False,
            material_action_available=material_action_available,
            prior_belief=prior_belief,
            posterior_belief=prior_belief,
        )

    supplied_groups = set(exact_prize_groups)
    expected_groups = set(prior_belief.groups)
    if supplied_groups != expected_groups:
        raise ValueError("exact_prize_groups must match the prior belief groups")

    ordered_counts = {
        group: exact_prize_groups[group]
        for group in prior_belief.groups
    }
    posterior = PrizeBelief.from_exact(
        ordered_counts,
        prior_belief.prize_count,
    )
    return SearchInformationProjection(
        observation_applied=True,
        material_action_available=material_action_available,
        prior_belief=prior_belief,
        posterior_belief=posterior,
    )


def precommitment_information_value_if_observed(
    resolution: SearchResolution,
    group_sizes: Mapping[str, int],
    lines: Sequence[Line],
    *,
    unknown_cards: int = 53,
    prize_count: int = 6,
) -> float:
    """Return VPI when this observation occurs before the modeled commitment.

    Timing is explicit: if the deck-inspection step is not reached, the action
    contributes zero information value to this precommitment decision.
    """

    if not resolution.inspected_full_deck:
        return 0.0
    return evaluate_prize_information(
        group_sizes,
        lines,
        unknown_cards=unknown_cards,
        prize_count=prize_count,
    ).information_value
