"""Exact same-turn access probabilities for a target Supporter with typed connectors.

This isolates one timing distinction in Pokemon TCG search graphs. Some connectors
can obtain a target Supporter while preserving the Supporter play for the turn
(e.g. Items or Abilities). Other connectors are themselves Supporters and consume
one Supporter play before the target can be played.

The model conditions on a valid starter-containing opening hand, sets Prize cards
from the remaining deck, and optionally observes later random draws before the
same-turn access check.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Iterator

from lock_state_kernel import PlayerChannels
from turn_action_budget import TurnAction, TurnActionBudget


@dataclass(frozen=True)
class SupporterAccessResult:
    """Exact same-turn target-Supporter access probabilities."""

    state_mass: float
    typed_access_probability: float
    naive_access_probability: float
    naive_only_probability: float


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
    denominator = _choose(sum(sizes), sample_size)
    numerator = 1
    for size, count in zip(sizes, counts):
        numerator *= _choose(size, count)
    return numerator / denominator


def accepted_opening_probability(
    deck_size: int, starter_cards: int, opening_hand_size: int = 7
) -> float:
    """Return P(a random opening hand contains at least one setup-eligible starter)."""
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must be between 0 and deck_size")
    if not 0 <= opening_hand_size <= deck_size:
        raise ValueError("opening_hand_size must be between 0 and deck_size")
    if opening_hand_size == 0 or starter_cards == 0:
        return 0.0

    return 1.0 - _choose(deck_size - starter_cards, opening_hand_size) / _choose(
        deck_size, opening_hand_size
    )


def same_turn_supporter_access(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    target_supporters: int,
    preserving_starter_connectors: int = 0,
    preserving_nonstarter_connectors: int = 0,
    consuming_connectors: int = 0,
    opening_hand_size: int = 7,
    extra_random_draws: int = 0,
    supporter_plays_remaining: int | None = None,
    turn_budget: TurnActionBudget | None = None,
    player_channels: PlayerChannels | None = None,
) -> SupporterAccessResult:
    """Return exact same-turn access to a target Supporter.

    Categories are:
      target Supporters;
      Supporter-preserving setup-starter connectors;
      Supporter-preserving non-starter connectors;
      Supporter-consuming connectors;
      filler setup starters;
      filler non-starters.

    A preserving connector can search a target Supporter still in the deck without
    reducing "supporter_plays_remaining". A consuming connector first spends one
    Supporter play, so it can only search and then play the target in the same turn
    when at least two Supporter plays remain.

    Callers may provide either an explicit "supporter_plays_remaining" value or a
    canonical "turn_budget". When a budget is supplied, remaining Supporter quota
    is derived from its current usage, limit, and turn-ended state. An optional
    "player_channels" state then applies play permission; Supporter lock reduces
    executable capacity to zero without mutating quota history.

    "naive_access_probability" is the reachability result obtained by incorrectly
    treating both connector classes as if they preserve the Supporter play. It is
    included to quantify timing overstatement.
    """
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must be between 0 and deck_size")
    if min(
        target_supporters,
        preserving_starter_connectors,
        preserving_nonstarter_connectors,
        consuming_connectors,
    ) < 0:
        raise ValueError("target and connector counts must be non-negative")
    if preserving_starter_connectors > starter_cards:
        raise ValueError("preserving starter connectors exceed starter_cards")

    used_nonstarters = (
        target_supporters
        + preserving_nonstarter_connectors
        + consuming_connectors
    )
    if used_nonstarters > deck_size - starter_cards:
        raise ValueError("target/connectors exceed non-starter capacity")

    post_prize_deck = deck_size - opening_hand_size - prize_count
    if not 0 <= extra_random_draws <= post_prize_deck:
        raise ValueError("extra_random_draws must fit in the post-Prize deck")
    if turn_budget is not None:
        if supporter_plays_remaining is not None:
            raise ValueError(
                "provide either supporter_plays_remaining or turn_budget, not both"
            )
        supporter_plays_remaining = turn_budget.remaining(TurnAction.SUPPORTER)
    elif supporter_plays_remaining is None:
        supporter_plays_remaining = 1

    if supporter_plays_remaining < 0:
        raise ValueError("supporter_plays_remaining must be non-negative")
    if player_channels is not None and not player_channels.supporter_play:
        supporter_plays_remaining = 0

    filler_starters = starter_cards - preserving_starter_connectors
    filler_nonstarters = deck_size - starter_cards - used_nonstarters
    sizes = (
        target_supporters,
        preserving_starter_connectors,
        preserving_nonstarter_connectors,
        consuming_connectors,
        filler_starters,
        filler_nonstarters,
    )

    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    total_mass = 0.0
    typed_access = 0.0
    naive_access = 0.0
    naive_only = 0.0

    for hand in _bounded_compositions(opening_hand_size, sizes):
        if hand[1] + hand[4] == 0:
            continue

        hand_mass = _multivariate_probability(hand, sizes, opening_hand_size) / accepted
        after_hand = tuple(size - count for size, count in zip(sizes, hand))

        for prizes in _bounded_compositions(prize_count, after_hand):
            prize_mass = _multivariate_probability(prizes, after_hand, prize_count)
            after_prizes = tuple(
                size - count for size, count in zip(after_hand, prizes)
            )

            for draws in _bounded_compositions(extra_random_draws, after_prizes):
                draw_mass = _multivariate_probability(
                    draws, after_prizes, extra_random_draws
                )
                state_mass = hand_mass * prize_mass * draw_mass
                total_mass += state_mass

                if supporter_plays_remaining == 0:
                    continue

                target_in_hand = hand[0] + draws[0] > 0
                target_in_searchable_deck = after_prizes[0] - draws[0] > 0
                preserving_available = (
                    hand[1] + hand[2] + draws[1] + draws[2] > 0
                )
                consuming_available = hand[3] + draws[3] > 0

                preserving_line = preserving_available and target_in_searchable_deck
                consuming_line = (
                    supporter_plays_remaining >= 2
                    and consuming_available
                    and target_in_searchable_deck
                )
                typed_success = target_in_hand or preserving_line or consuming_line

                naive_line = (
                    (preserving_available or consuming_available)
                    and target_in_searchable_deck
                )
                naive_success = target_in_hand or naive_line

                typed_access += state_mass * typed_success
                naive_access += state_mass * naive_success
                naive_only += state_mass * (naive_success and not typed_success)

    return SupporterAccessResult(
        state_mass=total_mass,
        typed_access_probability=typed_access,
        naive_access_probability=naive_access,
        naive_only_probability=naive_only,
    )
