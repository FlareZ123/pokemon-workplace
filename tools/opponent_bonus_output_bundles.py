"""Exact grouped assembly of bundled and exclusive-mode resource outputs.

A physical resource can offer several alternative ONE-USE output bundles.
The owner chooses at most one bundle per copy. The model assumes each
declared bundle is feasible, independently of payment or deck targets.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb, prod

from tools.opponent_bonus_matching import allocations


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class OutputBundleClass:
    count: int
    basic: bool
    output_choices: tuple[frozenset[int], ...]


@dataclass(frozen=True)
class BonusOutputBundles:
    opening_size: int
    prize_count: int
    requirements: int
    classes: tuple[OutputBundleClass, ...]

    def __post_init__(self) -> None:
        if not 1 <= self.requirements <= 16:
            raise ValueError("requirements must be 1..16")
        if not self.classes or any(
            card.count < 0 or any(
                role < 0 or role >= self.requirements
                for choice in card.output_choices for role in choice
            )
            for card in self.classes
        ):
            raise ValueError("invalid cards or output requirements")
        if not 0 < self.opening_size < self.deck_size:
            raise ValueError("invalid opening size")
        if not 0 <= self.prize_count <= self.deck_size - self.opening_size:
            raise ValueError("invalid Prize count")
        if self.basic_count == 0:
            raise ValueError("at least one ordinary Basic starting card required")

    @property
    def deck_size(self) -> int:
        return sum(card.count for card in self.classes)

    @property
    def basic_count(self) -> int:
        return sum(card.count for card in self.classes if card.basic)

    @property
    def maximum_bonus_draws(self) -> int:
        return self.deck_size - self.opening_size - self.prize_count

    @staticmethod
    def _class_reachable(card: OutputBundleClass, copies: int) -> frozenset[int]:
        choices = [sum(1 << role for role in choice) for choice in card.output_choices]
        covered = {0}
        for _ in range(copies):
            covered = covered | {old | option for old in covered for option in choices}
        return frozenset(covered)

    def feasible(self, counts: tuple[int, ...]) -> bool:
        reachable = {0}
        complete = (1 << self.requirements) - 1
        for card, copies in zip(self.classes, counts):
            masks = self._class_reachable(card, copies)
            reachable = {old | option for old in reachable for option in masks}
            if complete in reachable:
                return True
        return complete in reachable

    def probability(self, bonus_draws: int) -> Fraction:
        if not 0 <= bonus_draws <= self.maximum_bonus_draws:
            raise ValueError("invalid bonus-draw count")
        n, h, b = self.deck_size, self.opening_size, self.basic_count
        seen = h + bonus_draws
        capacities = tuple(card.count for card in self.classes)
        accepted = Fraction(choose(n, h)-choose(n-b, h),choose(n,h))
        success = Fraction()
        for counts in allocations(capacities, seen):
            if not self.feasible(counts):
                continue
            basic_count = sum(
                k for card,k in zip(self.classes,counts) if card.basic
            )
            legal_opener_given_seen = Fraction(
                choose(seen,h)-choose(seen-basic_count,h),choose(seen,h)
            )
            mass = Fraction(
                prod(choose(cap,k) for cap,k in zip(capacities,counts)),
                choose(n,seen)
            )
            success += mass * legal_opener_given_seen
        return success/accepted

    def marginal_values(self, payoff: float, draw_cap: int) -> tuple[float, ...]:
        if payoff < 0 or not 0 <= draw_cap <= self.maximum_bonus_draws:
            raise ValueError("invalid payoff or bonus cap")
        probabilities = [self.probability(i) for i in range(draw_cap+1)]
        return tuple(
            float(payoff * (b-a))
            for a,b in zip(probabilities,probabilities[1:])
        )
