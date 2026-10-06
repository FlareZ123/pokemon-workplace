"""Exact deck-state access using finite connector outcome profiles.

This combines valid-opening conditioning, Prize cards, optional random exposure,
and the deterministic capacity solver from connector_capacity.py.

Targets and connector types are modeled as non-starters. Connector profile
availability is state-local input. Timing, costs, locks, and other requirements
should be resolved before constructing the profiles.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator, Sequence

from connector_capacity import (
    ConnectorType,
    evaluate_connector_capacity,
)


@dataclass(frozen=True)
class ConnectorProfileAccessResult:
    """Exact valid-start-conditioned joint access probabilities."""

    state_mass: float
    individual_access_probabilities: tuple[float, ...]
    true_joint_access_probability: float
    naive_joint_access_probability: float
    connector_contention_probability: float
    contention_given_naive_joint: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(
    total: int,
    bounds: tuple[int, ...],
) -> Iterator[tuple[int, ...]]:
    """Yield non-negative tuples summing to total within category bounds."""

    def visit(
        index: int,
        remaining: int,
        prefix: tuple[int, ...],
    ) -> Iterator[tuple[int, ...]]:
        if index == len(bounds) - 1:
            if 0 <= remaining <= bounds[index]:
                yield prefix + (remaining,)
            return

        for value in range(min(bounds[index], remaining) + 1):
            yield from visit(
                index + 1,
                remaining - value,
                prefix + (value,),
            )

    yield from visit(0, total, ())


def _multivariate_probability(
    counts: tuple[int, ...],
    sizes: tuple[int, ...],
    sample_size: int,
) -> float:
    numerator = 1
    for size, count in zip(sizes, counts):
        numerator *= _choose(size, count)
    return numerator / _choose(sum(sizes), sample_size)


def accepted_opening_probability(
    deck_size: int,
    starter_cards: int,
    opening_hand_size: int = 7,
) -> float:
    """Return P(opening hand contains at least one setup-eligible starter)."""

    return 1.0 - _choose(
        deck_size - starter_cards,
        opening_hand_size,
    ) / _choose(deck_size, opening_hand_size)


def connector_profile_access(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_copies: Sequence[int],
    connector_types: Sequence[ConnectorType],
    opening_hand_size: int = 7,
    extra_random_draws: int = 0,
) -> ConnectorProfileAccessResult:
    """Return exact joint access with state-exposed finite connector capacity.

    Each ConnectorType.copies value is its count in the deck. Its profiles are
    the outcome vectors a single exposed copy may realize in the modeled state.

    A target channel is already satisfied when at least one copy is exposed into
    hand. If absent from hand, at least one copy must remain in the searchable
    deck and the exposed connectors must jointly cover that target demand.
    """

    targets = tuple(target_copies)
    connectors = tuple(connector_types)
    if not targets:
        raise ValueError("target_copies must contain at least one target channel")
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in the deck")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening hand must fit before Prize cards")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(*targets, extra_random_draws) < 0:
        raise ValueError("target counts and extra_random_draws must be non-negative")

    target_count = len(targets)
    for connector in connectors:
        if connector.copies < 0:
            raise ValueError("connector copies must be non-negative")
        if not connector.profiles:
            raise ValueError("connector profiles cannot be empty")
        for profile in connector.profiles:
            if len(profile) != target_count:
                raise ValueError("profile length must match target count")

    connector_counts = tuple(
        connector.copies
        for connector in connectors
    )
    used_nonstarters = (
        sum(targets) + sum(connector_counts)
    )
    nonstarter_capacity = deck_size - starter_cards
    if used_nonstarters > nonstarter_capacity:
        raise ValueError("modeled non-starter cards exceed deck capacity")

    post_prize_deck = deck_size - opening_hand_size - prize_count
    if extra_random_draws > post_prize_deck:
        raise ValueError("extra_random_draws must fit in the post-Prize deck")

    filler_nonstarters = nonstarter_capacity - used_nonstarters
    connector_start = target_count
    starter_index = target_count + len(connectors)
    sizes = targets + connector_counts + (
        starter_cards,
        filler_nonstarters,
    )

    accepted = accepted_opening_probability(
        deck_size,
        starter_cards,
        opening_hand_size,
    )
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    state_mass = 0.0
    individual_access = [0.0] * target_count
    true_joint_access = 0.0
    naive_joint_access = 0.0
    contention = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[starter_index] == 0:
            continue

        hand_mass = (
            _multivariate_probability(
                hand,
                sizes,
                opening_hand_size,
            )
            / accepted
        )
        after_hand = tuple(
            size - count
            for size, count in zip(sizes, hand)
        )

        for prizes in _bounded_compositions(
            prize_count,
            after_hand,
        ):
            prize_mass = _multivariate_probability(
                prizes,
                after_hand,
                prize_count,
            )
            after_prizes = tuple(
                size - count
                for size, count in zip(after_hand, prizes)
            )

            for draws in _bounded_compositions(
                extra_random_draws,
                after_prizes,
            ):
                draw_mass = _multivariate_probability(
                    draws,
                    after_prizes,
                    extra_random_draws,
                )
                mass = hand_mass * prize_mass * draw_mass
                state_mass += mass

                in_hand = tuple(
                    hand[index] + draws[index]
                    for index in range(target_count)
                )
                in_deck = tuple(
                    after_prizes[index] - draws[index]
                    for index in range(target_count)
                )

                exposed_connectors = tuple(
                    ConnectorType(
                        connector.name,
                        hand[connector_start + index]
                        + draws[connector_start + index],
                        connector.profiles,
                    )
                    for index, connector in enumerate(connectors)
                )

                reachable = []
                for target_index in range(target_count):
                    if in_hand[target_index] > 0:
                        reachable.append(True)
                        continue
                    if in_deck[target_index] == 0:
                        reachable.append(False)
                        continue

                    reachable.append(
                        any(
                            connector.copies > 0
                            and any(
                                profile[target_index] > 0
                                for profile in connector.profiles
                            )
                            for connector in exposed_connectors
                        )
                    )

                for index, is_reachable in enumerate(reachable):
                    individual_access[index] += mass * is_reachable

                naive_joint = all(reachable)
                all_targets_exist = all(
                    hand_count > 0 or deck_count > 0
                    for hand_count, deck_count in zip(
                        in_hand,
                        in_deck,
                    )
                )

                if all_targets_exist:
                    demand = tuple(
                        int(hand_count == 0)
                        for hand_count in in_hand
                    )
                    capacity = evaluate_connector_capacity(
                        demand,
                        exposed_connectors,
                    )
                    true_joint = capacity.exact_joint_feasible
                else:
                    true_joint = False

                naive_joint_access += mass * naive_joint
                true_joint_access += mass * true_joint
                contention += mass * (
                    naive_joint and not true_joint
                )

    conditional_contention = (
        contention / naive_joint_access
        if naive_joint_access
        else 0.0
    )
    return ConnectorProfileAccessResult(
        state_mass=state_mass,
        individual_access_probabilities=tuple(individual_access),
        true_joint_access_probability=true_joint_access,
        naive_joint_access_probability=naive_joint_access,
        connector_contention_probability=contention,
        contention_given_naive_joint=conditional_contention,
    )
