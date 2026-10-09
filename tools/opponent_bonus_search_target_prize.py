"""Exact singleton search-target Prize risk after conditioned openings.

A single one-output search source can complete two singleton requirements
when exactly one target is seen and the other is still in the deck.
Two dedicated safe hand cards are required for the modeled search payment.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb, prod

from tools.opponent_bonus_matching import allocations


def choose(n: int, k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class SingletonSearchPrize:
    deck_size: int = 60
    opening_size: int = 7
    prizes: int = 6
    basics: int = 12
    safe_discards: int = 8
    discard_payment: int = 2

    def __post_init__(self) -> None:
        if not 0 < self.opening_size < self.deck_size:
            raise ValueError("invalid deck or opening")
        if not 0 <= self.prizes <= self.deck_size-self.opening_size:
            raise ValueError("invalid prize count")
        if self.basics <= 0 or not 0 <= self.discard_payment <= self.safe_discards:
            raise ValueError("invalid Basic count or safe-payment count")
        if self.basics+3+self.safe_discards>self.deck_size:
            raise ValueError("card categories exceed deck")
        # Exactly one physical A, B, and search source card, all non-Basic.

    @property
    def capacities(self) -> tuple[int,...]:
        return (
            self.basics,1,1,1,self.safe_discards,
            self.deck_size-self.basics-3-self.safe_discards,
        )

    @property
    def maximum_bonus_draws(self) -> int:
        return self.deck_size-self.opening_size-self.prizes

    def components(self, bonus_draws: int) -> tuple[Fraction,Fraction]:
        """Return p(both seen), p(exactly one seen and playable search).

        Prize positions are marginalized for the hand-presence terms.
        """
        if not 0 <= bonus_draws <= self.maximum_bonus_draws:
            raise ValueError("invalid bonus count")
        n,h,b = self.deck_size,self.opening_size,self.basics
        s=h+bonus_draws
        sizes=self.capacities
        accept=Fraction(choose(n,h)-choose(n-b,h),choose(n,h))
        direct=Fraction()
        needs_search=Fraction()
        for counts in allocations(sizes,s):
            seen_basic,a,target_b,source,safe,_ = counts
            direct_hit=bool(a and target_b)
            search_case=bool(
                a+target_b==1 and source and safe>=self.discard_payment
            )
            if not (direct_hit or search_case):
                continue
            valid=Fraction(choose(s,h)-choose(s-seen_basic,h),choose(s,h))
            hypergeom=Fraction(
                prod(choose(c,x) for c,x in zip(sizes,counts)),
                choose(n,s),
            )
            mass=valid*hypergeom
            if direct_hit:
                direct+=mass
            else:
                needs_search+=mass
        return direct/accept,needs_search/accept

    def probability(
        self, bonus_draws: int, *, assume_target_in_deck: bool = False
    ) -> Fraction:
        direct,source=self.components(bonus_draws)
        if assume_target_in_deck:
            return direct+source
        # Conditional on a target missing from both opener and bonus,
        # its unseen position is uniformly among N-H-m positions; six
        # of them are Prize cards.
        available=Fraction(
            self.deck_size-self.opening_size-bonus_draws-self.prizes,
            self.deck_size-self.opening_size-bonus_draws,
        )
        return direct+available*source

    def prize_overstatement(self, bonus_draws: int) -> Fraction:
        _,search_case=self.components(bonus_draws)
        return search_case*Fraction(
            self.prizes,
            self.deck_size-self.opening_size-bonus_draws,
        )
