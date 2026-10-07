"""Exact two-channel access through one discard-gated universal connector.

This module formalizes connector domination for a narrow same-window state.
The deck contains two target channels, one single-use universal connector,
currently disposable non-starters, protected setup starters, and protected
non-starters.

The opening hand is conditioned on containing at least one setup-eligible
starter. Prize cards are then sampled from the remaining deck. The connector
resembles Computer Search when ``discard_cost=2``: it can find any one card
from the searchable deck but can only satisfy one missing target channel.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class ConnectorDominationResult:
    """Exact same-window joint-access probabilities."""

    state_mass: float
    direct_joint_access: float
    capacity_aware_no_cost_access: float
    capacity_aware_gated_access: float
    naive_shared_connector_gated_access: float
    naive_shared_connector_no_cost_access: float
    connector_capacity_overstatement: float
    discard_gate_loss: float
    combined_naive_overstatement: float
    one_missing_connector_route: float
    one_missing_payable_route: float
    one_missing_payability: float
    both_missing_connector_route: float
    both_missing_payable_route: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(
    total: int, bounds: tuple[int, ...]
) -> Iterator[tuple[int, ...]]:
    """Yield tuples summing to total without exceeding category bounds."""

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
    """Return P(the opening hand contains a setup-eligible starter)."""

    return 1.0 - _choose(
        deck_size - starter_cards, opening_hand_size
    ) / _choose(deck_size, opening_hand_size)


def two_channel_connector_access(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_a_copies: int,
    target_b_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int = 7,
) -> ConnectorDominationResult:
    """Return exact joint access to two target channels.

    The model contains exactly one universal connector. It can search for one
    card in the remaining deck after setup, so it can repair exactly one
    missing target channel.

    ``capacity_aware_no_cost_access`` respects that one-search capacity but
    ignores the discard gate.

    ``capacity_aware_gated_access`` is the realistic result under the modeled
    binary disposable/protected split.

    ``naive_shared_connector_gated_access`` keeps the discard gate but commits
    the connector-domination error: if the same connector makes each missing
    target individually reachable, it treats all missing channels as jointly
    reachable.

    ``naive_shared_connector_no_cost_access`` additionally ignores the
    connector's discard cost.

    Only the explicitly modeled disposable non-starters count as discard
    fodder. Extra target copies and setup starters remain protected. This is a
    conservative binary DCI abstraction, not a claim that those cards can
    never be discarded in a real game.
    """

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(
        target_a_copies,
        target_b_copies,
        disposable_nonstarters,
        discard_cost,
    ) < 0:
        raise ValueError("card counts and discard_cost must be non-negative")
    if target_a_copies == 0 or target_b_copies == 0:
        raise ValueError("both target channels need at least one deck copy")

    connector_copies = 1
    used_nonstarters = (
        target_a_copies
        + target_b_copies
        + connector_copies
        + disposable_nonstarters
    )
    nonstarter_capacity = deck_size - starter_cards
    if used_nonstarters > nonstarter_capacity:
        raise ValueError("non-starter categories exceed non-starter capacity")

    protected_nonstarters = nonstarter_capacity - used_nonstarters
    sizes = (
        target_a_copies,
        target_b_copies,
        connector_copies,
        disposable_nonstarters,
        starter_cards,
        protected_nonstarters,
    )

    accepted = accepted_opening_probability(
        deck_size, starter_cards, opening_hand_size
    )
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    total_mass = 0.0
    direct_joint = 0.0
    capacity_no_cost = 0.0
    capacity_gated = 0.0
    naive_gated = 0.0
    naive_no_cost = 0.0
    one_missing_route = 0.0
    one_missing_payable = 0.0
    both_missing_route = 0.0
    both_missing_payable = 0.0

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
            state_mass = hand_mass * prize_mass
            total_mass += state_mass

            target_a_in_hand = hand[0] > 0
            target_b_in_hand = hand[1] > 0
            connector_in_hand = hand[2] > 0

            post_prize_deck = tuple(
                count - prized for count, prized in zip(after_hand, prizes)
            )
            target_a_searchable = post_prize_deck[0] > 0
            target_b_searchable = post_prize_deck[1] > 0

            direct_success = target_a_in_hand and target_b_in_hand
            missing_count = int(not target_a_in_hand) + int(not target_b_in_hand)

            missing_target_searchable = (
                (not target_a_in_hand and target_a_searchable)
                or (not target_b_in_hand and target_b_searchable)
            )
            one_missing = (
                connector_in_hand
                and missing_count == 1
                and missing_target_searchable
            )
            connector_payable = (
                connector_in_hand and hand[3] >= discard_cost
            )
            one_missing_paid = one_missing and connector_payable

            both_missing = (
                connector_in_hand
                and not target_a_in_hand
                and not target_b_in_hand
                and target_a_searchable
                and target_b_searchable
            )
            both_missing_paid = both_missing and connector_payable

            capacity_no_cost_success = direct_success or one_missing
            capacity_gated_success = direct_success or one_missing_paid

            all_channels_individually_reachable = (
                (target_a_in_hand or target_a_searchable)
                and (target_b_in_hand or target_b_searchable)
            )
            naive_gated_success = direct_success or (
                connector_payable and all_channels_individually_reachable
            )
            naive_no_cost_success = direct_success or (
                connector_in_hand and all_channels_individually_reachable
            )

            direct_joint += state_mass * direct_success
            capacity_no_cost += state_mass * capacity_no_cost_success
            capacity_gated += state_mass * capacity_gated_success
            naive_gated += state_mass * naive_gated_success
            naive_no_cost += state_mass * naive_no_cost_success
            one_missing_route += state_mass * one_missing
            one_missing_payable += state_mass * one_missing_paid
            both_missing_route += state_mass * both_missing
            both_missing_payable += state_mass * both_missing_paid

    one_missing_payability = (
        one_missing_payable / one_missing_route
        if one_missing_route
        else 1.0
    )

    return ConnectorDominationResult(
        state_mass=total_mass,
        direct_joint_access=direct_joint,
        capacity_aware_no_cost_access=capacity_no_cost,
        capacity_aware_gated_access=capacity_gated,
        naive_shared_connector_gated_access=naive_gated,
        naive_shared_connector_no_cost_access=naive_no_cost,
        connector_capacity_overstatement=naive_gated - capacity_gated,
        discard_gate_loss=capacity_no_cost - capacity_gated,
        combined_naive_overstatement=naive_no_cost - capacity_gated,
        one_missing_connector_route=one_missing_route,
        one_missing_payable_route=one_missing_payable,
        one_missing_payability=one_missing_payability,
        both_missing_connector_route=both_missing_route,
        both_missing_payable_route=both_missing_payable,
    )


def two_channel_connector_access_collapsed(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_a_copies: int,
    target_b_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int = 7,
) -> ConnectorDominationResult:
    """Return the same exact result while integrating Prize states analytically.

    This function is mathematically equivalent to
    `two_channel_connector_access` for the same-window model. It enumerates
    accepted opening-hand category compositions only.

    Conditional on one hand composition, a missing target class is searchable
    after Prize placement unless every remaining copy of that class is Prized.
    Those probabilities have closed forms, so explicit Prize-composition
    enumeration is unnecessary.
    """

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(
        target_a_copies,
        target_b_copies,
        disposable_nonstarters,
        discard_cost,
    ) < 0:
        raise ValueError("card counts and discard_cost must be non-negative")
    if target_a_copies == 0 or target_b_copies == 0:
        raise ValueError("both target channels need at least one deck copy")

    connector_copies = 1
    nonstarter_capacity = deck_size - starter_cards
    used_nonstarters = (
        target_a_copies
        + target_b_copies
        + connector_copies
        + disposable_nonstarters
    )
    if used_nonstarters > nonstarter_capacity:
        raise ValueError("non-starter categories exceed non-starter capacity")

    protected_nonstarters = nonstarter_capacity - used_nonstarters
    sizes = (
        target_a_copies,
        target_b_copies,
        connector_copies,
        disposable_nonstarters,
        starter_cards,
        protected_nonstarters,
    )

    accepted = accepted_opening_probability(
        deck_size, starter_cards, opening_hand_size
    )
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    cards_after_hand = deck_size - opening_hand_size
    prize_denominator = _choose(cards_after_hand, prize_count)

    def all_copies_prized_probability(copies: int) -> float:
        if copies == 0:
            return 1.0
        if copies > prize_count:
            return 0.0
        return (
            _choose(cards_after_hand - copies, prize_count - copies)
            / prize_denominator
        )

    total_mass = 0.0
    direct_joint = 0.0
    one_missing_route = 0.0
    one_missing_payable = 0.0
    both_missing_route = 0.0
    both_missing_payable = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[4] == 0:
            continue

        hand_mass = (
            _multivariate_probability(hand, sizes, opening_hand_size) / accepted
        )
        total_mass += hand_mass

        target_a_in_hand = hand[0] > 0
        target_b_in_hand = hand[1] > 0
        connector_in_hand = hand[2] > 0
        connector_payable = (
            connector_in_hand and hand[3] >= discard_cost
        )

        if target_a_in_hand and target_b_in_hand:
            direct_joint += hand_mass
            continue

        if not connector_in_hand:
            continue

        missing_count = (
            int(not target_a_in_hand) + int(not target_b_in_hand)
        )
        remaining_a = target_a_copies - hand[0]
        remaining_b = target_b_copies - hand[1]

        if missing_count == 1:
            missing_copies = (
                remaining_a if not target_a_in_hand else remaining_b
            )
            searchable_probability = (
                1.0 - all_copies_prized_probability(missing_copies)
            )
            route_mass = hand_mass * searchable_probability
            one_missing_route += route_mass
            if connector_payable:
                one_missing_payable += route_mass
            continue

        all_a_prized = all_copies_prized_probability(remaining_a)
        all_b_prized = all_copies_prized_probability(remaining_b)
        all_both_prized = all_copies_prized_probability(
            remaining_a + remaining_b
        )
        both_searchable_probability = (
            1.0 - all_a_prized - all_b_prized + all_both_prized
        )
        route_mass = hand_mass * both_searchable_probability
        both_missing_route += route_mass
        if connector_payable:
            both_missing_payable += route_mass

    capacity_no_cost = direct_joint + one_missing_route
    capacity_gated = direct_joint + one_missing_payable
    naive_gated = (
        direct_joint + one_missing_payable + both_missing_payable
    )
    naive_no_cost = (
        direct_joint + one_missing_route + both_missing_route
    )
    conditional_payability = (
        one_missing_payable / one_missing_route
        if one_missing_route
        else 1.0
    )

    return ConnectorDominationResult(
        state_mass=total_mass,
        direct_joint_access=direct_joint,
        capacity_aware_no_cost_access=capacity_no_cost,
        capacity_aware_gated_access=capacity_gated,
        naive_shared_connector_gated_access=naive_gated,
        naive_shared_connector_no_cost_access=naive_no_cost,
        connector_capacity_overstatement=(
            naive_gated - capacity_gated
        ),
        discard_gate_loss=capacity_no_cost - capacity_gated,
        combined_naive_overstatement=naive_no_cost - capacity_gated,
        one_missing_connector_route=one_missing_route,
        one_missing_payable_route=one_missing_payable,
        one_missing_payability=conditional_payability,
        both_missing_connector_route=both_missing_route,
        both_missing_payable_route=both_missing_payable,
    )
