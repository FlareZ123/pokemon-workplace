"""Exact setup policy optimization from grouped opening-hand state.

The model separates:
- forced starters, whose presence ends the mulligan sequence;
- optional setup groups, which let the player keep an otherwise Basic-less hand;
- feature groups, which may affect the strategic value of a kept opening;
- filler cards.

Under a stationary policy and a constant utility penalty per failed mulligan,
optional-only hands have an exact threshold policy: keep when the terminal hand
value is at least the continuation value after rejecting the hand.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import product
from math import comb, inf


@dataclass(frozen=True)
class SetupHandState:
    forced_in_hand: int
    optional_counts: tuple[int, ...]
    feature_counts: tuple[int, ...]
    filler_in_hand: int


@dataclass(frozen=True)
class PolicyMetrics:
    acceptance_probability: float
    expected_mulligans: float
    expected_terminal_value: float
    expected_utility: float


@dataclass(frozen=True)
class OptimalSetupPolicy:
    metrics: PolicyMetrics
    keep_value_floor: float
    optional_keep_states: frozenset[SetupHandState]


HandValue = Callable[[SetupHandState], float]
OptionalHandPolicy = Callable[[SetupHandState], float]


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _validate(
    deck_size: int,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int],
    opening_hand_size: int,
) -> tuple[tuple[int, ...], tuple[int, ...], int]:
    optional = tuple(optional_group_sizes)
    features = tuple(feature_group_sizes)
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if forced_starters < 0 or any(size < 0 for size in (*optional, *features)):
        raise ValueError("card counts must be non-negative")
    represented = forced_starters + sum(optional) + sum(features)
    if represented > deck_size:
        raise ValueError("card counts exceed deck size")
    if not 0 <= opening_hand_size <= deck_size:
        raise ValueError("opening_hand_size must be between 0 and deck_size")
    return optional, features, deck_size - represented


def opening_hand_distribution(
    deck_size: int,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int] = (),
    *,
    opening_hand_size: int = 7,
) -> list[tuple[SetupHandState, float]]:
    """Return exact grouped opening-hand states and their probabilities."""
    optional, features, filler = _validate(
        deck_size,
        forced_starters,
        optional_group_sizes,
        feature_group_sizes,
        opening_hand_size,
    )
    denominator = _choose(deck_size, opening_hand_size)
    if denominator == 0:
        return []

    category_sizes = (forced_starters, *optional, *features)
    ranges = [range(min(size, opening_hand_size) + 1) for size in category_sizes]
    states: list[tuple[SetupHandState, float]] = []

    for counts in product(*ranges):
        filler_in_hand = opening_hand_size - sum(counts)
        if not 0 <= filler_in_hand <= filler:
            continue
        ways = _choose(filler, filler_in_hand)
        for size, count in zip(category_sizes, counts):
            ways *= _choose(size, count)
        if ways == 0:
            continue

        optional_end = 1 + len(optional)
        state = SetupHandState(
            forced_in_hand=counts[0],
            optional_counts=tuple(counts[1:optional_end]),
            feature_counts=tuple(counts[optional_end:]),
            filler_in_hand=filler_in_hand,
        )
        states.append((state, ways / denominator))
    return states


def _optional_available(state: SetupHandState) -> bool:
    return state.forced_in_hand == 0 and sum(state.optional_counts) > 0


def opening_acceptance_hand_policy(
    deck_size: int,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int],
    optional_policy: OptionalHandPolicy,
    *,
    opening_hand_size: int = 7,
) -> float:
    """Return per-attempt acceptance under a stationary hand-state policy."""
    accepted = 0.0
    for state, mass in opening_hand_distribution(
        deck_size,
        forced_starters,
        optional_group_sizes,
        feature_group_sizes,
        opening_hand_size=opening_hand_size,
    ):
        if state.forced_in_hand > 0:
            keep_probability = 1.0
        elif _optional_available(state):
            keep_probability = float(optional_policy(state))
            if not 0.0 <= keep_probability <= 1.0:
                raise ValueError("optional_policy must return a value between 0 and 1")
        else:
            keep_probability = 0.0
        accepted += mass * keep_probability
    return accepted


def stationary_policy_metrics(
    deck_size: int,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int],
    terminal_value: HandValue,
    optional_policy: OptionalHandPolicy,
    *,
    opening_hand_size: int = 7,
    mulligan_penalty: float = 0.0,
) -> PolicyMetrics:
    """Evaluate a stationary setup policy exactly.

    mulligan_penalty is an additive utility cost for each failed opening hand.
    It can represent a linearized cost of the opponent's optional bonus draw,
    information leakage, time, or another repeated-mulligan externality.
    """
    if mulligan_penalty < 0:
        raise ValueError("mulligan_penalty must be non-negative")

    acceptance = 0.0
    terminal_value_mass = 0.0
    for state, mass in opening_hand_distribution(
        deck_size,
        forced_starters,
        optional_group_sizes,
        feature_group_sizes,
        opening_hand_size=opening_hand_size,
    ):
        if state.forced_in_hand > 0:
            keep_probability = 1.0
        elif _optional_available(state):
            keep_probability = float(optional_policy(state))
            if not 0.0 <= keep_probability <= 1.0:
                raise ValueError("optional_policy must return a value between 0 and 1")
        else:
            keep_probability = 0.0

        if keep_probability:
            acceptance += mass * keep_probability
            terminal_value_mass += mass * keep_probability * float(terminal_value(state))

    if acceptance == 0.0:
        raise ValueError("policy can never accept an opening hand")

    expected_mulligans = (1.0 - acceptance) / acceptance
    expected_terminal_value = terminal_value_mass / acceptance
    return PolicyMetrics(
        acceptance_probability=acceptance,
        expected_mulligans=expected_mulligans,
        expected_terminal_value=expected_terminal_value,
        expected_utility=expected_terminal_value - mulligan_penalty * expected_mulligans,
    )


def optimize_linear_mulligan_penalty(
    deck_size: int,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int],
    terminal_value: HandValue,
    *,
    opening_hand_size: int = 7,
    mulligan_penalty: float = 0.0,
) -> OptimalSetupPolicy:
    """Return the optimal stationary optional-hand policy.

    With a constant cost per failed mulligan, the Bellman comparison on an
    optional-only hand is keep_value >= expected_utility - mulligan_penalty.
    Therefore an optimal stationary policy is a threshold in terminal hand
    value. The finite grouped state space lets us evaluate every distinct
    threshold exactly.
    """
    if mulligan_penalty < 0:
        raise ValueError("mulligan_penalty must be non-negative")

    forced_probability = 0.0
    forced_value_mass = 0.0
    optional_states: list[tuple[SetupHandState, float, float]] = []

    for state, mass in opening_hand_distribution(
        deck_size,
        forced_starters,
        optional_group_sizes,
        feature_group_sizes,
        opening_hand_size=opening_hand_size,
    ):
        value = float(terminal_value(state))
        if state.forced_in_hand > 0:
            forced_probability += mass
            forced_value_mass += mass * value
        elif _optional_available(state):
            optional_states.append((state, mass, value))

    cutoffs = [inf, *sorted({value for _, _, value in optional_states}, reverse=True)]
    best: OptimalSetupPolicy | None = None

    for cutoff in cutoffs:
        kept = [(state, mass, value) for state, mass, value in optional_states if value >= cutoff]
        acceptance = forced_probability + sum(mass for _, mass, _ in kept)
        if acceptance == 0.0:
            continue
        terminal_value_mass = forced_value_mass + sum(mass * value for _, mass, value in kept)
        expected_mulligans = (1.0 - acceptance) / acceptance
        expected_terminal_value = terminal_value_mass / acceptance
        expected_utility = expected_terminal_value - mulligan_penalty * expected_mulligans
        metrics = PolicyMetrics(
            acceptance_probability=acceptance,
            expected_mulligans=expected_mulligans,
            expected_terminal_value=expected_terminal_value,
            expected_utility=expected_utility,
        )
        solution = OptimalSetupPolicy(
            metrics=metrics,
            keep_value_floor=expected_utility - mulligan_penalty,
            optional_keep_states=frozenset(state for state, _, _ in kept),
        )
        if best is None or expected_utility > best.metrics.expected_utility + 1e-15:
            best = solution
        elif abs(expected_utility - best.metrics.expected_utility) <= 1e-15:
            if acceptance > best.metrics.acceptance_probability:
                best = solution

    if best is None:
        raise ValueError("no stationary policy can accept an opening hand")
    return best


def conditioned_prize_hand_distribution(
    deck_size: int,
    prize_count: int,
    *,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int],
    optional_policy: OptionalHandPolicy,
    opening_hand_size: int = 7,
) -> list[tuple[tuple[int, ...], float]]:
    """Return exact Prize class counts conditioned on the accepted opening.

    State order is forced starters, optional groups, feature groups, filler.
    """
    optional, features, filler = _validate(
        deck_size,
        forced_starters,
        optional_group_sizes,
        feature_group_sizes,
        opening_hand_size,
    )
    if prize_count < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")

    total_acceptance = opening_acceptance_hand_policy(
        deck_size,
        forced_starters,
        optional,
        features,
        optional_policy,
        opening_hand_size=opening_hand_size,
    )
    if total_acceptance == 0.0:
        raise ValueError("conditioning event has zero probability")

    category_sizes = (forced_starters, *optional, *features, filler)
    denominator = _choose(deck_size, prize_count)
    ranges = [range(min(size, prize_count) + 1) for size in category_sizes]
    states: list[tuple[tuple[int, ...], float]] = []

    for prize_counts in product(*ranges):
        if sum(prize_counts) != prize_count:
            continue
        ways = 1
        for size, count in zip(category_sizes, prize_counts):
            ways *= _choose(size, count)
        if ways == 0:
            continue

        index = 0
        remaining_forced = forced_starters - prize_counts[index]
        index += 1
        remaining_optional = tuple(
            size - count
            for size, count in zip(optional, prize_counts[index : index + len(optional)])
        )
        index += len(optional)
        remaining_features = tuple(
            size - count
            for size, count in zip(features, prize_counts[index : index + len(features)])
        )

        acceptance_given_prizes = opening_acceptance_hand_policy(
            deck_size - prize_count,
            remaining_forced,
            remaining_optional,
            remaining_features,
            optional_policy,
            opening_hand_size=opening_hand_size,
        )
        mass = (ways / denominator) * acceptance_given_prizes / total_acceptance
        if mass:
            states.append((prize_counts, mass))
    return states


def specific_class_card_prize_probability(
    deck_size: int,
    prize_count: int,
    *,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    feature_group_sizes: Sequence[int],
    optional_policy: OptionalHandPolicy,
    class_index: int,
    opening_hand_size: int = 7,
) -> float:
    """Return the Prize probability of one labeled card in a represented class."""
    optional, features, filler = _validate(
        deck_size,
        forced_starters,
        optional_group_sizes,
        feature_group_sizes,
        opening_hand_size,
    )
    category_sizes = (forced_starters, *optional, *features, filler)
    if not 0 <= class_index < len(category_sizes):
        raise ValueError("class_index is out of range")
    class_size = category_sizes[class_index]
    if class_size <= 0:
        raise ValueError("requested class contains no cards")

    expected_prized = sum(
        counts[class_index] * mass
        for counts, mass in conditioned_prize_hand_distribution(
            deck_size,
            prize_count,
            forced_starters=forced_starters,
            optional_group_sizes=optional,
            feature_group_sizes=features,
            optional_policy=optional_policy,
            opening_hand_size=opening_hand_size,
        )
    )
    return expected_prized / class_size
