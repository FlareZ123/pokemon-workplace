"""Exact setup-conditioned probability for the named Iron Thorns ex attack line.

The model tracks only the card categories needed by the line:
Iron Thorns ex, Tag Call, Guzma & Hala, Thunder Mountain Prism Star,
Double Colorless Energy, and all other cards.

It conditions on a legal seven-card opening containing at least one Iron Thorns
ex, samples six Prize cards from the remaining deck, then draws one card for the
first turn going second.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterator


@dataclass(frozen=True)
class NamedLineCounts:
    iron_thorns: int = 4
    tag_call: int = 2
    guzma_hala: int = 2
    thunder_mountain: int = 1
    double_colorless: int = 1
    deck_size: int = 60
    opening_hand_size: int = 7
    prize_count: int = 6

    @property
    def filler(self) -> int:
        return self.deck_size - (
            self.iron_thorns
            + self.tag_call
            + self.guzma_hala
            + self.thunder_mountain
            + self.double_colorless
        )


@dataclass(frozen=True)
class NamedLineResult:
    accepted_opening_probability: Fraction
    success_probability_given_accepted_opening: Fraction
    direct_package_probability: Fraction
    mediated_discard_probability: Fraction
    mediated_no_discard_probability: Fraction
    unavailable_resource_probability: Fraction
    connector_access_failure_probability: Fraction


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def _bounded_compositions(
    total: int,
    bounds: tuple[int, ...],
) -> Iterator[tuple[int, ...]]:
    current = [0] * len(bounds)

    def visit(index: int, remaining: int) -> Iterator[tuple[int, ...]]:
        if index == len(bounds) - 1:
            if 0 <= remaining <= bounds[index]:
                current[index] = remaining
                yield tuple(current)
            return
        for value in range(min(bounds[index], remaining) + 1):
            current[index] = value
            yield from visit(index + 1, remaining - value)

    yield from visit(0, total)


def _validate(counts: NamedLineCounts) -> None:
    if counts.deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if counts.opening_hand_size <= 0:
        raise ValueError("opening_hand_size must be positive")
    if counts.prize_count < 0:
        raise ValueError("prize_count must be non-negative")
    if counts.filler < 0:
        raise ValueError("named card counts exceed deck size")
    if counts.iron_thorns <= 0:
        raise ValueError("at least one Iron Thorns ex is required")
    if counts.opening_hand_size + counts.prize_count >= counts.deck_size:
        raise ValueError("setup leaves no card for the first-turn draw")


def exact_named_line_probability(counts: NamedLineCounts) -> NamedLineResult:
    """Return exact probabilities for the named first-turn-going-second line."""

    _validate(counts)
    categories = (
        counts.iron_thorns,
        counts.tag_call,
        counts.guzma_hala,
        counts.thunder_mountain,
        counts.double_colorless,
        counts.filler,
    )

    total_openings = _choose(counts.deck_size, counts.opening_hand_size)
    rejected_openings = _choose(
        counts.deck_size - counts.iron_thorns,
        counts.opening_hand_size,
    )
    accepted_openings = total_openings - rejected_openings

    remaining_after_opening = counts.deck_size - counts.opening_hand_size
    remaining_after_prizes = remaining_after_opening - counts.prize_count

    denominator = (
        accepted_openings
        * _choose(remaining_after_opening, counts.prize_count)
        * remaining_after_prizes
    )

    buckets = {
        "direct": 0,
        "mediated_discard": 0,
        "mediated_no_discard": 0,
        "unavailable_resource": 0,
        "connector_access_failure": 0,
    }

    for opening in _bounded_compositions(counts.opening_hand_size, categories):
        if opening[0] < 1:
            continue

        opening_ways = math.prod(
            _choose(total, taken)
            for total, taken in zip(categories, opening)
        )
        after_opening = tuple(
            total - taken
            for total, taken in zip(categories, opening)
        )

        for prizes in _bounded_compositions(counts.prize_count, after_opening):
            prize_ways = math.prod(
                _choose(total, taken)
                for total, taken in zip(after_opening, prizes)
            )
            after_prizes = tuple(
                total - taken
                for total, taken in zip(after_opening, prizes)
            )

            for draw_index, draw_copies in enumerate(after_prizes):
                if draw_copies == 0:
                    continue

                draw = [0] * len(categories)
                draw[draw_index] = 1

                turn_hand = [
                    opening[index] + draw[index]
                    for index in range(len(categories))
                ]
                turn_hand[0] -= 1

                deck = [
                    after_prizes[index] - draw[index]
                    for index in range(len(categories))
                ]

                tag_in_hand = turn_hand[1]
                gh_in_hand = turn_hand[2]
                mountain_in_hand = turn_hand[3]
                dce_in_hand = turn_hand[4]

                gh_in_deck = deck[2]
                mountain_in_deck = deck[3]
                dce_in_deck = deck[4]

                weight = opening_ways * prize_ways * draw_copies

                if mountain_in_hand >= 1 and dce_in_hand >= 1:
                    buckets["direct"] += weight
                    continue

                resources_available = (
                    (mountain_in_hand >= 1 or mountain_in_deck >= 1)
                    and (dce_in_hand >= 1 or dce_in_deck >= 1)
                )
                if not resources_available:
                    buckets["unavailable_resource"] += weight
                    continue

                gh_accessible = (
                    gh_in_hand >= 1
                    or (tag_in_hand >= 1 and gh_in_deck >= 1)
                )
                if not gh_accessible:
                    buckets["connector_access_failure"] += weight
                    continue

                if dce_in_hand >= 1:
                    buckets["mediated_no_discard"] += weight
                else:
                    buckets["mediated_discard"] += weight

    if sum(buckets.values()) != denominator:
        raise AssertionError("probability partition does not cover the state space")

    success = (
        buckets["direct"]
        + buckets["mediated_discard"]
        + buckets["mediated_no_discard"]
    )

    return NamedLineResult(
        accepted_opening_probability=Fraction(accepted_openings, total_openings),
        success_probability_given_accepted_opening=Fraction(success, denominator),
        direct_package_probability=Fraction(buckets["direct"], denominator),
        mediated_discard_probability=Fraction(
            buckets["mediated_discard"],
            denominator,
        ),
        mediated_no_discard_probability=Fraction(
            buckets["mediated_no_discard"],
            denominator,
        ),
        unavailable_resource_probability=Fraction(
            buckets["unavailable_resource"],
            denominator,
        ),
        connector_access_failure_probability=Fraction(
            buckets["connector_access_failure"],
            denominator,
        ),
    )
