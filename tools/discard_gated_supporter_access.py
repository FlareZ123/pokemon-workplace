"""Exact current-window target-Supporter access through a discard-gated connector.

The model conditions on a valid starter-containing opening hand and initial Prize
cards, then optionally adds later random draws before a same-window access check.
Setup-eligible starters are modeled as protected/non-disposable. The disposable
pool therefore consists only of non-starter cards currently acceptable to discard.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class DiscardGatedAccessResult:
    """Exact access probabilities with and without the connector's discard gate."""

    state_mass: float
    direct_target_probability: float
    naive_access_probability: float
    gated_access_probability: float
    gate_overstatement_probability: float
    connector_needed_probability: float
    connector_payability_given_needed: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(
    total: int, bounds: tuple[int, ...]
) -> Iterator[tuple[int, ...]]:
    """Yield tuples summing to total without exceeding per-category bounds."""

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
    """Return P(a random opening hand contains at least one setup-eligible starter)."""
    return 1.0 - _choose(
        deck_size - starter_cards, opening_hand_size
    ) / _choose(deck_size, opening_hand_size)


def discard_gated_supporter_access(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_supporters: int,
    connector_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int = 7,
    extra_random_draws: int = 0,
    spare_connectors_disposable: bool = False,
) -> DiscardGatedAccessResult:
    """Return exact target-Supporter access before the Supporter play.

    Categories are target Supporters, connector copies, disposable non-starters,
    protected setup starters, and protected non-starters.

    Naive access counts a connector in hand plus a target still in the deck as an
    out without checking its discard cost. Gated access additionally requires
    enough currently disposable cards in hand to pay the connector's cost.
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
        target_supporters,
        connector_copies,
        disposable_nonstarters,
        discard_cost,
    ) < 0:
        raise ValueError("counts and discard_cost must be non-negative")

    nonstarter_capacity = deck_size - starter_cards
    used_nonstarters = (
        target_supporters + connector_copies + disposable_nonstarters
    )
    if used_nonstarters > nonstarter_capacity:
        raise ValueError("non-starter categories exceed non-starter capacity")

    post_prize_deck = deck_size - opening_hand_size - prize_count
    if not 0 <= extra_random_draws <= post_prize_deck:
        raise ValueError("extra_random_draws must fit in the post-Prize deck")

    protected_nonstarters = nonstarter_capacity - used_nonstarters
    sizes = (
        target_supporters,
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
    direct_target = 0.0
    naive_access = 0.0
    gated_access = 0.0
    gate_overstatement = 0.0
    connector_needed = 0.0
    connector_payable = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[3] == 0:
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
                draw_mass = _multivariate_probability(
                    draws, after_prizes, extra_random_draws
                )
                state_mass = hand_mass * prize_mass * draw_mass
                total_mass += state_mass

                target_in_hand = hand[0] + draws[0] > 0
                connectors_in_hand = hand[1] + draws[1]
                target_in_searchable_deck = (
                    after_prizes[0] - draws[0] > 0
                )

                route_needed = (
                    not target_in_hand
                    and connectors_in_hand > 0
                    and target_in_searchable_deck
                )

                disposable = hand[2] + draws[2]
                if spare_connectors_disposable and connectors_in_hand > 1:
                    disposable += connectors_in_hand - 1
                route_payable = route_needed and disposable >= discard_cost

                direct_target += state_mass * target_in_hand

                naive_success = target_in_hand or route_needed
                gated_success = target_in_hand or route_payable
                naive_access += state_mass * naive_success
                gated_access += state_mass * gated_success
                gate_overstatement += state_mass * (
                    naive_success and not gated_success
                )
                connector_needed += state_mass * route_needed
                connector_payable += state_mass * route_payable

    conditional_payability = (
        connector_payable / connector_needed if connector_needed else 1.0
    )
    return DiscardGatedAccessResult(
        state_mass=total_mass,
        direct_target_probability=direct_target,
        naive_access_probability=naive_access,
        gated_access_probability=gated_access,
        gate_overstatement_probability=gate_overstatement,
        connector_needed_probability=connector_needed,
        connector_payability_given_needed=conditional_payability,
    )
