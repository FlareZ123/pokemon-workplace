"""Exact turn-by-turn Prize rescue through Xtransceiver-like stochastic Items.

The model conditions on a valid starter-containing opening hand, sets Prize cards
from the remaining deck, then simulates a fixed number of rescue turns. Each turn
begins with one random draw and allows any number of one-shot Item connectors
before at most one rescue Supporter play.

A connector is consumed when played. With ``hit_probability=0.5`` it models
Xtransceiver's coin flip for the narrow purpose of finding a rescue Supporter.
On a hit it searches one rescue Supporter from deck to hand; on a miss it only
consumes the connector. The optimizer may retry with another copy, play a rescuer,
or hold remaining copies for later turns.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class StochasticConnectorRescueResult:
    """Exact success probabilities for a stochastic preserving connector."""

    state_mass: float
    any_critical_prized: float
    success_probability: float
    conditional_success_probability: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(total: int, bounds: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    def visit(index: int, remaining: int, prefix: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if index == len(bounds) - 1:
            if 0 <= remaining <= bounds[index]:
                yield prefix + (remaining,)
            return
        for value in range(min(bounds[index], remaining) + 1):
            yield from visit(index + 1, remaining - value, prefix + (value,))

    yield from visit(0, total, ())


def _multivariate_probability(
    counts: tuple[int, ...], sizes: tuple[int, ...], sample_size: int
) -> float:
    numerator = 1
    for size, count in zip(sizes, counts):
        numerator *= _choose(size, count)
    return numerator / _choose(sum(sizes), sample_size)


def accepted_opening_probability(deck_size: int, starter_cards: int, opening_hand_size: int = 7) -> float:
    """Return P(a random opening contains at least one setup-eligible starter)."""
    return 1.0 - _choose(deck_size - starter_cards, opening_hand_size) / _choose(
        deck_size, opening_hand_size
    )


def _finish_turn_without_more_connectors(
    turns_remaining: int,
    critical_remaining: int,
    rescue_in_hand: int,
    connector_in_hand: int,
    rescue_in_deck: int,
    connector_in_deck: int,
    other_in_deck: int,
    hit_numerator: int,
    hit_denominator: int,
    same_turn_retries: bool,
) -> float:
    """Choose whether to play the one rescue Supporter, with Item play closed."""
    best = _success_from_state(
        turns_remaining - 1,
        critical_remaining,
        rescue_in_hand,
        connector_in_hand,
        rescue_in_deck,
        connector_in_deck,
        other_in_deck,
        hit_numerator,
        hit_denominator,
        same_turn_retries,
    )
    if rescue_in_hand > 0:
        best = max(
            best,
            _success_from_state(
                turns_remaining - 1,
                critical_remaining - 1,
                rescue_in_hand - 1,
                connector_in_hand,
                rescue_in_deck,
                connector_in_deck,
                other_in_deck,
                hit_numerator,
                hit_denominator,
                same_turn_retries,
            ),
        )
    return best


@lru_cache(maxsize=None)
def _best_after_draw(
    turns_remaining: int,
    critical_remaining: int,
    rescue_in_hand: int,
    connector_in_hand: int,
    rescue_in_deck: int,
    connector_in_deck: int,
    other_in_deck: int,
    hit_numerator: int,
    hit_denominator: int,
    same_turn_retries: bool,
) -> float:
    """Optimize Item use and the one Supporter play after this turn's draw."""
    if critical_remaining == 0:
        return 1.0

    best = _finish_turn_without_more_connectors(
        turns_remaining,
        critical_remaining,
        rescue_in_hand,
        connector_in_hand,
        rescue_in_deck,
        connector_in_deck,
        other_in_deck,
        hit_numerator,
        hit_denominator,
        same_turn_retries,
    )

    if connector_in_hand > 0 and rescue_in_deck > 0:
        p = hit_numerator / hit_denominator
        if same_turn_retries:
            hit_value = _best_after_draw(
                turns_remaining,
                critical_remaining,
                rescue_in_hand + 1,
                connector_in_hand - 1,
                rescue_in_deck - 1,
                connector_in_deck,
                other_in_deck,
                hit_numerator,
                hit_denominator,
                same_turn_retries,
            )
            miss_value = _best_after_draw(
                turns_remaining,
                critical_remaining,
                rescue_in_hand,
                connector_in_hand - 1,
                rescue_in_deck,
                connector_in_deck,
                other_in_deck,
                hit_numerator,
                hit_denominator,
                same_turn_retries,
            )
        else:
            hit_value = _finish_turn_without_more_connectors(
                turns_remaining,
                critical_remaining,
                rescue_in_hand + 1,
                connector_in_hand - 1,
                rescue_in_deck - 1,
                connector_in_deck,
                other_in_deck,
                hit_numerator,
                hit_denominator,
                same_turn_retries,
            )
            miss_value = _finish_turn_without_more_connectors(
                turns_remaining,
                critical_remaining,
                rescue_in_hand,
                connector_in_hand - 1,
                rescue_in_deck,
                connector_in_deck,
                other_in_deck,
                hit_numerator,
                hit_denominator,
                same_turn_retries,
            )
        best = max(best, p * hit_value + (1.0 - p) * miss_value)

    return best


@lru_cache(maxsize=None)
def _success_from_state(
    turns_remaining: int,
    critical_remaining: int,
    rescue_in_hand: int,
    connector_in_hand: int,
    rescue_in_deck: int,
    connector_in_deck: int,
    other_in_deck: int,
    hit_numerator: int,
    hit_denominator: int,
    same_turn_retries: bool,
) -> float:
    if critical_remaining == 0:
        return 1.0
    if turns_remaining == 0:
        return 0.0

    deck_size = rescue_in_deck + connector_in_deck + other_in_deck
    if deck_size == 0:
        return 0.0

    probability = 0.0
    for category, count in enumerate((rescue_in_deck, connector_in_deck, other_in_deck)):
        if count == 0:
            continue

        hand_rescue = rescue_in_hand
        hand_connector = connector_in_hand
        deck_rescue = rescue_in_deck
        deck_connector = connector_in_deck
        deck_other = other_in_deck

        if category == 0:
            hand_rescue += 1
            deck_rescue -= 1
        elif category == 1:
            hand_connector += 1
            deck_connector -= 1
        else:
            deck_other -= 1

        probability += (count / deck_size) * _best_after_draw(
            turns_remaining,
            critical_remaining,
            hand_rescue,
            hand_connector,
            deck_rescue,
            deck_connector,
            deck_other,
            hit_numerator,
            hit_denominator,
            same_turn_retries,
        )

    return probability


def rescue_success_with_stochastic_connector(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_supporters: int,
    connector_copies: int,
    opening_hand_size: int = 7,
    rescue_turns: int = 1,
    hit_numerator: int = 1,
    hit_denominator: int = 2,
    same_turn_retries: bool = True,
) -> StochasticConnectorRescueResult:
    """Return exact rescue success for an Xtransceiver-like connector package."""
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
        rescue_turns,
        hit_numerator,
    ) < 0:
        raise ValueError("counts, horizon, and hit numerator must be non-negative")
    if hit_denominator <= 0 or hit_numerator > hit_denominator:
        raise ValueError("hit probability must be in [0, 1]")
    if critical_starter > starter_cards:
        raise ValueError("critical_starter exceeds starter_cards")

    nonstarter_specials = critical_nonstarter + rescue_supporters + connector_copies
    if nonstarter_specials > deck_size - starter_cards:
        raise ValueError("non-starter categories exceed non-starter capacity")

    filler_starter = starter_cards - critical_starter
    protected_nonstarter = deck_size - starter_cards - nonstarter_specials
    sizes = (
        critical_starter,
        critical_nonstarter,
        rescue_supporters,
        connector_copies,
        filler_starter,
        protected_nonstarter,
    )

    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    _best_after_draw.cache_clear()
    _success_from_state.cache_clear()
    total_mass = 0.0
    any_critical = 0.0
    successful_critical_mass = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[0] + hand[4] == 0:
            continue

        hand_mass = _multivariate_probability(hand, sizes, opening_hand_size) / accepted
        after_hand = tuple(size - count for size, count in zip(sizes, hand))

        for prizes in _bounded_compositions(prize_count, after_hand):
            prize_mass = _multivariate_probability(prizes, after_hand, prize_count)
            state_mass = hand_mass * prize_mass
            total_mass += state_mass

            critical_prized = prizes[0] + prizes[1]
            if critical_prized == 0:
                continue
            any_critical += state_mass

            rescue_in_deck = after_hand[2] - prizes[2]
            connector_in_deck = after_hand[3] - prizes[3]
            post_prize_deck_size = deck_size - opening_hand_size - prize_count
            other_in_deck = post_prize_deck_size - rescue_in_deck - connector_in_deck

            state_success = _success_from_state(
                rescue_turns,
                critical_prized,
                hand[2],
                hand[3],
                rescue_in_deck,
                connector_in_deck,
                other_in_deck,
                hit_numerator,
                hit_denominator,
                same_turn_retries,
            )
            successful_critical_mass += state_mass * state_success

    conditional_success = successful_critical_mass / any_critical if any_critical else 1.0
    return StochasticConnectorRescueResult(
        state_mass=total_mass,
        any_critical_prized=any_critical,
        success_probability=successful_critical_mass,
        conditional_success_probability=conditional_success,
    )
