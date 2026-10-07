"""Two-horizon regional recovery package for Aichi Iron Thorns failures.

The model refines the same exact first-turn state space as the narrow named-line
analysis. In named-line failure states it asks whether Palace Belt can be made
ready for the next turn while Palace Book or Player's Ceremony supplies an
immediate end-turn draw continuation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterator


@dataclass(frozen=True)
class RegionalRecoveryCounts:
    iron_thorns: int = 4
    tag_call: int = 2
    guzma_hala: int = 2
    thunder_mountain: int = 1
    double_colorless: int = 1
    palace_book: int = 0
    palace_belt: int = 0
    players_ceremony: int = 0
    competing_active_tools: int = 0
    deck_size: int = 60
    opening_size: int = 7
    prize_count: int = 6

    @property
    def filler(self) -> int:
        return self.deck_size - sum(
            (
                self.iron_thorns,
                self.tag_call,
                self.guzma_hala,
                self.thunder_mountain,
                self.double_colorless,
                self.palace_book,
                self.palace_belt,
                self.players_ceremony,
                self.competing_active_tools,
            )
        )

    def categories(self) -> tuple[int, ...]:
        return (
            self.iron_thorns,
            self.tag_call,
            self.guzma_hala,
            self.thunder_mountain,
            self.double_colorless,
            self.palace_book,
            self.palace_belt,
            self.players_ceremony,
            self.competing_active_tools,
            self.filler,
        )


@dataclass(frozen=True)
class RegionalRecoveryResult:
    accepted_opening_probability: Fraction
    named_success_probability: Fraction
    belt_ready_on_failure_probability: Fraction
    draw_ready_on_failure_probability: Fraction
    dual_horizon_ready_probability: Fraction
    gh_fetch_belt_and_ceremony_probability: Fraction
    dual_horizon_with_competing_tool_in_hand_probability: Fraction

    @property
    def named_failure_probability(self) -> Fraction:
        return Fraction(1) - self.named_success_probability

    def conditional_on_named_failure(self, value: Fraction) -> Fraction:
        return value / self.named_failure_probability


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


def exact_regional_recovery_package(
    counts: RegionalRecoveryCounts,
) -> RegionalRecoveryResult:
    categories = counts.categories()
    if counts.filler < 0:
        raise ValueError("modeled card counts exceed deck size")
    if counts.iron_thorns <= 0:
        raise ValueError("at least one Iron Thorns ex is required")
    if counts.palace_belt <= 0:
        raise ValueError("at least one Palace Belt is required for this endpoint")
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

    success_weight = 0
    belt_ready_weight = 0
    draw_ready_weight = 0
    dual_ready_weight = 0
    gh_fetch_both_weight = 0
    dual_competing_tool_weight = 0

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
                hand[0] -= 1
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
                belt_hand = hand[6]
                ceremony_hand = hand[7]
                competing_tool_hand = hand[8]

                gh_deck = deck[2]
                thunder_deck = deck[3]
                dce_deck = deck[4]
                belt_deck = deck[6]
                ceremony_deck = deck[7]

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
                    success_weight += weight
                    continue

                # G&H can obtain Ceremony through its unconditional Stadium
                # channel. Obtaining Belt through its optional Tool channel
                # requires the two-card discard; this model establishes only
                # raw mechanical reachability, not strategic DCI.
                belt_ready = (
                    belt_hand > 0
                    or (gh_accessible and belt_deck > 0)
                )
                draw_ready = (
                    book_hand > 0
                    or ceremony_hand > 0
                    or (gh_accessible and ceremony_deck > 0)
                )
                dual_ready = belt_ready and draw_ready

                if belt_ready:
                    belt_ready_weight += weight
                if draw_ready:
                    draw_ready_weight += weight
                if dual_ready:
                    dual_ready_weight += weight
                    if competing_tool_hand > 0:
                        dual_competing_tool_weight += weight

                # This isolates the strongest same-connector package: neither
                # Belt nor Ceremony has already been drawn, both remain in the
                # deck, and one live G&H can search both in a single action.
                if (
                    gh_accessible
                    and belt_hand == 0
                    and ceremony_hand == 0
                    and belt_deck > 0
                    and ceremony_deck > 0
                ):
                    gh_fetch_both_weight += weight

    return RegionalRecoveryResult(
        accepted_opening_probability=Fraction(accepted_openings, total_openings),
        named_success_probability=Fraction(success_weight, denominator),
        belt_ready_on_failure_probability=Fraction(belt_ready_weight, denominator),
        draw_ready_on_failure_probability=Fraction(draw_ready_weight, denominator),
        dual_horizon_ready_probability=Fraction(dual_ready_weight, denominator),
        gh_fetch_belt_and_ceremony_probability=Fraction(
            gh_fetch_both_weight, denominator
        ),
        dual_horizon_with_competing_tool_in_hand_probability=Fraction(
            dual_competing_tool_weight, denominator
        ),
    )
