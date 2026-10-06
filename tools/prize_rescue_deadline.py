"""Exact timed-access probabilities for Gladion-like Prize rescue.

The model extends valid-start-conditioned Prize topology by asking whether enough
rescue Supporters actually reach the hand by a sequence of Supporter windows.
Each rescue play can recover one critical Prized card and then becomes a Prize,
matching the capacity model in prize_rescue_start_condition.py.

cards_seen_by_window is cumulative random card exposure outside the Prize cards,
including the accepted opening hand. It can represent natural draws or another
unbiased without-replacement exposure process. Targeted search, shuffle-draw
effects, Supporter contention, locks, and ordinary Prize taking are outside this
model.
"""

from __future__ import annotations

from itertools import product
from math import comb
from typing import Sequence

from prize_rescue_start_condition import (
    accepted_opening_probability,
    any_critical_prized_probability_given_valid_start,
    conditioned_prize_state_distribution,
)


PrizeState = tuple[int, int, int, int, int, int]


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _validate_windows(
    cards_seen_by_window: Sequence[int],
    *,
    opening_hand_size: int,
    non_prize_cards: int,
) -> tuple[int, ...]:
    windows = tuple(cards_seen_by_window)
    previous = opening_hand_size
    for cards_seen in windows:
        if cards_seen < previous:
            raise ValueError("cards_seen_by_window must be nondecreasing and include the opening hand")
        if cards_seen > non_prize_cards:
            raise ValueError("cards_seen_by_window cannot exceed the non-Prize card count")
        previous = cards_seen
    return windows


def _opening_rescue_count_distribution(
    *,
    rescue_starters: int,
    rescue_nonstarters: int,
    other_starters: int,
    other_nonstarters: int,
    opening_hand_size: int,
) -> dict[int, float]:
    """Return P(rescuers in accepted opening hand | fixed Prize state)."""
    deck_size = rescue_starters + rescue_nonstarters + other_starters + other_nonstarters
    starter_cards = rescue_starters + other_starters
    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("fixed Prize state cannot produce a valid opening hand")

    denominator = _choose(deck_size, opening_hand_size)
    distribution: dict[int, float] = {}

    for rs_hand in range(min(rescue_starters, opening_hand_size) + 1):
        for rn_hand in range(min(rescue_nonstarters, opening_hand_size - rs_hand) + 1):
            for os_hand in range(min(other_starters, opening_hand_size - rs_hand - rn_hand) + 1):
                on_hand = opening_hand_size - rs_hand - rn_hand - os_hand
                if not 0 <= on_hand <= other_nonstarters:
                    continue
                if rs_hand + os_hand == 0:
                    continue

                ways = (
                    _choose(rescue_starters, rs_hand)
                    * _choose(rescue_nonstarters, rn_hand)
                    * _choose(other_starters, os_hand)
                    * _choose(other_nonstarters, on_hand)
                )
                rescuers_in_hand = rs_hand + rn_hand
                distribution[rescuers_in_hand] = distribution.get(rescuers_in_hand, 0.0) + (
                    ways / denominator / accepted
                )

    return distribution


def _schedule_success_probability(
    *,
    cards_after_opening: int,
    rescuers_after_opening: int,
    rescuers_in_opening: int,
    required_plays: int,
    cards_seen_by_window: Sequence[int],
    opening_hand_size: int,
) -> float:
    """Return probability the observed rescuers can be scheduled by the deadline."""
    windows = tuple(cards_seen_by_window)
    window_count = len(windows)
    if required_plays == 0:
        return 1.0
    if required_plays > window_count:
        return 0.0
    if rescuers_in_opening + rescuers_after_opening < required_plays:
        return 0.0

    segment_sizes: list[int] = []
    previous = opening_hand_size
    for cards_seen in windows:
        segment_sizes.append(cards_seen - previous)
        previous = cards_seen

    exposed_after_opening = sum(segment_sizes)
    unseen_cards = cards_after_opening - exposed_after_opening
    denominator = _choose(cards_after_opening, rescuers_after_opening)
    probability = 0.0

    ranges = [range(min(segment, rescuers_after_opening) + 1) for segment in segment_sizes]
    for rescue_allocation in product(*ranges):
        allocated = sum(rescue_allocation)
        rescuers_unseen = rescuers_after_opening - allocated
        if not 0 <= rescuers_unseen <= unseen_cards:
            continue

        ways = _choose(unseen_cards, rescuers_unseen)
        for segment, rescuers in zip(segment_sizes, rescue_allocation):
            ways *= _choose(segment, rescuers)
        if ways == 0:
            continue

        rescuers_seen = rescuers_in_opening
        feasible = True
        for window_index, rescuers in enumerate(rescue_allocation, start=1):
            rescuers_seen += rescuers
            required_by_now = max(0, required_plays - (window_count - window_index))
            if rescuers_seen < required_by_now:
                feasible = False
                break

        if feasible:
            probability += ways / denominator

    return probability


def rescue_schedule_success_given_prize_state(
    deck_size: int,
    prize_count: int,
    prize_state: PrizeState,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
    cards_seen_by_window: Sequence[int],
    opening_hand_size: int = 7,
) -> float:
    """Return P(all initially Prized criticals rescued by deadline | Prize state, valid start)."""
    non_prize_cards = deck_size - prize_count
    windows = _validate_windows(
        cards_seen_by_window,
        opening_hand_size=opening_hand_size,
        non_prize_cards=non_prize_cards,
    )
    critical_prized = prize_state[0] + prize_state[1]
    if critical_prized == 0:
        return 1.0

    rescue_prized = prize_state[2] + prize_state[3]
    rescue_total = rescue_starter + rescue_nonstarter
    if critical_prized > rescue_total - rescue_prized:
        return 0.0
    if critical_prized > len(windows):
        return 0.0

    filler_starter = starter_cards - critical_starter - rescue_starter
    filler_nonstarter = (
        deck_size - starter_cards - critical_nonstarter - rescue_nonstarter
    )

    remaining_rescue_starter = rescue_starter - prize_state[2]
    remaining_rescue_nonstarter = rescue_nonstarter - prize_state[3]
    remaining_other_starter = (
        critical_starter - prize_state[0]
        + filler_starter - prize_state[4]
    )
    remaining_other_nonstarter = (
        critical_nonstarter - prize_state[1]
        + filler_nonstarter - prize_state[5]
    )

    opening_distribution = _opening_rescue_count_distribution(
        rescue_starters=remaining_rescue_starter,
        rescue_nonstarters=remaining_rescue_nonstarter,
        other_starters=remaining_other_starter,
        other_nonstarters=remaining_other_nonstarter,
        opening_hand_size=opening_hand_size,
    )

    rescue_outside_prizes = remaining_rescue_starter + remaining_rescue_nonstarter
    cards_after_opening = non_prize_cards - opening_hand_size
    probability = 0.0
    for rescuers_in_opening, opening_mass in opening_distribution.items():
        probability += opening_mass * _schedule_success_probability(
            cards_after_opening=cards_after_opening,
            rescuers_after_opening=rescue_outside_prizes - rescuers_in_opening,
            rescuers_in_opening=rescuers_in_opening,
            required_plays=critical_prized,
            cards_seen_by_window=windows,
            opening_hand_size=opening_hand_size,
        )
    return probability


def deadline_failure_probability_given_valid_start(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
    cards_seen_by_window: Sequence[int],
    opening_hand_size: int = 7,
) -> float:
    """Return P(a modeled critical misses the rescue deadline | valid start)."""
    probability = 0.0
    for prize_state, state_mass in conditioned_prize_state_distribution(
        deck_size,
        prize_count,
        starter_cards=starter_cards,
        critical_starter=critical_starter,
        critical_nonstarter=critical_nonstarter,
        rescue_starter=rescue_starter,
        rescue_nonstarter=rescue_nonstarter,
        opening_hand_size=opening_hand_size,
    ):
        if prize_state[0] + prize_state[1] == 0:
            continue
        schedule_success = rescue_schedule_success_given_prize_state(
            deck_size,
            prize_count,
            prize_state,
            starter_cards=starter_cards,
            critical_starter=critical_starter,
            critical_nonstarter=critical_nonstarter,
            rescue_starter=rescue_starter,
            rescue_nonstarter=rescue_nonstarter,
            cards_seen_by_window=cards_seen_by_window,
            opening_hand_size=opening_hand_size,
        )
        probability += state_mass * (1.0 - schedule_success)
    return probability


def conditional_deadline_failure_probability_given_valid_start(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
    cards_seen_by_window: Sequence[int],
    opening_hand_size: int = 7,
) -> float:
    """Return P(deadline failure | a modeled critical is Prized, valid start)."""
    any_critical = any_critical_prized_probability_given_valid_start(
        deck_size,
        prize_count,
        starter_cards=starter_cards,
        critical_starter=critical_starter,
        critical_nonstarter=critical_nonstarter,
        rescue_starter=rescue_starter,
        rescue_nonstarter=rescue_nonstarter,
        opening_hand_size=opening_hand_size,
    )
    if any_critical == 0.0:
        return 0.0

    return deadline_failure_probability_given_valid_start(
        deck_size,
        prize_count,
        starter_cards=starter_cards,
        critical_starter=critical_starter,
        critical_nonstarter=critical_nonstarter,
        rescue_starter=rescue_starter,
        rescue_nonstarter=rescue_nonstarter,
        cards_seen_by_window=cards_seen_by_window,
        opening_hand_size=opening_hand_size,
    ) / any_critical
