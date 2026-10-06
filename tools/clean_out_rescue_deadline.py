"""Exact multi-window Prize rescue with clean deterministic direct outs.

This combines valid-start Prize topology, random exposure, one rescue Supporter
play per modeled window, and an abstract class of clean non-Supporter search outs.

A clean out is assumed to be playable before the Supporter action, consume no
Supporter window, and search one rescue copy from deck into hand. Concrete cards
still require separate cost, lock, timing, and opportunity-cost analysis.
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


def _segments(
    cards_seen_by_window: Sequence[int],
    *,
    opening_hand_size: int,
    non_prize_cards: int,
) -> tuple[int, ...]:
    previous = opening_hand_size
    segments: list[int] = []
    for cards_seen in cards_seen_by_window:
        if cards_seen < previous:
            raise ValueError("cards_seen_by_window must be nondecreasing")
        if cards_seen > non_prize_cards:
            raise ValueError("cards_seen_by_window cannot exceed non-Prize cards")
        segments.append(cards_seen - previous)
        previous = cards_seen
    return tuple(segments)


def _schedule_success_probability(
    *,
    deck_rescue: int,
    deck_outs: int,
    deck_other: int,
    hand_rescue: int,
    hand_outs: int,
    critical_prized: int,
    draw_segments: tuple[int, ...],
) -> float:
    """Return exact success probability after opening and Prize cards are fixed."""
    if critical_prized == 0:
        return 1.0
    if critical_prized > len(draw_segments):
        return 0.0

    states: dict[tuple[int, int, int, int, int, int], float] = {
        (
            deck_rescue,
            deck_outs,
            deck_other,
            hand_rescue,
            hand_outs,
            0,
        ): 1.0
    }

    window_count = len(draw_segments)
    for window_index, draw_count in enumerate(draw_segments, start=1):
        required_by_now = max(
            0,
            critical_prized - (window_count - window_index),
        )
        next_states: defaultdict[
            tuple[int, int, int, int, int, int], float
        ] = defaultdict(float)

        for state, state_mass in states.items():
            (
                rescue_deck,
                outs_deck,
                other_deck,
                rescue_hand,
                outs_hand,
                played,
            ) = state
            total_deck = rescue_deck + outs_deck + other_deck
            draw_denominator = _choose(total_deck, draw_count)
            if draw_denominator == 0:
                continue

            for rescue_drawn in range(
                min(rescue_deck, draw_count) + 1
            ):
                max_outs = min(
                    outs_deck,
                    draw_count - rescue_drawn,
                )
                for outs_drawn in range(max_outs + 1):
                    other_drawn = (
                        draw_count - rescue_drawn - outs_drawn
                    )
                    if not 0 <= other_drawn <= other_deck:
                        continue

                    ways = (
                        _choose(rescue_deck, rescue_drawn)
                        * _choose(outs_deck, outs_drawn)
                        * _choose(other_deck, other_drawn)
                    )
                    if ways == 0:
                        continue

                    next_rescue_deck = (
                        rescue_deck - rescue_drawn
                    )
                    next_outs_deck = outs_deck - outs_drawn
                    next_other_deck = other_deck - other_drawn
                    next_rescue_hand = (
                        rescue_hand + rescue_drawn
                    )
                    next_outs_hand = outs_hand + outs_drawn

                    # Greedily convert every usable clean out into a rescue card.
                    # Moving a rescue from deck to hand cannot reduce future
                    # rescue availability under this costless direct-out model.
                    outs_used = min(
                        next_outs_hand,
                        next_rescue_deck,
                    )
                    next_outs_hand -= outs_used
                    next_rescue_deck -= outs_used
                    next_rescue_hand += outs_used

                    needed_now = max(
                        0,
                        required_by_now - played,
                    )
                    if next_rescue_hand < needed_now:
                        continue

                    next_rescue_hand -= needed_now
                    next_played = played + needed_now
                    next_state = (
                        next_rescue_deck,
                        next_outs_deck,
                        next_other_deck,
                        next_rescue_hand,
                        next_outs_hand,
                        next_played,
                    )
                    next_states[next_state] += (
                        state_mass
                        * ways
                        / draw_denominator
                    )

        states = dict(next_states)

    return sum(states.values())


def deadline_failure_probability_with_clean_outs(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    direct_out_nonstarter: int,
    cards_seen_by_window: Sequence[int],
    opening_hand_size: int = 7,
    condition_on_critical_prized: bool = False,
) -> float:
    """Return exact deadline failure under valid-start conditioning.

    All modeled critical, rescue, and direct-out cards are non-starters.
    """
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if min(
        critical_nonstarter,
        rescue_nonstarter,
        direct_out_nonstarter,
    ) < 0:
        raise ValueError("modeled card counts must be non-negative")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must fit in the deck")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in the deck")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening hand must fit before Prize cards")

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
        raise ValueError("valid-start conditioning requires a starter")

    draw_segments = _segments(
        cards_seen_by_window,
        opening_hand_size=opening_hand_size,
        non_prize_cards=deck_size - prize_count,
    )
    if not draw_segments and critical_nonstarter:
        raise ValueError("at least one Supporter window is required")

    # Category order: critical, rescue, out, starter filler, non-starter filler.
    sizes = (
        critical_nonstarter,
        rescue_nonstarter,
        direct_out_nonstarter,
        starter_cards,
        filler_nonstarter,
    )
    opening_denominator = _choose(
        deck_size, opening_hand_size
    )
    opening_acceptance = 1.0 - _choose(
        deck_size - starter_cards,
        opening_hand_size,
    ) / opening_denominator
    if opening_acceptance == 0.0:
        raise ValueError("valid opening has zero probability")

    failure_mass = 0.0
    conditioning_mass = 0.0

    for opening_counts in product(*[
        range(min(size, opening_hand_size) + 1)
        for size in sizes
    ]):
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
            opening_ways
            / opening_denominator
            / opening_acceptance
        )
        after_opening = tuple(
            size - count
            for size, count in zip(sizes, opening_counts)
        )

        prize_denominator = _choose(
            deck_size - opening_hand_size,
            prize_count,
        )
        for prize_counts in product(*[
            range(min(size, prize_count) + 1)
            for size in after_opening
        ]):
            if sum(prize_counts) != prize_count:
                continue
            critical_prized = prize_counts[0]
            if (
                condition_on_critical_prized
                and critical_prized == 0
            ):
                continue

            prize_ways = 1
            for size, count in zip(
                after_opening, prize_counts
            ):
                prize_ways *= _choose(size, count)
            if prize_ways == 0:
                continue

            state_mass = (
                opening_mass
                * prize_ways
                / prize_denominator
            )
            conditioning_mass += state_mass

            if critical_prized == 0:
                continue

            rescue_deck = (
                after_opening[1] - prize_counts[1]
            )
            outs_deck = (
                after_opening[2] - prize_counts[2]
            )
            other_deck = (
                deck_size
                - opening_hand_size
                - prize_count
                - rescue_deck
                - outs_deck
            )

            success = _schedule_success_probability(
                deck_rescue=rescue_deck,
                deck_outs=outs_deck,
                deck_other=other_deck,
                hand_rescue=opening_counts[1],
                hand_outs=opening_counts[2],
                critical_prized=critical_prized,
                draw_segments=draw_segments,
            )
            failure_mass += state_mass * (1.0 - success)

    if conditioning_mass == 0.0:
        return 0.0
    return failure_mass / conditioning_mass
