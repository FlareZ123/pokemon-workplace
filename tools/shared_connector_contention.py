"""Exact joint-access loss from one-shot shared connector contention.

The model asks whether two distinct required channels can both be satisfied from
an accessible hand plus one-shot connectors that may search either target.

A naive reachability graph can count the same physical connector as an out to
both targets at once. The exact model enforces connector capacity: each connector
copy in hand can satisfy at most one missing target channel.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class SharedConnectorResult:
    """Valid-start-conditioned access probabilities for two target channels."""

    state_mass: float
    target_a_access_probability: float
    target_b_access_probability: float
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


def shared_connector_contention(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_a_copies: int,
    target_b_copies: int,
    shared_connector_copies: int,
    opening_hand_size: int = 7,
    extra_random_draws: int = 0,
) -> SharedConnectorResult:
    """Return exact access with one-use connectors shared by two target channels.

    Target A, target B, and shared connectors are modeled as non-starters.
    A connector in the accessible hand may search exactly one missing target
    from the remaining deck. It cannot satisfy both channels simultaneously.

    Naive joint access deliberately makes one graph error: it tests target A and
    target B independently, allowing the same connector copy to count as an out
    to both channels.
    """

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in the deck")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening hand must fit before Prize cards")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(
        target_a_copies,
        target_b_copies,
        shared_connector_copies,
        extra_random_draws,
    ) < 0:
        raise ValueError("card counts and extra_random_draws must be non-negative")

    used_nonstarters = (
        target_a_copies
        + target_b_copies
        + shared_connector_copies
    )
    nonstarter_capacity = deck_size - starter_cards
    if used_nonstarters > nonstarter_capacity:
        raise ValueError("modeled non-starter cards exceed deck capacity")

    post_prize_deck = deck_size - opening_hand_size - prize_count
    if extra_random_draws > post_prize_deck:
        raise ValueError("extra_random_draws must fit in the post-Prize deck")

    filler_nonstarters = nonstarter_capacity - used_nonstarters
    sizes = (
        target_a_copies,
        target_b_copies,
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
    target_a_access = 0.0
    target_b_access = 0.0
    true_joint_access = 0.0
    naive_joint_access = 0.0
    contention = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[3] == 0:
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

                a_in_hand = hand[0] + draws[0]
                b_in_hand = hand[1] + draws[1]
                connectors_in_hand = hand[2] + draws[2]

                a_in_deck = after_prizes[0] - draws[0]
                b_in_deck = after_prizes[1] - draws[1]

                a_accessible = (
                    a_in_hand > 0
                    or (
                        connectors_in_hand > 0
                        and a_in_deck > 0
                    )
                )
                b_accessible = (
                    b_in_hand > 0
                    or (
                        connectors_in_hand > 0
                        and b_in_deck > 0
                    )
                )
                naive_joint = a_accessible and b_accessible

                missing_targets = (
                    int(a_in_hand == 0)
                    + int(b_in_hand == 0)
                )
                both_targets_exist = (
                    (a_in_hand > 0 or a_in_deck > 0)
                    and (b_in_hand > 0 or b_in_deck > 0)
                )
                true_joint = (
                    both_targets_exist
                    and connectors_in_hand >= missing_targets
                )

                target_a_access += mass * a_accessible
                target_b_access += mass * b_accessible
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
    return SharedConnectorResult(
        state_mass=state_mass,
        target_a_access_probability=target_a_access,
        target_b_access_probability=target_b_access,
        true_joint_access_probability=true_joint_access,
        naive_joint_access_probability=naive_joint_access,
        connector_contention_probability=contention,
        contention_given_naive_joint=conditional_contention,
    )
