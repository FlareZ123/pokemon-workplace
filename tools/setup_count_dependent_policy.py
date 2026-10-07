"""Exact count-dependent setup policy with an eventually constant mulligan cost."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from tools.setup_hand_value_policy import (
    HandValue,
    OptimalSetupPolicy,
    SetupHandState,
    conditioned_prize_hand_distribution,
    opening_hand_distribution,
    optimize_linear_mulligan_penalty,
)


@dataclass(frozen=True)
class CountPolicyStep:
    failed_mulligans: int
    expected_utility: float
    reject_continuation_value: float
    acceptance_probability: float
    expected_future_mulligans: float
    optional_keep_states: frozenset[SetupHandState]


@dataclass(frozen=True)
class CountDependentPolicy:
    prefix_steps: tuple[CountPolicyStep, ...]
    tail_step: CountPolicyStep
    tail_policy: OptimalSetupPolicy

    @property
    def start(self) -> CountPolicyStep:
        return self.prefix_steps[0] if self.prefix_steps else self.tail_step


def optimize_count_dependent_mulligan_penalty(
    deck_size: int,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int],
    terminal_value: HandValue,
    *,
    prefix_marginal_penalties: Sequence[float],
    tail_marginal_penalty: float,
    opening_hand_size: int = 7,
) -> CountDependentPolicy:
    """Optimize setup when the next mulligan's marginal cost depends on count.

    prefix_marginal_penalties[m] is the cost paid when an opening seen after
    exactly m failed mulligans is rejected. Once the prefix is exhausted, every
    additional failed mulligan costs tail_marginal_penalty, giving an exact
    stationary tail rather than a truncated approximation.
    """
    prefix = tuple(float(value) for value in prefix_marginal_penalties)
    tail_penalty = float(tail_marginal_penalty)
    if any(value < 0 for value in (*prefix, tail_penalty)):
        raise ValueError("mulligan penalties must be non-negative")

    distribution = opening_hand_distribution(
        deck_size,
        forced_starters,
        optional_group_sizes,
        feature_group_sizes,
        opening_hand_size=opening_hand_size,
    )
    forced_probability = 0.0
    forced_value_mass = 0.0
    optional_states: list[tuple[SetupHandState, float, float]] = []
    for state, mass in distribution:
        value = float(terminal_value(state))
        if state.forced_in_hand > 0:
            forced_probability += mass
            forced_value_mass += mass * value
        elif sum(state.optional_counts) > 0:
            optional_states.append((state, mass, value))

    tail_policy = optimize_linear_mulligan_penalty(
        deck_size,
        forced_starters,
        optional_group_sizes,
        feature_group_sizes,
        terminal_value,
        opening_hand_size=opening_hand_size,
        mulligan_penalty=tail_penalty,
    )
    tail_step = CountPolicyStep(
        failed_mulligans=len(prefix),
        expected_utility=tail_policy.metrics.expected_utility,
        reject_continuation_value=(
            tail_policy.metrics.expected_utility - tail_penalty
        ),
        acceptance_probability=tail_policy.metrics.acceptance_probability,
        expected_future_mulligans=tail_policy.metrics.expected_mulligans,
        optional_keep_states=tail_policy.optional_keep_states,
    )

    next_value = tail_step.expected_utility
    next_mulligans = tail_step.expected_future_mulligans
    reverse_steps: list[CountPolicyStep] = []

    for failed_mulligans in range(len(prefix) - 1, -1, -1):
        reject_value = next_value - prefix[failed_mulligans]
        kept = [
            (state, mass, value)
            for state, mass, value in optional_states
            if value >= reject_value
        ]
        acceptance = forced_probability + sum(
            mass for _, mass, _ in kept
        )
        rejection = 1.0 - acceptance
        current_value = (
            forced_value_mass
            + sum(mass * value for _, mass, value in kept)
            + rejection * reject_value
        )
        current_mulligans = rejection * (1.0 + next_mulligans)
        step = CountPolicyStep(
            failed_mulligans=failed_mulligans,
            expected_utility=current_value,
            reject_continuation_value=reject_value,
            acceptance_probability=acceptance,
            expected_future_mulligans=current_mulligans,
            optional_keep_states=frozenset(state for state, _, _ in kept),
        )
        reverse_steps.append(step)
        next_value = current_value
        next_mulligans = current_mulligans

    return CountDependentPolicy(
        prefix_steps=tuple(reversed(reverse_steps)),
        tail_step=tail_step,
        tail_policy=tail_policy,
    )


def final_acceptance_source_masses(
    policy: CountDependentPolicy,
) -> tuple[tuple[int, float], ...]:
    """Return mass accepted at each prefix count plus the stationary tail.

    The final tuple uses the tail count, meaning "this count or later".
    """
    reach = 1.0
    masses: list[tuple[int, float]] = []
    for step in policy.prefix_steps:
        accepted = reach * step.acceptance_probability
        masses.append((step.failed_mulligans, accepted))
        reach *= 1.0 - step.acceptance_probability
    masses.append((policy.tail_step.failed_mulligans, reach))
    return tuple(masses)


def count_dependent_prize_distribution(
    deck_size: int,
    prize_count: int,
    *,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int],
    policy: CountDependentPolicy,
    opening_hand_size: int = 7,
) -> list[tuple[tuple[int, ...], float]]:
    """Return final Prize counts after a count-dependent setup policy.

    Prefix acceptance distributions are mixed by the probability of reaching
    and accepting at each count. Once the stationary tail is reached, repeated
    rejected tail hands do not further change the accepted-hand-conditioned
    Prize distribution, so the entire tail contributes one aggregate mixture
    component.
    """
    combined: dict[tuple[int, ...], float] = {}
    reach = 1.0

    for step in policy.prefix_steps:
        acceptance = step.acceptance_probability
        if acceptance > 0.0 and reach > 0.0:
            keep_states = step.optional_keep_states
            component = conditioned_prize_hand_distribution(
                deck_size,
                prize_count,
                forced_starters=forced_starters,
                optional_group_sizes=optional_group_sizes,
                feature_group_sizes=feature_group_sizes,
                optional_policy=lambda state, keep_states=keep_states: float(
                    state in keep_states
                ),
                opening_hand_size=opening_hand_size,
            )
            weight = reach * acceptance
            for counts, mass in component:
                combined[counts] = combined.get(counts, 0.0) + weight * mass
        reach *= 1.0 - acceptance

    if reach > 0.0:
        keep_states = policy.tail_step.optional_keep_states
        component = conditioned_prize_hand_distribution(
            deck_size,
            prize_count,
            forced_starters=forced_starters,
            optional_group_sizes=optional_group_sizes,
            feature_group_sizes=feature_group_sizes,
            optional_policy=lambda state, keep_states=keep_states: float(
                state in keep_states
            ),
            opening_hand_size=opening_hand_size,
        )
        for counts, mass in component:
            combined[counts] = combined.get(counts, 0.0) + reach * mass

    total = sum(combined.values())
    if abs(total - 1.0) > 1e-12:
        raise AssertionError(f"final Prize distribution has mass {total}")
    return sorted(combined.items())


def count_dependent_specific_class_prize_probability(
    deck_size: int,
    prize_count: int,
    *,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int],
    policy: CountDependentPolicy,
    class_index: int,
    opening_hand_size: int = 7,
) -> float:
    """Return one labeled class member's final Prize probability."""
    optional = tuple(optional_group_sizes)
    features = tuple(feature_group_sizes)
    filler = deck_size - forced_starters - sum(optional) - sum(features)
    category_sizes = (forced_starters, *optional, *features, filler)
    if not 0 <= class_index < len(category_sizes):
        raise ValueError("class_index is out of range")
    class_size = category_sizes[class_index]
    if class_size <= 0:
        raise ValueError("requested class contains no cards")

    expected_prized = sum(
        counts[class_index] * mass
        for counts, mass in count_dependent_prize_distribution(
            deck_size,
            prize_count,
            forced_starters=forced_starters,
            optional_group_sizes=optional,
            feature_group_sizes=features,
            policy=policy,
            opening_hand_size=opening_hand_size,
        )
    )
    return expected_prized / class_size
