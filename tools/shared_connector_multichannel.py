"""Exact multichannel access with one-shot fully shared connectors.

Each accessible connector can search one missing target channel from the
remaining deck. The exact joint-access calculation enforces connector capacity.
A naive comparison deliberately evaluates every target channel independently,
which allows one physical connector to satisfy several missing channels at once.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator, Sequence


@dataclass(frozen=True)
class MultichannelConnectorResult:
    """Valid-start-conditioned access probabilities for target channels."""

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


def multichannel_shared_connector_contention(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_copies: Sequence[int],
    shared_connector_copies: int,
    opening_hand_size: int = 7,
    extra_random_draws: int = 0,
) -> MultichannelConnectorResult:
    """Return exact joint access for any number of target channels.

    Each target channel is represented by a non-starter copy count. A shared
    connector in the accessible hand may search exactly one missing channel from
    the searchable deck.

    Naive joint access tests each target independently and therefore lets one
    connector copy count as an out to every missing channel.
    """

    targets = tuple(target_copies)
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
    if min(
        *targets,
        shared_connector_copies,
        extra_random_draws,
    ) < 0:
        raise ValueError("card counts and extra_random_draws must be non-negative")

    used_nonstarters = sum(targets) + shared_connector_copies
    nonstarter_capacity = deck_size - starter_cards
    if used_nonstarters > nonstarter_capacity:
        raise ValueError("modeled non-starter cards exceed deck capacity")

    post_prize_deck = deck_size - opening_hand_size - prize_count
    if extra_random_draws > post_prize_deck:
        raise ValueError("extra_random_draws must fit in the post-Prize deck")

    filler_nonstarters = nonstarter_capacity - used_nonstarters
    target_count = len(targets)
    connector_index = target_count
    starter_index = target_count + 1
    sizes = targets + (
        shared_connector_copies,
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

                target_in_hand = tuple(
                    hand[index] + draws[index]
                    for index in range(target_count)
                )
                target_in_deck = tuple(
                    after_prizes[index] - draws[index]
                    for index in range(target_count)
                )
                connectors_in_hand = (
                    hand[connector_index] + draws[connector_index]
                )

                accessible = tuple(
                    in_hand > 0
                    or (
                        connectors_in_hand > 0
                        and in_deck > 0
                    )
                    for in_hand, in_deck in zip(
                        target_in_hand,
                        target_in_deck,
                    )
                )
                for index, is_accessible in enumerate(accessible):
                    individual_access[index] += mass * is_accessible

                naive_joint = all(accessible)
                missing_channels = sum(
                    in_hand == 0
                    for in_hand in target_in_hand
                )
                all_channels_exist = all(
                    in_hand > 0 or in_deck > 0
                    for in_hand, in_deck in zip(
                        target_in_hand,
                        target_in_deck,
                    )
                )
                true_joint = (
                    all_channels_exist
                    and connectors_in_hand >= missing_channels
                )

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
    return MultichannelConnectorResult(
        state_mass=state_mass,
        individual_access_probabilities=tuple(individual_access),
        true_joint_access_probability=true_joint_access,
        naive_joint_access_probability=naive_joint_access,
        connector_contention_probability=contention,
        contention_given_naive_joint=conditional_contention,
    )
