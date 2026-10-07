"""Exact regional-card continuation within Aichi Iron Thorns named-line failures.

The state space matches the narrow first-turn-going-second named-line model:
accepted seven-card opening, six Prize cards, then one normal draw. The model
adds Palace Book and Player's Ceremony so failure states can be partitioned by
whether a region-only end-turn draw continuation is immediately available.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterator


@dataclass(frozen=True)
class RegionalContinuationCounts:
    iron_thorns: int = 4
    tag_call: int = 2
    guzma_hala: int = 2
    thunder_mountain: int = 1
    double_colorless: int = 1
    palace_book: int = 0
    players_ceremony: int = 0
    deck_size: int = 60
    opening_size: int = 7
    prize_count: int = 6

    @property
    def filler(self) -> int:
        return self.deck_size - (
            self.iron_thorns
            + self.tag_call
            + self.guzma_hala
            + self.thunder_mountain
            + self.double_colorless
            + self.palace_book
            + self.players_ceremony
        )

    def categories(self) -> tuple[int, ...]:
        return (
            self.iron_thorns,
            self.tag_call,
            self.guzma_hala,
            self.thunder_mountain,
            self.double_colorless,
            self.palace_book,
            self.players_ceremony,
            self.filler,
        )


@dataclass(frozen=True)
class RegionalContinuationResult:
    accepted_opening_probability: Fraction
    named_success_probability: Fraction
    failure_book_witness_probability: Fraction
    failure_ceremony_hand_witness_probability: Fraction
    failure_ceremony_search_witness_probability: Fraction
    failure_without_regional_draw_probability: Fraction
    resource_unavailable_failure_probability: Fraction
    connector_failure_probability: Fraction

    @property
    def named_failure_probability(self) -> Fraction:
        return Fraction(1) - self.named_success_probability

    @property
    def regional_draw_on_failure_probability(self) -> Fraction:
        return (
            self.failure_book_witness_probability
            + self.failure_ceremony_hand_witness_probability
            + self.failure_ceremony_search_witness_probability
        )

    @property
    def regional_draw_given_named_failure(self) -> Fraction:
        return (
            self.regional_draw_on_failure_probability
            / self.named_failure_probability
        )


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

        for selected in range(min(bounds[index], remaining) + 1):
            current[index] = selected
            yield from visit(index + 1, remaining - selected)

    yield from visit(0, total)


def exact_regional_failure_continuation(
    counts: RegionalContinuationCounts,
) -> RegionalContinuationResult:
    categories = counts.categories()
    if counts.filler < 0:
        raise ValueError("modeled card counts exceed deck size")
    if counts.iron_thorns <= 0:
        raise ValueError("at least one Iron Thorns ex is required")
    if counts.opening_size + counts.prize_count >= counts.deck_size:
        raise ValueError("setup leaves no card for the normal draw")

    total_openings = _choose(counts.deck_size, counts.opening_size)
    rejected_openings = _choose(
        counts.deck_size - counts.iron_thorns,
        counts.opening_size,
    )
    accepted_openings = total_openings - rejected_openings
    after_opening_size = counts.deck_size - counts.opening_size
    after_prizes_size = after_opening_size - counts.prize_count
    denominator = (
        accepted_openings
        * _choose(after_opening_size, counts.prize_count)
        * after_prizes_size
    )

    buckets = {
        "success": 0,
        "failure_book": 0,
        "failure_ceremony_hand": 0,
        "failure_ceremony_search": 0,
        "failure_none": 0,
        "resource_unavailable": 0,
        "connector_failure": 0,
    }

    for opening in _bounded_compositions(counts.opening_size, categories):
        if opening[0] == 0:
            continue

        opening_ways = math.prod(
            _choose(population, selected)
            for population, selected in zip(categories, opening)
        )
        after_opening = tuple(
            population - selected
            for population, selected in zip(categories, opening)
        )

        for prizes in _bounded_compositions(counts.prize_count, after_opening):
            prize_ways = math.prod(
                _choose(population, selected)
                for population, selected in zip(after_opening, prizes)
            )
            after_prizes = tuple(
                population - selected
                for population, selected in zip(after_opening, prizes)
            )

            for draw_index, draw_copies in enumerate(after_prizes):
                if draw_copies == 0:
                    continue

                hand = [
                    opening[index] + int(index == draw_index)
                    for index in range(len(categories))
                ]
                hand[0] -= 1  # one Iron Thorns ex becomes the Active Pokemon
                deck = [
                    after_prizes[index] - int(index == draw_index)
                    for index in range(len(categories))
                ]

                weight = opening_ways * prize_ways * draw_copies

                tag_hand = hand[1]
                gh_hand = hand[2]
                thunder_hand = hand[3]
                dce_hand = hand[4]
                book_hand = hand[5]
                ceremony_hand = hand[6]

                gh_deck = deck[2]
                thunder_deck = deck[3]
                dce_deck = deck[4]
                ceremony_deck = deck[6]

                resources_available = (
                    (thunder_hand > 0 or thunder_deck > 0)
                    and (dce_hand > 0 or dce_deck > 0)
                )
                gh_accessible = (
                    gh_hand > 0
                    or (tag_hand > 0 and gh_deck > 0)
                )
                direct_package = thunder_hand > 0 and dce_hand > 0
                named_success = direct_package or (
                    resources_available and gh_accessible
                )

                if named_success:
                    buckets["success"] += weight
                    continue

                if resources_available:
                    buckets["connector_failure"] += weight
                else:
                    buckets["resource_unavailable"] += weight

                # Exclusive witness partition. Directly held Palace Book gets
                # first priority, then a directly held Ceremony, then a
                # Ceremony still searchable through the live G&H connector.
                if book_hand > 0:
                    buckets["failure_book"] += weight
                elif ceremony_hand > 0:
                    buckets["failure_ceremony_hand"] += weight
                elif gh_accessible and ceremony_deck > 0:
                    buckets["failure_ceremony_search"] += weight
                else:
                    buckets["failure_none"] += weight

    state_partition = (
        buckets["success"]
        + buckets["failure_book"]
        + buckets["failure_ceremony_hand"]
        + buckets["failure_ceremony_search"]
        + buckets["failure_none"]
    )
    if state_partition != denominator:
        raise AssertionError("regional continuation partition is incomplete")

    failure_partition = (
        buckets["resource_unavailable"]
        + buckets["connector_failure"]
    )
    if failure_partition != denominator - buckets["success"]:
        raise AssertionError("named-line failure partition is incomplete")

    return RegionalContinuationResult(
        accepted_opening_probability=Fraction(accepted_openings, total_openings),
        named_success_probability=Fraction(buckets["success"], denominator),
        failure_book_witness_probability=Fraction(
            buckets["failure_book"], denominator
        ),
        failure_ceremony_hand_witness_probability=Fraction(
            buckets["failure_ceremony_hand"], denominator
        ),
        failure_ceremony_search_witness_probability=Fraction(
            buckets["failure_ceremony_search"], denominator
        ),
        failure_without_regional_draw_probability=Fraction(
            buckets["failure_none"], denominator
        ),
        resource_unavailable_failure_probability=Fraction(
            buckets["resource_unavailable"], denominator
        ),
        connector_failure_probability=Fraction(
            buckets["connector_failure"], denominator
        ),
    )
