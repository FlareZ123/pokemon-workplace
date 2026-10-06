"""Exact two-channel access with shared-connector capacity and discard gates.

A shared connector may search either of two required target channels, one target
per physical connector copy, and requires a fixed number of disposable cards from
hand for each use.

The model compares four evaluations:
* naive: connector copies are reusable across target channels and costs are ignored;
* capacity-only: physical connector copies cannot be reused, costs are ignored;
* discard-only naive: the discard gate is enforced but the same connector may still
  be reused across target channels;
* full: both one-use connector capacity and discard costs are enforced.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class CompoundConstraintResult:
    state_mass: float
    naive_joint_probability: float
    capacity_only_probability: float
    discard_only_naive_probability: float
    full_joint_probability: float
    capacity_error_probability: float
    discard_error_probability: float
    combined_error_probability: float
    constraint_overlap_probability: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(
    total: int, bounds: tuple[int, ...]
) -> Iterator[tuple[int, ...]]:
    def visit(
        index: int, remaining: int, prefix: tuple[int, ...]
    ) -> Iterator[tuple[int, ...]]:
        if index == len(bounds) - 1:
            if 0 <= remaining <= bounds[index]:
                yield prefix + (remaining,)
            return
        for value in range(min(bounds[index], remaining) + 1):
            yield from visit(
                index + 1, remaining - value, prefix + (value,)
            )

    yield from visit(0, total, ())


def _multivariate_probability(
    counts: tuple[int, ...], sizes: tuple[int, ...], sample_size: int
) -> float:
    numerator = 1
    for size, count in zip(sizes, counts):
        numerator *= _choose(size, count)
    return numerator / _choose(sum(sizes), sample_size)


def accepted_opening_probability(
    deck_size: int, starter_cards: int, opening_hand_size: int = 7
) -> float:
    return 1.0 - _choose(
        deck_size - starter_cards, opening_hand_size
    ) / _choose(deck_size, opening_hand_size)


def compound_connector_constraints(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_a_copies: int,
    target_b_copies: int,
    connector_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int = 7,
    extra_random_draws: int = 0,
) -> CompoundConstraintResult:
    """Return exact joint access under capacity and discard constraints."""
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in the deck")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(
        target_a_copies,
        target_b_copies,
        connector_copies,
        disposable_nonstarters,
        discard_cost,
        extra_random_draws,
    ) < 0:
        raise ValueError("counts and discard cost must be non-negative")

    used_nonstarters = (
        target_a_copies
        + target_b_copies
        + connector_copies
        + disposable_nonstarters
    )
    if used_nonstarters > deck_size - starter_cards:
        raise ValueError("modeled non-starters exceed deck capacity")

    post_prize_deck = deck_size - opening_hand_size - prize_count
    if extra_random_draws > post_prize_deck:
        raise ValueError("extra_random_draws must fit in the post-Prize deck")

    sizes = (
        target_a_copies,
        target_b_copies,
        connector_copies,
        disposable_nonstarters,
        starter_cards,
        deck_size - starter_cards - used_nonstarters,
    )
    accepted = accepted_opening_probability(
        deck_size, starter_cards, opening_hand_size
    )

    mass = 0.0
    naive_joint = 0.0
    capacity_only = 0.0
    discard_only_naive = 0.0
    full_joint = 0.0
    capacity_error = 0.0
    discard_error = 0.0
    combined_error = 0.0
    overlap = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[4] == 0:
            continue

        hand_mass = (
            _multivariate_probability(hand, sizes, opening_hand_size) / accepted
        )
        after_hand = tuple(size - count for size, count in zip(sizes, hand))

        for prizes in _bounded_compositions(prize_count, after_hand):
            prize_mass = _multivariate_probability(
                prizes, after_hand, prize_count
            )
            after_prizes = tuple(
                size - count for size, count in zip(after_hand, prizes)
            )

            for draws in _bounded_compositions(
                extra_random_draws, after_prizes
            ):
                state_mass = (
                    hand_mass
                    * prize_mass
                    * _multivariate_probability(
                        draws, after_prizes, extra_random_draws
                    )
                )
                mass += state_mass

                a_direct = hand[0] + draws[0] > 0
                b_direct = hand[1] + draws[1] > 0
                connectors = hand[2] + draws[2]
                disposable = hand[3] + draws[3]
                a_in_deck = after_prizes[0] - draws[0] > 0
                b_in_deck = after_prizes[1] - draws[1] > 0

                a_naive = a_direct or (
                    connectors > 0 and a_in_deck
                )
                b_naive = b_direct or (
                    connectors > 0 and b_in_deck
                )
                naive = a_naive and b_naive

                missing = int(not a_direct) + int(not b_direct)
                both_targets_exist = (
                    (a_direct or a_in_deck)
                    and (b_direct or b_in_deck)
                )
                capacity = (
                    both_targets_exist and connectors >= missing
                    if missing
                    else True
                )

                if discard_cost == 0:
                    payable_connectors = connectors
                else:
                    payable_connectors = min(
                        connectors, disposable // discard_cost
                    )

                a_gated = a_direct or (
                    payable_connectors > 0 and a_in_deck
                )
                b_gated = b_direct or (
                    payable_connectors > 0 and b_in_deck
                )
                gated_naive = a_gated and b_gated

                full = (
                    both_targets_exist
                    and payable_connectors >= missing
                    if missing
                    else True
                )

                capacity_failure = naive and not capacity
                discard_failure = naive and not gated_naive
                combined_failure = naive and not full

                naive_joint += state_mass * naive
                capacity_only += state_mass * capacity
                discard_only_naive += state_mass * gated_naive
                full_joint += state_mass * full
                capacity_error += state_mass * capacity_failure
                discard_error += state_mass * discard_failure
                combined_error += state_mass * combined_failure
                overlap += state_mass * (
                    capacity_failure and discard_failure
                )

    return CompoundConstraintResult(
        state_mass=mass,
        naive_joint_probability=naive_joint,
        capacity_only_probability=capacity_only,
        discard_only_naive_probability=discard_only_naive,
        full_joint_probability=full_joint,
        capacity_error_probability=capacity_error,
        discard_error_probability=discard_error,
        combined_error_probability=combined_error,
        constraint_overlap_probability=overlap,
    )
