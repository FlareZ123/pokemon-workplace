"""Exact timed Prize-rescue access with clean direct non-Supporter outs.

A direct out is an abstract non-starter card that, once exposed before a
Supporter window, can search one Gladion-like rescue Supporter from the
remaining deck into the hand without consuming that Supporter play.

The model preserves:
- accepted-opening conditioning;
- Prize cards drawn from the post-opening deck;
- cumulative random exposure by Supporter window;
- one rescue Supporter play per window;
- depletion of searchable rescue copies when direct outs are used.

Direct outs are intentionally abstract. Real cards can have costs, conditions,
lock exposure, Bench requirements, stochastic search, or opportunity costs.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import product
from math import comb
from typing import Sequence


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _validate_windows(
    cards_seen_by_window: Sequence[int],
    *,
    opening_hand_size: int,
) -> tuple[int, ...]:
    windows = tuple(cards_seen_by_window)
    previous = opening_hand_size
    for cards_seen in windows:
        if cards_seen < previous:
            raise ValueError(
                "cards_seen_by_window must be nondecreasing and include the opening hand"
            )
        previous = cards_seen
    return windows


def _success_probability_after_opening_and_prizes(
    *,
    rescue_in_hand: int,
    outs_in_hand: int,
    rescue_in_deck: int,
    outs_in_deck: int,
    other_in_deck: int,
    required_rescues: int,
    draw_segments: Sequence[int],
) -> float:
    """Return exact success probability for one accepted opening/Prize state."""

    states: dict[tuple[int, int, int, int, int, int], float] = {
        (
            rescue_in_hand,
            outs_in_hand,
            rescue_in_deck,
            outs_in_deck,
            other_in_deck,
            required_rescues,
        ): 1.0
    }

    for cards_drawn in draw_segments:
        next_states: defaultdict[
            tuple[int, int, int, int, int, int], float
        ] = defaultdict(float)

        for (
            hand_rescue,
            hand_outs,
            deck_rescue,
            deck_outs,
            deck_other,
            required,
        ), state_mass in states.items():
            deck_cards = deck_rescue + deck_outs + deck_other
            if cards_drawn > deck_cards:
                continue

            denominator = _choose(deck_cards, cards_drawn)

            for rescue_drawn in range(min(deck_rescue, cards_drawn) + 1):
                remaining_draws = cards_drawn - rescue_drawn
                for outs_drawn in range(min(deck_outs, remaining_draws) + 1):
                    other_drawn = remaining_draws - outs_drawn
                    if other_drawn > deck_other:
                        continue

                    ways = (
                        _choose(deck_rescue, rescue_drawn)
                        * _choose(deck_outs, outs_drawn)
                        * _choose(deck_other, other_drawn)
                    )
                    if ways == 0:
                        continue

                    next_hand_rescue = hand_rescue + rescue_drawn
                    next_hand_outs = hand_outs + outs_drawn
                    next_deck_rescue = deck_rescue - rescue_drawn
                    next_deck_outs = deck_outs - outs_drawn
                    next_deck_other = deck_other - other_drawn

                    rescues_still_needed_in_hand = max(
                        0, required - next_hand_rescue
                    )
                    searches = min(
                        next_hand_outs,
                        next_deck_rescue,
                        rescues_still_needed_in_hand,
                    )
                    next_hand_rescue += searches
                    next_hand_outs -= searches
                    next_deck_rescue -= searches

                    if required > 0 and next_hand_rescue > 0:
                        next_hand_rescue -= 1
                        next_required = required - 1
                    else:
                        next_required = required

                    next_states[
                        (
                            next_hand_rescue,
                            next_hand_outs,
                            next_deck_rescue,
                            next_deck_outs,
                            next_deck_other,
                            next_required,
                        )
                    ] += state_mass * ways / denominator

        states = dict(next_states)

    return sum(
        state_mass
        for (*_, required), state_mass in states.items()
        if required == 0
    )


def timed_rescue_direct_out_metrics(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    direct_out_nonstarter: int,
    cards_seen_by_window: Sequence[int],
    opening_hand_size: int = 7,
) -> dict[str, float]:
    """Return exact valid-start-conditioned timed rescue metrics.

    All modeled critical, rescue, and direct-out cards are non-starters.
    The returned mapping contains:

    - critical_prized_probability:
      P(at least one modeled critical is Prized | valid start)
    - conditional_success_probability:
      P(all modeled critical Prizes rescued by the deadline |
        at least one modeled critical is Prized, valid start)
    - conditional_failure_probability:
      complement of conditional_success_probability
    - overall_failure_probability:
      P(deadline failure | valid start)
    """

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in the deck")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening_hand_size must fit before Prize cards")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must fit in the deck")
    if min(
        critical_nonstarter,
        rescue_nonstarter,
        direct_out_nonstarter,
    ) < 0:
        raise ValueError("modeled card counts must be non-negative")

    filler_nonstarter = (
        deck_size
        - starter_cards
        - critical_nonstarter
        - rescue_nonstarter
        - direct_out_nonstarter
    )
    if filler_nonstarter < 0:
        raise ValueError("modeled card counts exceed deck size")
    if starter_cards == 0:
        raise ValueError("valid-start conditioning requires at least one starter")

    windows = _validate_windows(
        cards_seen_by_window,
        opening_hand_size=opening_hand_size,
    )
    draw_segments: list[int] = []
    previous = opening_hand_size
    for cards_seen in windows:
        draw_segments.append(cards_seen - previous)
        previous = cards_seen

    sizes = (
        critical_nonstarter,
        rescue_nonstarter,
        direct_out_nonstarter,
        starter_cards,
        filler_nonstarter,
    )

    opening_denominator = _choose(deck_size, opening_hand_size)
    opening_acceptance = 1.0 - _choose(
        deck_size - starter_cards, opening_hand_size
    ) / opening_denominator
    if opening_acceptance == 0.0:
        raise ValueError("valid opening has zero probability")

    critical_mass = 0.0
    success_mass = 0.0

    opening_ranges = [
        range(min(size, opening_hand_size) + 1)
        for size in sizes
    ]
    for opening_counts in product(*opening_ranges):
        if sum(opening_counts) != opening_hand_size:
            continue
        if opening_counts[3] == 0:
            continue

        opening_ways = 1
        for size, count in zip(sizes, opening_counts):
            opening_ways *= _choose(size, count)
        if opening_ways == 0:
            continue

        opening_mass = (
            opening_ways / opening_denominator / opening_acceptance
        )
        after_opening = tuple(
            size - count
            for size, count in zip(sizes, opening_counts)
        )

        prize_denominator = _choose(
            deck_size - opening_hand_size,
            prize_count,
        )
        prize_ranges = [
            range(min(size, prize_count) + 1)
            for size in after_opening
        ]

        for prize_counts in product(*prize_ranges):
            if sum(prize_counts) != prize_count:
                continue
            if prize_counts[0] == 0:
                continue

            prize_ways = 1
            for size, count in zip(after_opening, prize_counts):
                prize_ways *= _choose(size, count)
            if prize_ways == 0:
                continue

            state_mass = (
                opening_mass * prize_ways / prize_denominator
            )
            critical_mass += state_mass

            after_prizes = tuple(
                size - count
                for size, count in zip(after_opening, prize_counts)
            )
            required_rescues = prize_counts[0]

            success_probability = _success_probability_after_opening_and_prizes(
                rescue_in_hand=opening_counts[1],
                outs_in_hand=opening_counts[2],
                rescue_in_deck=after_prizes[1],
                outs_in_deck=after_prizes[2],
                other_in_deck=(
                    after_prizes[0]
                    + after_prizes[3]
                    + after_prizes[4]
                ),
                required_rescues=required_rescues,
                draw_segments=draw_segments,
            )
            success_mass += state_mass * success_probability

    if critical_mass == 0.0:
        conditional_success = 0.0
        conditional_failure = 0.0
    else:
        conditional_success = success_mass / critical_mass
        conditional_failure = 1.0 - conditional_success

    return {
        "critical_prized_probability": critical_mass,
        "conditional_success_probability": conditional_success,
        "conditional_failure_probability": conditional_failure,
        "overall_failure_probability": critical_mass - success_mass,
    }
