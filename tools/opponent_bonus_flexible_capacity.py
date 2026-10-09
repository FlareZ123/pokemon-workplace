"""Exact two-demand assembly under one-use flexible-card capacity.

All strategic cards in this minimal model are non-Basic and physically
disjoint from ordinary Basic starters. Prize cards are marginalized.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class FlexibleTwoDemand:
    deck_size: int
    opening_size: int
    prizes: int
    basic_starters: int
    a_only: int
    b_only: int
    flexible: int

    def __post_init__(self) -> None:
        if self.deck_size <= 0 or not 0 < self.opening_size < self.deck_size:
            raise ValueError("invalid deck or opening size")
        if not 0 <= self.prizes <= self.deck_size - self.opening_size:
            raise ValueError("invalid Prize count")
        if self.basic_starters <= 0 or min(
            self.a_only, self.b_only, self.flexible
        ) < 0:
            raise ValueError("invalid basic or target counts")
        if (self.basic_starters + self.a_only + self.b_only + self.flexible
                > self.deck_size):
            raise ValueError("card classes exceed deck")
        if self.a_only + self.flexible == 0 or self.b_only + self.flexible == 0:
            raise ValueError("each demand must have some possible supplier")

    @property
    def max_bonus_draws(self) -> int:
        return self.deck_size - self.opening_size - self.prizes

    def none(self, excluded: int, bonus: int) -> Fraction:
        if not 0 <= excluded <= (
            self.a_only + self.b_only + self.flexible
        ):
            raise ValueError("invalid exclusion")
        if not 0 <= bonus <= self.max_bonus_draws:
            raise ValueError("invalid bonus draw count")
        n, h, b = self.deck_size, self.opening_size, self.basic_starters
        eligible = choose(n, h) - choose(n-b, h)
        eligible_without = choose(n-excluded, h) - choose(n-b-excluded, h)
        return (
            Fraction(eligible_without, eligible)
            * Fraction(choose(n-h-excluded, bonus), choose(n-h, bonus))
        )

    def simultaneous_coverage(self, bonus: int) -> Fraction:
        """Idealized flexible card covers A and B in the same use."""
        a, b, f = self.a_only, self.b_only, self.flexible
        return (
            1 - self.none(a+f, bonus) - self.none(b+f, bonus)
            + self.none(a+b+f, bonus)
        )

    def one_use_gap(self, bonus: int) -> Fraction:
        """P(exactly one F, zero A and zero B in the observed cards)."""
        f = self.flexible
        if not f:
            return Fraction(0)
        k = self.a_only + self.b_only + f
        return f * (self.none(k-1, bonus) - self.none(k, bonus))

    def one_use_coverage(self, bonus: int) -> Fraction:
        """Each flexible physical card may satisfy only one demand."""
        return self.simultaneous_coverage(bonus) - self.one_use_gap(bonus)

    def bonus_costs(self, payoff: float, cap: int, *, one_use: bool) -> tuple[float, ...]:
        if payoff < 0 or not 0 <= cap <= self.max_bonus_draws:
            raise ValueError("invalid payoff or cap")
        function = self.one_use_coverage if one_use else self.simultaneous_coverage
        probabilities = [function(i) for i in range(cap+1)]
        return tuple(
            float(payoff*(b-a)) for a,b in zip(probabilities,probabilities[1:])
        )
