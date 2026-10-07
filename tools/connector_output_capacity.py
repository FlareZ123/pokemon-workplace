"""Exact two-channel access for connectors with different output capacities.

This isolates the tradeoff between a lower discard cost with one searched card
and a higher discard cost with enough simultaneous outputs to satisfy both
missing target channels.
"""

from __future__ import annotations

from dataclasses import dataclass

from connector_domination import (
    _bounded_compositions,
    _choose,
    _multivariate_probability,
    accepted_opening_probability,
)


@dataclass(frozen=True)
class OutputCapacityResult:
    """Exact joint-access result for one connector."""

    state_mass: float
    direct_joint_access: float
    joint_access: float
    one_missing_route: float
    one_missing_payable_route: float
    both_missing_route: float
    both_missing_payable_route: float


def two_channel_output_capacity_access(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_a_copies: int,
    target_b_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    connector_capacity: int,
    opening_hand_size: int = 7,
) -> OutputCapacityResult:
    """Return exact joint access with a one-copy multi-output connector.

    `connector_capacity=1` models a one-card universal search for this
    objective. `connector_capacity>=2` can satisfy both missing channels in
    the same action, provided both remain searchable after Prize placement.

    The two targets are assumed to be independently legal outputs of the
    connector. For a Secret Box interpretation, they must occupy distinct
    eligible search categories.
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
    if connector_capacity <= 0:
        raise ValueError("connector_capacity must be positive")

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

        remaining_a = target_a_copies - hand[0]
        remaining_b = target_b_copies - hand[1]
        missing_count = (
            int(not target_a_in_hand) + int(not target_b_in_hand)
        )

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

    joint_access = direct_joint + one_missing_payable
    if connector_capacity >= 2:
        joint_access += both_missing_payable

    return OutputCapacityResult(
        state_mass=total_mass,
        direct_joint_access=direct_joint,
        joint_access=joint_access,
        one_missing_route=one_missing_route,
        one_missing_payable_route=one_missing_payable,
        both_missing_route=both_missing_route,
        both_missing_payable_route=both_missing_payable,
    )
