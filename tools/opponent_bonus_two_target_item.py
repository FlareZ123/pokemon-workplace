"""Exact two-singleton Pokemon access via paid one-output search Items.

Both singleton targets are non-starting Pokemon and are not in the
designated discardable class. Searchers are abstract Ultra Ball-like Items:
each is used at most once, discards two designated safe cards, and
retrieves one still-in-deck target. Item lock and other game-state rules
are outside this static first-window model.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb, prod

from tools.opponent_bonus_matching import allocations


def choose(n: int,k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class TwoTargetPaidItem:
    deck_size: int = 60
    hand_size: int = 7
    prizes: int = 6
    ordinary_basics: int = 12
    item_sources: int = 3
    safe_fodder: int = 12
    payment_per_item: int = 2

    def __post_init__(self) -> None:
        if not 0 < self.hand_size < self.deck_size:
            raise ValueError("invalid deck and hand")
        if not 0 <= self.prizes <= self.deck_size-self.hand_size:
            raise ValueError("invalid Prize count")
        if self.ordinary_basics <= 0 or min(
            self.item_sources,self.safe_fodder,self.payment_per_item
        ) < 0:
            raise ValueError("invalid category counts or payment")
        if sum(self.capacities)!=self.deck_size or min(self.capacities)<0:
            raise ValueError("categories exceed physical deck")

    @property
    def capacities(self) -> tuple[int,...]:
        # The A and B Pokémon are distinct non-starting singletons.
        groups=(self.ordinary_basics,1,1,self.item_sources,self.safe_fodder)
        return (*groups,self.deck_size-sum(groups))

    @property
    def max_bonus_draws(self) -> int:
        return self.deck_size-self.hand_size-self.prizes

    @staticmethod
    def _unprized_missing(
        unseen: int,prizes: int,missing: int
    ) -> Fraction:
        return Fraction(
            choose(unseen-missing,prizes),
            choose(unseen,prizes),
        )

    def probability(
        self, bonus_draws: int,
        *, ignore_payment: bool = False,
        ignore_prizes: bool = False,
    ) -> Fraction:
        if not 0 <= bonus_draws <= self.max_bonus_draws:
            raise ValueError("invalid bonus count")
        n,h,b=self.deck_size,self.hand_size,self.ordinary_basics
        s=h+bonus_draws
        m=n-s
        sizes=self.capacities
        accepted=Fraction(choose(n,h)-choose(n-b,h),choose(n,h))
        total=Fraction()
        for counts in allocations(sizes,s):
            basics,a,target_b,sources,fodder,filler=counts
            missing=2-a-target_b
            if sources<missing:
                continue
            if not ignore_payment and fodder<missing*self.payment_per_item:
                continue
            chance_deck=(
                Fraction(1) if ignore_prizes else
                self._unprized_missing(m,self.prizes,missing)
            )
            legal_opener=Fraction(
                choose(s,h)-choose(s-basics,h),choose(s,h)
            )
            mass=Fraction(
                prod(choose(size,count) for size,count in zip(sizes,counts)),
                choose(n,s)
            )
            total+=mass*legal_opener*chance_deck
        return total/accepted

    def ablation(self, bonus_draws: int) -> dict[str,Fraction]:
        return {
            "ideal":self.probability(
                bonus_draws,ignore_prizes=True,ignore_payment=True
            ),
            "payment_only":self.probability(
                bonus_draws,ignore_prizes=True
            ),
            "prize_only":self.probability(
                bonus_draws,ignore_payment=True
            ),
            "physical":self.probability(bonus_draws),
        }
