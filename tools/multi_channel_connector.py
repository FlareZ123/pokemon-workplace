"""Exact same-window access for one connector across many target channels.

The model supports up to a modest number of abstract target channels and uses
inclusion-exclusion to integrate Prize placement analytically. It is intended
for comparing one-output universal search with multi-output category search.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from connector_domination import (
    _bounded_compositions,
    _choose,
    _multivariate_probability,
    accepted_opening_probability,
)


@dataclass(frozen=True)
class MultiChannelConnectorResult:
    """Exact joint-access result across all required channels."""

    state_mass: float
    direct_joint_access: float
    joint_access: float
    connector_route_by_missing_count: tuple[float, ...]
    payable_route_by_missing_count: tuple[float, ...]


def multi_channel_connector_access(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_counts: Sequence[int],
    disposable_nonstarters: int,
    discard_cost: int,
    connector_capacity: int,
    opening_hand_size: int = 7,
) -> MultiChannelConnectorResult:
    """Return exact probability of satisfying every target channel.

    There is exactly one connector. Each target channel is an independent
    search output class. The connector can satisfy at most
    `connector_capacity` missing channels in one action.

    For a Secret Box interpretation, every target channel must map to a
    distinct eligible search category.
    """

    targets = tuple(target_counts)
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not targets or min(targets) <= 0:
        raise ValueError("target_counts must be non-empty and positive")
    if connector_capacity <= 0:
        raise ValueError("connector_capacity must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("invalid prize_count")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in deck")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in deck")
    if disposable_nonstarters < 0 or discard_cost < 0:
        raise ValueError("disposable count and discard cost must be non-negative")

    connector_copies = 1
    used_nonstarters = (
        sum(targets) + connector_copies + disposable_nonstarters
    )
    nonstarter_capacity = deck_size - starter_cards
    if used_nonstarters > nonstarter_capacity:
        raise ValueError("non-starter categories exceed capacity")

    protected_nonstarters = nonstarter_capacity - used_nonstarters
    target_count = len(targets)
    connector_index = target_count
    disposable_index = target_count + 1
    starter_index = target_count + 2
    sizes = (
        *targets,
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

    def all_selected_copies_prized_probability(copies: int) -> float:
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
    joint_access = 0.0
    route_by_missing = [0.0] * (target_count + 1)
    payable_by_missing = [0.0] * (target_count + 1)

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[starter_index] == 0:
            continue

        hand_mass = (
            _multivariate_probability(hand, sizes, opening_hand_size) / accepted
        )
        total_mass += hand_mass

        missing = [
            index for index in range(target_count)
            if hand[index] == 0
        ]
        if not missing:
            direct_joint += hand_mass
            joint_access += hand_mass
            continue

        if hand[connector_index] == 0:
            continue

        remaining = [
            targets[index] - hand[index] for index in missing
        ]

        # Inclusion-exclusion over events E_i = "all remaining copies of
        # missing channel i are Prized". The desired event is that none of
        # the E_i occur, so every missing channel retains a searchable copy.
        all_searchable_probability = 0.0
        for subset_size in range(len(remaining) + 1):
            sign = -1.0 if subset_size % 2 else 1.0
            for subset in combinations(range(len(remaining)), subset_size):
                selected_copies = sum(remaining[index] for index in subset)
                all_searchable_probability += (
                    sign
                    * all_selected_copies_prized_probability(selected_copies)
                )

        missing_count = len(missing)
        route_mass = hand_mass * all_searchable_probability
        route_by_missing[missing_count] += route_mass

        payable = hand[disposable_index] >= discard_cost
        if payable:
            payable_by_missing[missing_count] += route_mass
            if missing_count <= connector_capacity:
                joint_access += route_mass

    return MultiChannelConnectorResult(
        state_mass=total_mass,
        direct_joint_access=direct_joint,
        joint_access=joint_access,
        connector_route_by_missing_count=tuple(route_by_missing),
        payable_route_by_missing_count=tuple(payable_by_missing),
    )
