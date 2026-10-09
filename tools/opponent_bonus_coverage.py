"""Exact multi-role card coverage after opponent bonus draws.

Physical card classes may satisfy multiple strategic requirements and also
provide ordinary Basic starting Pokemon. Prize placements are marginalized.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class CoverageClass:
    count: int
    groups: frozenset[int]
    basic: bool = False


@dataclass(frozen=True)
class OpponentBonusCoverage:
    opening_size: int
    prize_count: int
    required_count: int
    classes: tuple[CoverageClass, ...]

    def __post_init__(self) -> None:
        if self.required_count < 1 or not self.classes:
            raise ValueError("nonempty requirements and card classes needed")
        if any(card.count < 0 or any(
            i < 0 or i >= self.required_count for i in card.groups
        ) for card in self.classes):
            raise ValueError("invalid class")
        if not 0 < self.opening_size < self.deck_size:
            raise ValueError("invalid opening size")
        if not 0 <= self.prize_count <= self.deck_size - self.opening_size:
            raise ValueError("invalid Prize count")
        if not self.basic_count:
            raise ValueError("at least one ordinary Basic required")
        if any(not any(
            card.count and i in card.groups for card in self.classes
        ) for i in range(self.required_count)):
            raise ValueError("uncovered requirement")

    @property
    def deck_size(self) -> int:
        return sum(card.count for card in self.classes)

    @property
    def basic_count(self) -> int:
        return sum(card.count for card in self.classes if card.basic)

    @property
    def max_bonus_draws(self) -> int:
        return self.deck_size - self.opening_size - self.prize_count

    def no_groups(self, subset: frozenset[int], draws: int) -> Fraction:
        if any(i < 0 or i >= self.required_count for i in subset):
            raise ValueError("invalid requirement")
        if not 0 <= draws <= self.max_bonus_draws:
            raise ValueError("bonus draws exceed the post-Prize deck")
        k = sum(c.count for c in self.classes if c.groups & subset)
        t = sum(c.count for c in self.classes if c.basic and c.groups & subset)
        n, h, b = self.deck_size, self.opening_size, self.basic_count
        accepted = choose(n, h) - choose(n - b, h)
        eligible_without_targets = choose(n - k, h) - choose(n - b - k + t, h)
        return (
            Fraction(eligible_without_targets, accepted)
            * Fraction(choose(n - h - k, draws), choose(n - h, draws))
        )

    def probability(self, draws: int) -> Fraction:
        total = Fraction(0)
        for r in range(self.required_count + 1):
            for ix in combinations(range(self.required_count), r):
                total += (-1) ** r * self.no_groups(frozenset(ix), draws)
        return total

    def marginal_values(self, payoff: float, cap: int) -> tuple[float, ...]:
        if payoff < 0 or not 0 <= cap <= self.max_bonus_draws:
            raise ValueError("invalid payoff or cap")
        p = [self.probability(i) for i in range(cap + 1)]
        return tuple(float(payoff * (b-a)) for a,b in zip(p,p[1:]))
