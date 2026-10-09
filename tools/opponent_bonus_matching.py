"""Exact conditional bonus-draw assembly via Hall matching.

Observing H opening plus m bonus cards is equivalent to a uniform sample of
H+m physical cards, weighted by the probability that a uniformly chosen
H-card opening subset of those cards contains at least one ordinary Basic.
Prize positions marginalize by exchangeability.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb, prod
from collections.abc import Iterator

from tools.opponent_bonus_coverage import OpponentBonusCoverage


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def allocations(capacities: tuple[int, ...], total: int) -> Iterator[tuple[int, ...]]:
    """All class-count vectors whose sum is total."""
    if not capacities:
        if total == 0:
            yield ()
        return
    cap, *rest = capacities
    reserve = sum(rest)
    for amount in range(max(0, total-reserve), min(cap,total)+1):
        for suffix in allocations(tuple(rest), total-amount):
            yield (amount, *suffix)


@dataclass(frozen=True)
class BonusMatching:
    model: OpponentBonusCoverage

    def satisfies(self, counts: tuple[int, ...], *, single_use: bool) -> bool:
        role_masks = [
            sum(1 << group for group in card.groups)
            for card in self.model.classes
        ]
        required = self.model.required_count
        if not single_use:
            return all(
                any(count and mask & (1 << role)
                    for count,mask in zip(counts,role_masks))
                for role in range(required)
            )
        # Hall's marriage condition for physical one-use card resources:
        # every set of demands must have at least that many distinct
        # available cards eligible to cover at least one of those demands.
        for demand_subset in range(1, 1 << required):
            eligible = sum(
                count
                for count,mask in zip(counts,role_masks)
                if mask & demand_subset
            )
            if eligible < demand_subset.bit_count():
                return False
        return True

    def probability(self, bonus_draws: int, *, single_use: bool) -> Fraction:
        mod = self.model
        if not 0 <= bonus_draws <= mod.max_bonus_draws:
            raise ValueError("invalid bonus count")
        n, h, b = mod.deck_size, mod.opening_size, mod.basic_count
        s = h + bonus_draws
        capacities = tuple(card.count for card in mod.classes)
        opener_valid = Fraction(choose(n,h)-choose(n-b,h),choose(n,h))
        total = Fraction(0)
        for present in allocations(capacities,s):
            if not self.satisfies(present,single_use=single_use):
                continue
            seen_basics = sum(
                count for count,card in zip(present,mod.classes) if card.basic
            )
            if not seen_basics:
                continue
            union_mass = Fraction(
                prod(choose(cap,count) for cap,count in zip(capacities,present)),
                choose(n,s),
            )
            initial_basic_given_union = Fraction(
                choose(s,h)-choose(s-seen_basics,h),
                choose(s,h),
            )
            total += union_mass * initial_basic_given_union
        return total / opener_valid

    def marginal_costs(
        self, payoff: float, cap: int, *, single_use: bool
    ) -> tuple[float, ...]:
        if payoff < 0 or not 0 <= cap <= self.model.max_bonus_draws:
            raise ValueError("invalid payoff or cap")
        p = [self.probability(m,single_use=single_use) for m in range(cap+1)]
        return tuple(float(payoff*(q-p)) for p,q in zip(p,p[1:]))
