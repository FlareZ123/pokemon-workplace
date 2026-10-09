"""Exact first-window resource-cover with a paid multi-output singleton.

The payment condition is deliberately narrow: at least three distinct
dedicated disposable cards must be in the observed opener-plus-bonus hand.
All card classes are physically disjoint, including the ordinary Basics.
Search-target access, actual card text errata and board execution are omitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb, prod

from tools.opponent_bonus_matching import allocations


def choose(n: int, k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class PaidBundleTwoDemand:
    deck_size: int = 60
    opening_size: int = 7
    prize_count: int = 6
    ordinary_basics: int = 12
    exclusive_a: int = 2
    exclusive_b: int = 2
    single_output_flexible: int = 2
    bundled_cards: int = 1
    safe_discards: int = 8
    bundle_payment: int = 3

    def __post_init__(self) -> None:
        counts = self.class_capacities
        if not 0 < self.opening_size < self.deck_size:
            raise ValueError("invalid opening size")
        if not 0 <= self.prize_count <= self.deck_size-self.opening_size:
            raise ValueError("invalid Prize count")
        if any(count < 0 for count in counts) or not self.ordinary_basics:
            raise ValueError("invalid card class counts")
        if not 0 <= self.bundle_payment <= self.safe_discards:
            raise ValueError("invalid payment")
        if not self.bundled_cards in (0,1):
            raise ValueError("model permits zero or one bundled singleton")

    @property
    def class_capacities(self) -> tuple[int,...]:
        groups = (
            self.ordinary_basics, self.exclusive_a, self.exclusive_b,
            self.single_output_flexible, self.bundled_cards,
            self.safe_discards
        )
        return (*groups,self.deck_size-sum(groups))

    @property
    def maximum_bonus_draws(self) -> int:
        return self.deck_size-self.opening_size-self.prize_count

    def probability(
        self, bonus_draws: int, *,
        allow_bundle: bool = True,
        ignore_payment: bool = False,
    ) -> Fraction:
        if not 0 <= bonus_draws <= self.maximum_bonus_draws:
            raise ValueError("invalid bonus draw count")
        n,h,b = self.deck_size,self.opening_size,self.ordinary_basics
        seen = h+bonus_draws
        sizes = self.class_capacities
        accept = Fraction(choose(n,h)-choose(n-b,h),choose(n,h))
        total = Fraction()
        for counts in allocations(sizes,seen):
            basics,a,b_only,flex,bundle,discards,other = counts
            assert basics+a+b_only+flex+bundle+discards+other==seen
            base = bool((a and b_only) or (flex and (a or b_only)) or flex>=2)
            paid = bool(bundle and (ignore_payment or discards>=self.bundle_payment))
            if not (base or (allow_bundle and paid)):
                continue
            chance_valid_opener = Fraction(
                choose(seen,h)-choose(seen-basics,h),
                choose(seen,h)
            )
            combination_mass = Fraction(
                prod(choose(size,count) for size,count in zip(sizes,counts)),
                choose(n,seen),
            )
            total += combination_mass * chance_valid_opener
        return total/accept

    def payment_gain(self, bonus_draws: int) -> Fraction:
        return (
            self.probability(bonus_draws,allow_bundle=True)
            -self.probability(bonus_draws,allow_bundle=False)
        )
