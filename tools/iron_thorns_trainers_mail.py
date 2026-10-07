"""Exact Trainers' Mail extension for the Aichi Iron Thorns named line.

The state space conditions on a legal opening, six Prize cards, and the first
draw going second. Trainers' Mail lookups are solved recursively. Each lookup
samples the top four cards exactly, then chooses the action that maximizes the
represented probability of reaching the Thunder Mountain + Double Colorless
Energy Volt Cyclone package.

Only Guzma & Hala, Tag Call, Thunder Mountain, and otherwise irrelevant
Trainer cards are selectable by the represented Trainers' Mail transition.
Other Trainer effects are outside this model.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Iterator


@dataclass(frozen=True)
class MailLineCounts:
    iron_thorns: int
    guzma_hala: int
    tag_call: int
    thunder_mountain: int
    double_colorless: int
    trainers_mail: int
    other_trainers: int
    other_nontrainers: int
    opening_size: int = 7
    prize_count: int = 6

    @property
    def deck_size(self) -> int:
        return (
            self.iron_thorns
            + self.guzma_hala
            + self.tag_call
            + self.thunder_mountain
            + self.double_colorless
            + self.trainers_mail
            + self.other_trainers
            + self.other_nontrainers
        )

    def categories(self) -> tuple[int, ...]:
        return (
            self.iron_thorns,
            self.guzma_hala,
            self.tag_call,
            self.thunder_mountain,
            self.double_colorless,
            self.trainers_mail,
            self.other_trainers,
            self.other_nontrainers,
        )


@dataclass(frozen=True)
class MailLineResult:
    baseline_probability: Fraction
    mail_probability: Fraction

    @property
    def mail_increment(self) -> Fraction:
        return self.mail_probability - self.baseline_probability


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def _allocations(total: int, caps: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    current = [0] * len(caps)

    def visit(index: int, remaining: int) -> Iterator[tuple[int, ...]]:
        if index == len(caps) - 1:
            if 0 <= remaining <= caps[index]:
                current[index] = remaining
                yield tuple(current)
            return
        for value in range(min(caps[index], remaining) + 1):
            current[index] = value
            yield from visit(index + 1, remaining - value)

    yield from visit(0, total)


def _baseline_success(
    gnh_hand: int,
    tag_hand: int,
    thunder_hand: int,
    dce_hand: int,
    gnh_deck: int,
    thunder_deck: int,
    dce_deck: int,
) -> bool:
    if thunder_hand > 0 and dce_hand > 0:
        return True

    gnh_access = gnh_hand > 0 or (tag_hand > 0 and gnh_deck > 0)
    return (
        gnh_access
        and (thunder_hand > 0 or thunder_deck > 0)
        and (dce_hand > 0 or dce_deck > 0)
    )


@lru_cache(maxsize=None)
def _mail_success_probability(
    gnh_hand: int,
    tag_hand: int,
    thunder_hand: int,
    dce_hand: int,
    mail_hand: int,
    gnh_deck: int,
    tag_deck: int,
    thunder_deck: int,
    dce_deck: int,
    mail_deck: int,
    other_trainer_deck: int,
    nontrainer_deck: int,
) -> Fraction:
    if _baseline_success(
        gnh_hand,
        tag_hand,
        thunder_hand,
        dce_hand,
        gnh_deck,
        thunder_deck,
        dce_deck,
    ):
        return Fraction(1)

    if mail_hand <= 0:
        return Fraction(0)

    deck = (
        gnh_deck,
        tag_deck,
        thunder_deck,
        dce_deck,
        mail_deck,
        other_trainer_deck,
        nontrainer_deck,
    )
    deck_size = sum(deck)
    if deck_size < 4:
        return Fraction(0)

    denominator = _choose(deck_size, 4)
    total = Fraction(0)

    for reveal in _allocations(4, deck):
        ways = math.prod(
            _choose(deck[index], reveal[index])
            for index in range(len(deck))
        )

        reveal_gnh, reveal_tag, reveal_thunder, _, _, reveal_other, _ = reveal

        # Observable policy only. It depends on the current hand and the four
        # cards just revealed, never on hidden Prize composition.
        #
        # A revealed Thunder Mountain is a guaranteed direct completion when
        # DCE is already in hand. Otherwise G&H is the strongest direct
        # connector, followed by Tag Call, then Thunder Mountain. An unrelated
        # Trainer is taken only to remove one card from the deck before a later
        # Mail. If none of those targets is present, take nothing.
        if dce_hand > 0 and thunder_hand == 0 and reveal_thunder:
            continuation = _mail_success_probability(
                gnh_hand,
                tag_hand,
                thunder_hand + 1,
                dce_hand,
                mail_hand - 1,
                gnh_deck,
                tag_deck,
                thunder_deck - 1,
                dce_deck,
                mail_deck,
                other_trainer_deck,
                nontrainer_deck,
            )
        elif reveal_gnh:
            continuation = _mail_success_probability(
                gnh_hand + 1,
                tag_hand,
                thunder_hand,
                dce_hand,
                mail_hand - 1,
                gnh_deck - 1,
                tag_deck,
                thunder_deck,
                dce_deck,
                mail_deck,
                other_trainer_deck,
                nontrainer_deck,
            )
        elif reveal_tag:
            continuation = _mail_success_probability(
                gnh_hand,
                tag_hand + 1,
                thunder_hand,
                dce_hand,
                mail_hand - 1,
                gnh_deck,
                tag_deck - 1,
                thunder_deck,
                dce_deck,
                mail_deck,
                other_trainer_deck,
                nontrainer_deck,
            )
        elif reveal_thunder:
            continuation = _mail_success_probability(
                gnh_hand,
                tag_hand,
                thunder_hand + 1,
                dce_hand,
                mail_hand - 1,
                gnh_deck,
                tag_deck,
                thunder_deck - 1,
                dce_deck,
                mail_deck,
                other_trainer_deck,
                nontrainer_deck,
            )
        elif reveal_other:
            continuation = _mail_success_probability(
                gnh_hand,
                tag_hand,
                thunder_hand,
                dce_hand,
                mail_hand - 1,
                gnh_deck,
                tag_deck,
                thunder_deck,
                dce_deck,
                mail_deck,
                other_trainer_deck - 1,
                nontrainer_deck,
            )
        else:
            continuation = _mail_success_probability(
                gnh_hand,
                tag_hand,
                thunder_hand,
                dce_hand,
                mail_hand - 1,
                gnh_deck,
                tag_deck,
                thunder_deck,
                dce_deck,
                mail_deck,
                other_trainer_deck,
                nontrainer_deck,
            )

        total += Fraction(ways, denominator) * continuation

    return total


def exact_mail_line_probability(counts: MailLineCounts) -> MailLineResult:
    """Evaluate the narrow route with and without optimal Trainers' Mail use."""

    categories = counts.categories()
    deck_size = counts.deck_size
    if deck_size <= counts.opening_size + counts.prize_count:
        raise ValueError("setup must leave at least one card for the turn draw")
    if counts.iron_thorns <= 0:
        raise ValueError("at least one Iron Thorns ex is required")

    total_openings = _choose(deck_size, counts.opening_size)
    rejected_openings = _choose(
        deck_size - counts.iron_thorns,
        counts.opening_size,
    )
    accepted_openings = total_openings - rejected_openings

    remaining_after_opening = deck_size - counts.opening_size
    remaining_after_prizes = remaining_after_opening - counts.prize_count
    denominator = (
        accepted_openings
        * _choose(remaining_after_opening, counts.prize_count)
        * remaining_after_prizes
    )

    baseline_weight = 0
    mail_weight = Fraction(0)

    for opening in _allocations(counts.opening_size, categories):
        if opening[0] < 1:
            continue

        opening_ways = math.prod(
            _choose(categories[index], opening[index])
            for index in range(len(categories))
        )
        after_opening = tuple(
            categories[index] - opening[index]
            for index in range(len(categories))
        )

        for prizes in _allocations(counts.prize_count, after_opening):
            prize_ways = math.prod(
                _choose(after_opening[index], prizes[index])
                for index in range(len(categories))
            )
            after_prizes = tuple(
                after_opening[index] - prizes[index]
                for index in range(len(categories))
            )

            for draw_index, copies in enumerate(after_prizes):
                if copies == 0:
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

                weight = opening_ways * prize_ways * copies

                if _baseline_success(
                    hand[1],
                    hand[2],
                    hand[3],
                    hand[4],
                    deck[1],
                    deck[3],
                    deck[4],
                ):
                    baseline_weight += weight

                conditional_mail = _mail_success_probability(
                    hand[1],
                    hand[2],
                    hand[3],
                    hand[4],
                    hand[5],
                    deck[1],
                    deck[2],
                    deck[3],
                    deck[4],
                    deck[5],
                    deck[6],
                    deck[0] + deck[7],
                )
                mail_weight += weight * conditional_mail

    return MailLineResult(
        baseline_probability=Fraction(baseline_weight, denominator),
        mail_probability=mail_weight / denominator,
    )
