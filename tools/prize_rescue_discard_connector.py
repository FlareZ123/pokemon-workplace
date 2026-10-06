"""Exact Prize rescue with a discard-gated preserving connector.

The model conditions on a valid starter-containing opening hand and initial Prize
cards, then simulates rescue turns. Each turn begins with one random draw and has
one ordinary Supporter play. The connector preserves that Supporter play but
requires a fixed number of currently disposable non-starter cards from hand.

After each draw, dynamic programming chooses how many connector copies to spend
before playing at most one rescue Supporter. Waiting is also a legal choice, so
the solver preserves the option value of future random draws when that is better.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class DiscardConnectorRescueResult:
    """Exact success probabilities for the discard-gated rescue horizon."""

    state_mass: float
    any_critical_prized: float
    success_probability: float
    conditional_success_probability: float


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


@lru_cache(maxsize=None)
def _success_from_state(
    turns_remaining: int,
    critical_remaining: int,
    rescue_in_hand: int,
    connector_in_hand: int,
    disposable_in_hand: int,
    rescue_in_deck: int,
    connector_in_deck: int,
    disposable_in_deck: int,
    other_in_deck: int,
    discard_cost: int,
) -> float:
    if critical_remaining == 0:
        return 1.0
    if turns_remaining == 0:
        return 0.0

    deck_size = (
        rescue_in_deck
        + connector_in_deck
        + disposable_in_deck
        + other_in_deck
    )
    if deck_size == 0:
        return 0.0

    probability = 0.0
    draw_categories = (
        rescue_in_deck,
        connector_in_deck,
        disposable_in_deck,
        other_in_deck,
    )

    for category, count in enumerate(draw_categories):
        if count == 0:
            continue

        hand_rescue = rescue_in_hand
        hand_connector = connector_in_hand
        hand_disposable = disposable_in_hand
        deck_rescue = rescue_in_deck
        deck_connector = connector_in_deck
        deck_disposable = disposable_in_deck
        deck_other = other_in_deck

        if category == 0:
            hand_rescue += 1
            deck_rescue -= 1
        elif category == 1:
            hand_connector += 1
            deck_connector -= 1
        elif category == 2:
            hand_disposable += 1
            deck_disposable -= 1
        else:
            deck_other -= 1

        action_values = [
            _success_from_state(
                turns_remaining - 1,
                critical_remaining,
                hand_rescue,
                hand_connector,
                hand_disposable,
                deck_rescue,
                deck_connector,
                deck_disposable,
                deck_other,
                discard_cost,
            )
        ]

        if discard_cost == 0:
            payable_connectors = hand_connector
        else:
            payable_connectors = min(
                hand_connector, hand_disposable // discard_cost
            )
        max_searches = min(
            payable_connectors,
            deck_rescue,
            critical_remaining,
        )

        for searches in range(max_searches + 1):
            rescue_after_search = hand_rescue + searches
            if rescue_after_search == 0:
                continue

            action_values.append(
                _success_from_state(
                    turns_remaining - 1,
                    critical_remaining - 1,
                    rescue_after_search - 1,
                    hand_connector - searches,
                    hand_disposable - searches * discard_cost,
                    deck_rescue - searches,
                    deck_connector,
                    deck_disposable,
                    deck_other,
                    discard_cost,
                )
            )

        probability += (count / deck_size) * max(action_values)

    return probability


def rescue_success_with_discard_connector(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_supporters: int,
    connector_copies: int,
    disposable_nonstarters: int,
    discard_cost: int,
    opening_hand_size: int = 7,
    rescue_turns: int = 1,
) -> DiscardConnectorRescueResult:
    """Return exact rescue success with a preserving discard-gated connector."""
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(
        critical_starter,
        critical_nonstarter,
        rescue_supporters,
        connector_copies,
        disposable_nonstarters,
        discard_cost,
        rescue_turns,
    ) < 0:
        raise ValueError("counts and horizon must be non-negative")
    if critical_starter > starter_cards:
        raise ValueError("critical_starter exceeds starter_cards")

    nonstarter_specials = (
        critical_nonstarter
        + rescue_supporters
        + connector_copies
        + disposable_nonstarters
    )
    if nonstarter_specials > deck_size - starter_cards:
        raise ValueError("non-starter categories exceed non-starter capacity")

    filler_starter = starter_cards - critical_starter
    protected_nonstarter = (
        deck_size - starter_cards - nonstarter_specials
    )
    sizes = (
        critical_starter,
        critical_nonstarter,
        rescue_supporters,
        connector_copies,
        disposable_nonstarters,
        filler_starter,
        protected_nonstarter,
    )

    accepted = accepted_opening_probability(
        deck_size, starter_cards, opening_hand_size
    )
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    _success_from_state.cache_clear()
    total_mass = 0.0
    any_critical = 0.0
    successful_critical_mass = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[0] + hand[5] == 0:
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

            critical_prized = prizes[0] + prizes[1]
            if critical_prized == 0:
                continue
            any_critical += state_mass

            rescue_in_deck = after_hand[2] - prizes[2]
            connector_in_deck = after_hand[3] - prizes[3]
            disposable_in_deck = after_hand[4] - prizes[4]
            post_prize_deck_size = deck_size - opening_hand_size - prize_count
            other_in_deck = (
                post_prize_deck_size
                - rescue_in_deck
                - connector_in_deck
                - disposable_in_deck
            )

            state_success = _success_from_state(
                rescue_turns,
                critical_prized,
                hand[2],
                hand[3],
                hand[4],
                rescue_in_deck,
                connector_in_deck,
                disposable_in_deck,
                other_in_deck,
                discard_cost,
            )
            successful_critical_mass += state_mass * state_success

    conditional_success = (
        successful_critical_mass / any_critical if any_critical else 1.0
    )
    return DiscardConnectorRescueResult(
        state_mass=total_mass,
        any_critical_prized=any_critical,
        success_probability=successful_critical_mass,
        conditional_success_probability=conditional_success,
    )
