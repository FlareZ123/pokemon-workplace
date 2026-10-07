from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class Candidate:
    name: str
    forced_basics: int
    diagnostic_cards: int
    deck_size: int = 60
    hand_size: int = 7


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def attempt_components(candidate: Candidate) -> dict[str, float]:
    denominator = _choose(candidate.deck_size, candidate.hand_size)
    rejected = _choose(
        candidate.deck_size - candidate.forced_basics, candidate.hand_size
    ) / denominator
    rejected_without_diagnostic = _choose(
        candidate.deck_size
        - candidate.forced_basics
        - candidate.diagnostic_cards,
        candidate.hand_size,
    ) / denominator
    rejected_with_diagnostic = rejected - rejected_without_diagnostic
    return {
        "accepted": 1.0 - rejected,
        "rejected": rejected,
        "rejected_without_diagnostic": rejected_without_diagnostic,
        "rejected_with_diagnostic": rejected_with_diagnostic,
    }


def count_bin_observation(candidate: Candidate) -> dict[str, float]:
    parts = attempt_components(candidate)
    rejected = parts["rejected"]
    accepted = parts["accepted"]
    return {
        "0 mulligans": accepted,
        "1 mulligan": rejected * accepted,
        "2+ mulligans": rejected * rejected,
    }


def diagnostic_exposure_observation(candidate: Candidate) -> dict[str, float]:
    parts = attempt_components(candidate)
    accepted = parts["accepted"]
    reject_seen = parts["rejected_with_diagnostic"]
    ever_seen = reject_seen / (accepted + reject_seen)
    return {
        "diagnostic exposed": ever_seen,
        "diagnostic not exposed": 1.0 - ever_seen,
    }


def observation_table(
    candidates: tuple[Candidate, ...],
    per_candidate: Mapping[str, Mapping[str, float]],
) -> dict[str, dict[str, float]]:
    observations: dict[str, dict[str, float]] = {}
    for candidate in candidates:
        for observation, probability in per_candidate[candidate.name].items():
            observations.setdefault(observation, {})[candidate.name] = probability
    _validate_observations(candidates, observations)
    return observations


def _validate_observations(
    candidates: tuple[Candidate, ...],
    observations: Mapping[str, Mapping[str, float]],
) -> None:
    candidate_names = {candidate.name for candidate in candidates}
    if not observations:
        raise ValueError("observations must not be empty")
    for likelihoods in observations.values():
        if set(likelihoods) != candidate_names:
            raise ValueError("every observation must cover every candidate")
        if any(value < 0.0 for value in likelihoods.values()):
            raise ValueError("observation likelihoods must be nonnegative")
    for candidate in candidates:
        total = sum(row[candidate.name] for row in observations.values())
        if not math.isclose(total, 1.0, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError(
                f"observation probabilities for {candidate.name!r} sum to {total}"
            )


def bayes_decision_value(
    candidates: tuple[Candidate, ...],
    priors: Mapping[str, float],
    utilities: Mapping[str, Mapping[str, float]],
    observations: Mapping[str, Mapping[str, float]],
) -> dict[str, Any]:
    candidate_names = {candidate.name for candidate in candidates}
    if set(priors) != candidate_names:
        raise ValueError("priors must cover every candidate")
    if any(value < 0.0 for value in priors.values()):
        raise ValueError("priors must be nonnegative")
    if not math.isclose(sum(priors.values()), 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError("priors must sum to 1")
    if not utilities:
        raise ValueError("at least one action is required")
    for action, by_candidate in utilities.items():
        if set(by_candidate) != candidate_names:
            raise ValueError(f"utility action {action!r} must cover every candidate")

    _validate_observations(candidates, observations)

    prior_action_values = {
        action: sum(priors[name] * utility[name] for name in candidate_names)
        for action, utility in utilities.items()
    }
    baseline_action = max(prior_action_values, key=prior_action_values.get)
    baseline_value = prior_action_values[baseline_action]

    informed_value = 0.0
    observation_rows: dict[str, Any] = {}
    for observation, likelihoods in observations.items():
        evidence_probability = sum(
            priors[name] * likelihoods[name] for name in candidate_names
        )
        joint_action_values = {
            action: sum(
                priors[name] * likelihoods[name] * utility[name]
                for name in candidate_names
            )
            for action, utility in utilities.items()
        }
        best_action = max(joint_action_values, key=joint_action_values.get)
        best_joint_value = joint_action_values[best_action]
        informed_value += best_joint_value
        observation_rows[observation] = {
            "probability": evidence_probability,
            "posterior": {
                name: priors[name] * likelihoods[name] / evidence_probability
                for name in candidate_names
            },
            "best_action": best_action,
            "conditional_action_value": best_joint_value / evidence_probability,
        }

    return {
        "baseline_action": baseline_action,
        "baseline_value": baseline_value,
        "informed_value": informed_value,
        "value_of_information": informed_value - baseline_value,
        "observations": observation_rows,
    }


def identity_utilities(
    candidates: tuple[Candidate, ...],
) -> dict[str, dict[str, float]]:
    return {
        f"choose {candidate.name}": {
            other.name: float(other.name == candidate.name) for other in candidates
        }
        for candidate in candidates
    }


def build_examples() -> dict[str, Any]:
    low_basic = Candidate("4-Basic candidate", 4, 4)
    high_basic = Candidate("12-Basic candidate", 12, 4)
    density_candidates = (low_basic, high_basic)
    density_observations = observation_table(
        density_candidates,
        {
            candidate.name: count_bin_observation(candidate)
            for candidate in density_candidates
        },
    )
    density_value = bayes_decision_value(
        density_candidates,
        {candidate.name: 0.5 for candidate in density_candidates},
        identity_utilities(density_candidates),
        density_observations,
    )

    four_copy = Candidate("4-copy diagnostic", 4, 4)
    two_copy = Candidate("2-copy diagnostic", 4, 2)
    copy_candidates = (four_copy, two_copy)
    exposure_observations = observation_table(
        copy_candidates,
        {
            candidate.name: diagnostic_exposure_observation(candidate)
            for candidate in copy_candidates
        },
    )
    exposure_value = bayes_decision_value(
        copy_candidates,
        {candidate.name: 0.5 for candidate in copy_candidates},
        identity_utilities(copy_candidates),
        exposure_observations,
    )

    stable_action = bayes_decision_value(
        copy_candidates,
        {candidate.name: 0.5 for candidate in copy_candidates},
        {
            "preserve matchup tech": {
                "4-copy diagnostic": 1.0,
                "2-copy diagnostic": 0.72,
            },
            "spend matchup tech": {
                "4-copy diagnostic": 0.35,
                "2-copy diagnostic": 1.0,
            },
        },
        exposure_observations,
    )

    switching_action = bayes_decision_value(
        copy_candidates,
        {candidate.name: 0.5 for candidate in copy_candidates},
        {
            "preserve matchup tech": {
                "4-copy diagnostic": 1.0,
                "2-copy diagnostic": 0.3,
            },
            "spend matchup tech": {
                "4-copy diagnostic": 0.2,
                "2-copy diagnostic": 1.0,
            },
        },
        exposure_observations,
    )

    return {
        "basic_density_identification_from_count_bins": density_value,
        "copy_count_identification_from_diagnostic_exposure": exposure_value,
        "stable_action_example": stable_action,
        "boundary_crossing_action_example": switching_action,
    }
