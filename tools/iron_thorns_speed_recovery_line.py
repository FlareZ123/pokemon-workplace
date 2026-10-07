"""Exact Palace Belt + Player's Ceremony + Speed Lightning recovery line."""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterator


@dataclass(frozen=True)
class SpeedRecoveryCounts:
    iron_thorns: int = 4
    tag_call: int = 2
    guzma_hala: int = 2
    thunder_mountain: int = 1
    double_colorless: int = 1
    palace_belt: int = 0
    players_ceremony: int = 0
    speed_lightning: int = 4
    deck_size: int = 60
    opening_size: int = 7
    prize_count: int = 6

    @property
    def filler(self) -> int:
        return self.deck_size - (
            self.iron_thorns + self.tag_call + self.guzma_hala
            + self.thunder_mountain + self.double_colorless
            + self.palace_belt + self.players_ceremony
            + self.speed_lightning
        )

    def categories(self) -> tuple[int, ...]:
        return (
            self.iron_thorns,
            self.tag_call,
            self.guzma_hala,
            self.thunder_mountain,
            self.double_colorless,
            self.palace_belt,
            self.players_ceremony,
            self.speed_lightning,
            self.filler,
        )


@dataclass(frozen=True)
class SpeedRecoveryResult:
    accepted_opening_probability: Fraction
    named_success_probability: Fraction
    package_ready_on_failure_probability: Fraction
    package_requiring_paid_gh_probability: Fraction
    gh_fetch_all_three_probability: Fraction
    direct_package_without_gh_probability: Fraction

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


def exact_speed_recovery_line(
    counts: SpeedRecoveryCounts,
) -> SpeedRecoveryResult:
    categories = counts.categories()
    if counts.filler < 0:
        raise ValueError("modeled card counts exceed deck size")
    if counts.iron_thorns <= 0:
        raise ValueError("at least one Iron Thorns ex is required")
    if counts.palace_belt <= 0:
        raise ValueError("Palace Belt is required")
    if counts.players_ceremony <= 0:
        raise ValueError("Player's Ceremony is required")
    if counts.speed_lightning <= 0:
        raise ValueError("Speed Lightning Energy is required")

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
    package_weight = 0
    paid_gh_weight = 0
    fetch_all_three_weight = 0
    direct_without_gh_weight = 0

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
                belt_hand = hand[5]
                ceremony_hand = hand[6]
                speed_hand = hand[7]

                gh_deck = deck[2]
                thunder_deck = deck[3]
                dce_deck = deck[4]
                belt_deck = deck[5]
                ceremony_deck = deck[6]
                speed_deck = deck[7]

                gh_accessible = (
                    gh_hand > 0
                    or (tag_hand > 0 and gh_deck > 0)
                )
                resources_available = (
                    (thunder_hand > 0 or thunder_deck > 0)
                    and (dce_hand > 0 or dce_deck > 0)
                )
                named_success = (
                    (thunder_hand > 0 and dce_hand > 0)
                    or (resources_available and gh_accessible)
                )

                if named_success:
                    success_weight += weight
                    continue

                belt_ready = belt_hand > 0 or (
                    gh_accessible and belt_deck > 0
                )
                ceremony_ready = ceremony_hand > 0 or (
                    gh_accessible and ceremony_deck > 0
                )
                speed_ready = speed_hand > 0 or (
                    gh_accessible and speed_deck > 0
                )
                package_ready = belt_ready and ceremony_ready and speed_ready

                if not package_ready:
                    continue

                package_weight += weight

                if belt_hand == 0 or speed_hand == 0:
                    paid_gh_weight += weight

                if (
                    gh_accessible
                    and belt_hand == 0
                    and ceremony_hand == 0
                    and speed_hand == 0
                    and belt_deck > 0
                    and ceremony_deck > 0
                    and speed_deck > 0
                ):
                    fetch_all_three_weight += weight

                if (
                    not gh_accessible
                    and belt_hand > 0
                    and ceremony_hand > 0
                    and speed_hand > 0
                ):
                    direct_without_gh_weight += weight

    return SpeedRecoveryResult(
        accepted_opening_probability=Fraction(accepted_openings, total_openings),
        named_success_probability=Fraction(success_weight, denominator),
        package_ready_on_failure_probability=Fraction(package_weight, denominator),
        package_requiring_paid_gh_probability=Fraction(paid_gh_weight, denominator),
        gh_fetch_all_three_probability=Fraction(
            fetch_all_three_weight, denominator
        ),
        direct_package_without_gh_probability=Fraction(
            direct_without_gh_weight, denominator
        ),
    )
