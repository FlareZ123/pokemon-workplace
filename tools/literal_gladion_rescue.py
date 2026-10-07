"""Exact timed Prize rescue with literal Gladion Prize-zone cycling.

Gladion does not simply go to the discard pile after resolving. It takes one
face-down Prize card into hand, then the played Gladion is shuffled into the
remaining Prize cards. This model keeps that destination explicit and optimizes
whether to rescue an initially critical Prize, exchange for a Prized Gladion,
or wait.

For the isolated objective used by the repository's Prize-rescue baselines,
Prized Gladion copies are strategically inert: exchanging one Gladion for another
leaves the projected rescue state unchanged while consuming the current Supporter
window. The public result exposes the literal state so this projection equivalence
can be tested rather than assumed.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class LiteralGladionResult:
    """Exact setup-conditioned success probability for literal Gladion."""

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
    return 1.0 - _choose(deck_size - starter_cards, opening_hand_size) / _choose(
        deck_size, opening_hand_size
    )


@lru_cache(maxsize=None)
def literal_state_success(
    turns_remaining: int,
    critical_in_prizes: int,
    gladion_in_hand: int,
    gladion_in_prizes: int,
    gladion_in_deck: int,
    other_in_deck: int,
) -> float:
    """Optimal success from a literal Gladion state before the turn's draw."""
    if critical_in_prizes == 0:
        return 1.0
    if turns_remaining == 0:
        return 0.0

    deck_size = gladion_in_deck + other_in_deck
    if deck_size == 0:
        return 0.0

    probability = 0.0
    for draw_is_gladion, count in ((True, gladion_in_deck), (False, other_in_deck)):
        if count == 0:
            continue

        hand = gladion_in_hand + int(draw_is_gladion)
        deck_gladion = gladion_in_deck - int(draw_is_gladion)
        deck_other = other_in_deck - int(not draw_is_gladion)

        best = literal_state_success(
            turns_remaining - 1,
            critical_in_prizes,
            hand,
            gladion_in_prizes,
            deck_gladion,
            deck_other,
        )

        if hand > 0:
            best = max(
                best,
                literal_state_success(
                    turns_remaining - 1,
                    critical_in_prizes - 1,
                    hand - 1,
                    gladion_in_prizes + 1,
                    deck_gladion,
                    deck_other,
                ),
            )

            if gladion_in_prizes > 0:
                best = max(
                    best,
                    literal_state_success(
                        turns_remaining - 1,
                        critical_in_prizes,
                        hand,
                        gladion_in_prizes,
                        deck_gladion,
                        deck_other,
                    ),
                )

        probability += (count / deck_size) * best

    return probability


@lru_cache(maxsize=None)
def consumed_projection_success(
    turns_remaining: int,
    critical_remaining: int,
    rescue_in_hand: int,
    rescue_in_deck: int,
    other_in_deck: int,
) -> float:
    """The consumed-rescuer projection used by earlier isolated rescue models."""
    if critical_remaining == 0:
        return 1.0
    if turns_remaining == 0:
        return 0.0

    deck_size = rescue_in_deck + other_in_deck
    if deck_size == 0:
        return 0.0

    probability = 0.0
    for draw_is_rescuer, count in ((True, rescue_in_deck), (False, other_in_deck)):
        if count == 0:
            continue

        hand = rescue_in_hand + int(draw_is_rescuer)
        deck_rescue = rescue_in_deck - int(draw_is_rescuer)
        deck_other = other_in_deck - int(not draw_is_rescuer)

        best = consumed_projection_success(
            turns_remaining - 1,
            critical_remaining,
            hand,
            deck_rescue,
            deck_other,
        )
        if hand > 0:
            best = max(
                best,
                consumed_projection_success(
                    turns_remaining - 1,
                    critical_remaining - 1,
                    hand - 1,
                    deck_rescue,
                    deck_other,
                ),
            )
        probability += (count / deck_size) * best

    return probability


def literal_gladion_rescue_success(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    gladion_copies: int,
    opening_hand_size: int = 7,
    rescue_turns: int = 1,
) -> LiteralGladionResult:
    """Return exact success while preserving Gladion's Prize-zone destination."""
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 < starter_cards <= deck_size:
        raise ValueError("starter_cards must be positive and fit in the deck")
    if min(critical_starter, critical_nonstarter, gladion_copies, rescue_turns) < 0:
        raise ValueError("counts and horizon must be non-negative")
    if critical_starter > starter_cards:
        raise ValueError("critical_starter exceeds starter_cards")

    nonstarter_specials = critical_nonstarter + gladion_copies
    if nonstarter_specials > deck_size - starter_cards:
        raise ValueError("non-starter categories exceed non-starter capacity")

    filler_starter = starter_cards - critical_starter
    filler_nonstarter = deck_size - starter_cards - nonstarter_specials
    sizes = (
        critical_starter,
        critical_nonstarter,
        gladion_copies,
        filler_starter,
        filler_nonstarter,
    )

    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    literal_state_success.cache_clear()
    consumed_projection_success.cache_clear()
    total_mass = 0.0
    any_critical = 0.0
    successful_critical_mass = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[0] + hand[3] == 0:
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

            gladion_in_deck = after_hand[2] - prizes[2]
            post_prize_deck_size = deck_size - opening_hand_size - prize_count
            other_in_deck = post_prize_deck_size - gladion_in_deck

            state_success = literal_state_success(
                rescue_turns,
                critical_prized,
                hand[2],
                prizes[2],
                gladion_in_deck,
                other_in_deck,
            )
            successful_critical_mass += state_mass * state_success

    conditional_success = successful_critical_mass / any_critical if any_critical else 1.0
    return LiteralGladionResult(
        state_mass=total_mass,
        any_critical_prized=any_critical,
        success_probability=successful_critical_mass,
        conditional_success_probability=conditional_success,
    )
