"""Exact turn-by-turn Prize rescue with typed one-shot connectors.

The model isolates timing for a Gladion-like rescue Supporter. It conditions on a
valid starter-containing opening hand, sets Prize cards from the remaining deck,
then simulates a specified number of rescue turns. Each modeled turn begins with
one random draw and provides one ordinary Supporter play.

Supporter-preserving connectors can search one rescue Supporter without consuming
the turn's Supporter play. Supporter-consuming connectors can search one rescue
Supporter but spend that turn's Supporter play, so the fetched rescuer can only be
played on a later modeled turn.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class RescueTurnResult:
    """Exact success probabilities for the modeled rescue horizon."""

    state_mass: float
    any_critical_prized: float
    success_probability: float
    conditional_success_probability: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _bounded_compositions(total: int, bounds: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    """Yield tuples summing to total without exceeding per-category bounds."""

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


def accepted_opening_probability(
    deck_size: int, starter_cards: int, opening_hand_size: int = 7
) -> float:
    """Return P(a random opening hand contains a setup-eligible starter)."""
    return 1.0 - _choose(deck_size - starter_cards, opening_hand_size) / _choose(
        deck_size, opening_hand_size
    )


@lru_cache(maxsize=None)
def _success_from_state(
    turns_remaining: int,
    critical_remaining: int,
    rescue_in_hand: int,
    preserving_in_hand: int,
    consuming_in_hand: int,
    rescue_in_deck: int,
    preserving_in_deck: int,
    consuming_in_deck: int,
    other_in_deck: int,
) -> float:
    if critical_remaining == 0:
        return 1.0
    if turns_remaining == 0:
        return 0.0

    deck_size = (
        rescue_in_deck
        + preserving_in_deck
        + consuming_in_deck
        + other_in_deck
    )
    if deck_size == 0:
        return 0.0

    probability = 0.0
    draw_categories = (
        rescue_in_deck,
        preserving_in_deck,
        consuming_in_deck,
        other_in_deck,
    )

    for category, count in enumerate(draw_categories):
        if count == 0:
            continue

        hand_rescue = rescue_in_hand
        hand_preserving = preserving_in_hand
        hand_consuming = consuming_in_hand
        deck_rescue = rescue_in_deck
        deck_preserving = preserving_in_deck
        deck_consuming = consuming_in_deck
        deck_other = other_in_deck

        if category == 0:
            hand_rescue += 1
            deck_rescue -= 1
        elif category == 1:
            hand_preserving += 1
            deck_preserving -= 1
        elif category == 2:
            hand_consuming += 1
            deck_consuming -= 1
        else:
            deck_other -= 1

        action_values = [
            _success_from_state(
                turns_remaining - 1,
                critical_remaining,
                hand_rescue,
                hand_preserving,
                hand_consuming,
                deck_rescue,
                deck_preserving,
                deck_consuming,
                deck_other,
            )
        ]

        if hand_rescue > 0:
            action_values.append(
                _success_from_state(
                    turns_remaining - 1,
                    critical_remaining - 1,
                    hand_rescue - 1,
                    hand_preserving,
                    hand_consuming,
                    deck_rescue,
                    deck_preserving,
                    deck_consuming,
                    deck_other,
                )
            )

        if hand_preserving > 0 and deck_rescue > 0:
            action_values.append(
                _success_from_state(
                    turns_remaining - 1,
                    critical_remaining - 1,
                    hand_rescue,
                    hand_preserving - 1,
                    hand_consuming,
                    deck_rescue - 1,
                    deck_preserving,
                    deck_consuming,
                    deck_other,
                )
            )

        if hand_consuming > 0 and deck_rescue > 0:
            action_values.append(
                _success_from_state(
                    turns_remaining - 1,
                    critical_remaining,
                    hand_rescue + 1,
                    hand_preserving,
                    hand_consuming - 1,
                    deck_rescue - 1,
                    deck_preserving,
                    deck_consuming,
                    deck_other,
                )
            )

        probability += (count / deck_size) * max(action_values)

    return probability


def rescue_success_by_turns(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_supporters: int,
    preserving_starter_connectors: int = 0,
    preserving_nonstarter_connectors: int = 0,
    consuming_connectors: int = 0,
    opening_hand_size: int = 7,
    rescue_turns: int = 1,
) -> RescueTurnResult:
    """Return P(all initially Prized criticals are rescued within rescue_turns).

    Every modeled turn has one random draw followed by one ordinary Supporter play.
    Connectors are one-shot and deterministic once usable. Search effects shuffle
    implicitly because future draws depend only on remaining category counts.
    """
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must be between 0 and deck_size")
    if min(
        critical_starter,
        critical_nonstarter,
        rescue_supporters,
        preserving_starter_connectors,
        preserving_nonstarter_connectors,
        consuming_connectors,
    ) < 0:
        raise ValueError("card counts must be non-negative")
    if critical_starter + preserving_starter_connectors > starter_cards:
        raise ValueError("starter-class special cards exceed starter_cards")

    nonstarter_specials = (
        critical_nonstarter
        + rescue_supporters
        + preserving_nonstarter_connectors
        + consuming_connectors
    )
    if nonstarter_specials > deck_size - starter_cards:
        raise ValueError("non-starter special cards exceed non-starter capacity")
    if rescue_turns < 0:
        raise ValueError("rescue_turns must be non-negative")

    filler_starter = (
        starter_cards - critical_starter - preserving_starter_connectors
    )
    filler_nonstarter = deck_size - starter_cards - nonstarter_specials
    sizes = (
        critical_starter,
        critical_nonstarter,
        rescue_supporters,
        preserving_starter_connectors,
        preserving_nonstarter_connectors,
        consuming_connectors,
        filler_starter,
        filler_nonstarter,
    )

    accepted = accepted_opening_probability(
        deck_size, starter_cards, opening_hand_size
    )
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    total_mass = 0.0
    any_critical = 0.0
    successful_critical_mass = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[0] + hand[3] + hand[6] == 0:
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
            preserving_in_deck = (
                after_hand[3]
                - prizes[3]
                + after_hand[4]
                - prizes[4]
            )
            consuming_in_deck = after_hand[5] - prizes[5]
            post_prize_deck_size = deck_size - opening_hand_size - prize_count
            other_in_deck = (
                post_prize_deck_size
                - rescue_in_deck
                - preserving_in_deck
                - consuming_in_deck
            )

            state_success = _success_from_state(
                rescue_turns,
                critical_prized,
                hand[2],
                hand[3] + hand[4],
                hand[5],
                rescue_in_deck,
                preserving_in_deck,
                consuming_in_deck,
                other_in_deck,
            )
            successful_critical_mass += state_mass * state_success

    conditional_success = (
        successful_critical_mass / any_critical if any_critical else 1.0
    )
    return RescueTurnResult(
        state_mass=total_mass,
        any_critical_prized=any_critical,
        success_probability=successful_critical_mass,
        conditional_success_probability=conditional_success,
    )
