"""Opening/Prize aggregation for two support triggers with Quick Ball payments."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from bench_double_trigger_access import _vectors, _ways
from bench_quickball_sequence import (
    DECK, HAND, UNAVAILABLE, optimal_sequence_probability,
    payment_first_probability,
)


@dataclass(frozen=True)
class QuickBallAccess:
    valid_opening: Fraction
    payment_first: Fraction
    adaptive: Fraction

    @property
    def order_gain(self) -> Fraction:
        return self.adaptive - self.payment_first


def analyze_quickball_access(*, deck_size: int = 60,
                             opening_size: int = 7,
                             prize_count: int = 6,
                             later_random_draws: int = 4,
                             other_basics: int = 4,
                             quick_balls: int = 4,
                             direct_bench_items: int = 0,
                             expendable_cards: int = 0,
                             certain_pickups: int = 0,
                             coin_pickups: int = 4,
                             free_slots: int = 1) -> QuickBallAccess:
    """Exact accepted-opening-conditional probability for two singleton triggers.

    Classes: support A/B, ordinary Basics, Quick Balls, direct-to-Bench Items,
    discardable filler, deterministic and coin pickups, inert filler.
    A wrong-zone direct-to-Bench Item can still pay Quick Ball's discard.
    """
    groups = (1, 1, other_basics, quick_balls, direct_bench_items,
              expendable_cards, certain_pickups, coin_pickups)
    if min(groups) < 0 or sum(groups) > deck_size:
        raise ValueError("invalid card-class counts")
    if not 1 <= opening_size <= deck_size:
        raise ValueError("invalid opening size")
    if min(prize_count, later_random_draws) < 0:
        raise ValueError("negative Prize or draw count")
    if opening_size + prize_count + later_random_draws > deck_size:
        raise ValueError("exhausted deck")
    if not 1 <= free_slots <= 5:
        raise ValueError("invalid Bench slack")

    capacities = (*groups, deck_size - sum(groups))
    still_unseen = deck_size - opening_size - later_random_draws
    valid_openings = 0
    total_payment_first = Fraction(0)
    total_adaptive = Fraction(0)

    for opening in _vectors(capacities, opening_size):
        opening_ways = _ways(capacities, opening)
        if not (opening[0] or opening[1] or opening[2]):
            continue
        valid_openings += opening_ways
        remaining = tuple(c - v for c, v in zip(capacities, opening, strict=True))
        forced_a = int(opening[2] == 0 and opening[0] > 0)
        forced_b = int(opening[2] == 0 and opening[0] == 0 and opening[1] > 0)

        for draws in _vectors(remaining, later_random_draws):
            draw_ways = _ways(remaining, draws)
            original_present = (opening[0] + draws[0], opening[1] + draws[1])
            retained = (original_present[0] - forced_a,
                        original_present[1] - forced_b)
            unseen_targets = tuple(i for i in range(2)
                                   if original_present[i] == 0)
            quick = opening[3] + draws[3]
            fuel = sum(opening[i] + draws[i] for i in (4, 5))
            sure = opening[6] + draws[6]
            coin = opening[7] + draws[7]

            for prize_bits in product((0, 1), repeat=len(unseen_targets)):
                prized = sum(prize_bits)
                if prized > prize_count:
                    continue
                weight = (opening_ways * draw_ways
                          * comb(still_unseen - len(unseen_targets),
                                 prize_count - prized))
                prize_by_target = dict(zip(unseen_targets, prize_bits, strict=True))
                zones = tuple(
                    HAND if retained[i] else
                    DECK if i in unseen_targets and prize_by_target[i] == 0
                    else UNAVAILABLE
                    for i in range(2)
                )
                if UNAVAILABLE in zones:
                    continue
                args = dict(a=zones[0], b=zones[1], quick_balls=quick,
                            discard_fuel=fuel, sure_pickups=sure,
                            coin_pickups=coin, free_slots=free_slots)
                total_payment_first += weight * payment_first_probability(**args)
                total_adaptive += weight * optimal_sequence_probability(**args)

    if valid_openings == 0:
        return QuickBallAccess(Fraction(0), Fraction(0), Fraction(0))
    sample_count = (valid_openings
                    * comb(deck_size - opening_size, later_random_draws)
                    * comb(still_unseen, prize_count))
    return QuickBallAccess(
        Fraction(valid_openings, comb(deck_size, opening_size)),
        total_payment_first / sample_count,
        total_adaptive / sample_count,
    )
