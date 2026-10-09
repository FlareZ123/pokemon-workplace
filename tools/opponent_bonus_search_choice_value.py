"""Exact value of first-deck-search Prize information for ranked singleton goals.

All ranked targets are distinct singleton cards known to be absent from the
hand, and the unseen physical positions contain P uniform Prize cards.
The searcher learns the remaining searchable deck before selecting an
eligible output. Non-target mandatory searches can retrieve a filler.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb
from collections.abc import Sequence


def choose(n: int,k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class RankedSingletonSearch:
    unseen_cards: int
    prize_count: int
    target_values: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        if self.unseen_cards < 1 or not 0 <= self.prize_count <= self.unseen_cards:
            raise ValueError("invalid unseen and Prize counts")
        if not 1 <= len(self.target_values) <= self.unseen_cards:
            raise ValueError("invalid target count")
        if any(v < 0 for v in self.target_values):
            raise ValueError("target utilities must be nonnegative")
        if any(a < b for a,b in zip(self.target_values,self.target_values[1:])):
            raise ValueError("target values must be sorted descending")

    def fixed_choice_value(self) -> Fraction:
        """Pick best singleton in advance, without inspecting the deck."""
        return self.target_values[0]*Fraction(
            self.unseen_cards-self.prize_count,self.unseen_cards
        )

    def adaptive_choice_value(self) -> Fraction:
        """Choose the highest-value target available after deck inspection."""
        m,p=self.unseen_cards,self.prize_count
        denominator=choose(m,p)
        return sum(
            (
                value * Fraction(
                    choose(m-index-1,p-index),denominator
                )
                for index,value in enumerate(self.target_values)
            ),
            Fraction(),
        )

    def information_gain(self) -> Fraction:
        return self.adaptive_choice_value()-self.fixed_choice_value()

    def available_target_count_probability(self, count: int) -> Fraction:
        """Hypergeometric distribution of unprized singletons."""
        m,p,k=self.unseen_cards,self.prize_count,len(self.target_values)
        if not 0 <= count <= k:
            return Fraction()
        # count searchable targets, k-count Prized targets
        return Fraction(
            choose(k,count)*choose(m-k,p-(k-count)),
            choose(m,p),
        )

    def probability_no_targets_available(self) -> Fraction:
        return self.available_target_count_probability(0)


def from_numbers(unseen_cards: int,prize_count: int,values: Sequence[float]) -> RankedSingletonSearch:
    """Convenience converter for decimal use; core computations stay rational."""
    return RankedSingletonSearch(
        unseen_cards,
        prize_count,
        tuple(Fraction(str(value)) for value in sorted(values,reverse=True)),
    )
