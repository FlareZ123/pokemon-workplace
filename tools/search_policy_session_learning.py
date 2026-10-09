"""Bayesian inference of persistent search-policy hypotheses across games.

Each game is an independent hidden Prize deal, conditional on a fixed opponent
search policy. A selected-card print can be observed immediately, while the
Prize status of a specified card can become known later. Retain both evidence
types and update policy odds only from their likelihood under each hypothesis.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction

from latent_search_policy_belief import (
    PolicyHypothesis,
    PolicySearchPosterior,
    enumerate_policy_search_worlds,
)
from revealed_print_information import SearchCard


@dataclass(frozen=True)
class SearchObservation:
    """One completed search, possibly with retrospectively revealed Prize status."""

    selected_print_id: str
    critical_card_id: str
    critical_prized: bool | None = None

    def __post_init__(self) -> None:
        if not self.selected_print_id or not self.critical_card_id:
            raise ValueError("observation IDs must be nonempty")


@dataclass(frozen=True)
class PolicyLearningPosterior:
    """Persistent opponent policy probabilities after past search evidence."""

    weights: tuple[tuple[str, Fraction], ...]

    def __post_init__(self) -> None:
        if not self.weights or len({name for name, _ in self.weights}) != len(
            self.weights
        ):
            raise ValueError("policy posterior needs unique nonempty IDs")
        if any(not name or value < 0 for name, value in self.weights):
            raise ValueError("policy weights must be nonnegative and named")
        if sum((value for _, value in self.weights), Fraction()) != 1:
            raise ValueError("policy posterior weights must sum to one")

    def probability(self, policy_name: str) -> Fraction:
        return dict(self.weights)[policy_name]

    def update(
        self,
        observation: SearchObservation,
        worlds_by_policy: Mapping[str, PolicySearchPosterior],
    ) -> "PolicyLearningPosterior":
        """Condition policy odds on a search event, with optional delayed label."""
        if set(worlds_by_policy) != {name for name, _ in self.weights}:
            raise ValueError("hypothesis likelihoods must cover all known policies")

        numerators = []
        for name, prior in self.weights:
            likelihood = worlds_by_policy[name].probability(
                lambda world: (
                    world.selected_print_id == observation.selected_print_id
                    and (
                        observation.critical_prized is None
                        or (
                            observation.critical_card_id in world.ordered_prize_ids
                        ) == observation.critical_prized
                    )
                )
            )
            numerators.append((name, prior * likelihood))
        normalizer = sum((value for _, value in numerators), Fraction())
        if normalizer == 0:
            raise ValueError("observation impossible under all policy hypotheses")
        return PolicyLearningPosterior(
            tuple((name, value / normalizer) for name, value in numerators)
        )


def policy_search_likelihoods(
    cards: Sequence[SearchCard],
    prize_count: int,
    policies: Sequence[PolicyHypothesis],
) -> dict[str, PolicySearchPosterior]:
    """Compile exact within-policy search/Prize/top likelihoods."""
    return {
        policy.name: enumerate_policy_search_worlds(
            cards,
            prize_count,
            (PolicyHypothesis(policy.name, Fraction(1), policy.choose),),
        )
        for policy in policies
    }
