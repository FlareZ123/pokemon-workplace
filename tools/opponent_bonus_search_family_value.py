"""Prize-aware best-search value for ranked multi-copy target families.

A source can retrieve one card from the remaining deck after inspection.
Every target-family copy is known to be absent from the current hand.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb
from collections.abc import Sequence


def choose(n: int,k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class RankedFamilySearch:
    unseen_cards: int
    prizes: int
    family_copies: tuple[int,...]
    family_values: tuple[Fraction,...]

    def __post_init__(self) -> None:
        if self.unseen_cards < 1 or not 0 <= self.prizes <= self.unseen_cards:
            raise ValueError("invalid unseen deck or Prize count")
        if not self.family_copies or len(self.family_copies)!=len(self.family_values):
            raise ValueError("matched nonempty family vectors required")
        if any(c < 1 for c in self.family_copies):
            raise ValueError("each family must have a positive copy count")
        if sum(self.family_copies)>self.unseen_cards:
            raise ValueError("families exceed unseen cards")
        if any(v < 0 for v in self.family_values):
            raise ValueError("values must be nonnegative")
        if any(a < b for a,b in zip(self.family_values,self.family_values[1:])):
            raise ValueError("families must be ordered by descending value")

    def all_prized(self,cards: int) -> Fraction:
        """Probability a specified set of distinct cards is entirely Prized."""
        if not 0 <= cards <= self.unseen_cards:
            raise ValueError("invalid card count")
        return Fraction(
            choose(self.unseen_cards-cards,self.prizes-cards),
            choose(self.unseen_cards,self.prizes),
        )

    def fixed_choice_value(self) -> Fraction:
        return self.family_values[0]*(1-self.all_prized(self.family_copies[0]))

    def adaptive_choice_value(self) -> Fraction:
        prior=0
        total=Fraction()
        for copies,value in zip(self.family_copies,self.family_values):
            total+=value*(
                self.all_prized(prior)-self.all_prized(prior+copies)
            )
            prior+=copies
        return total

    def information_gain(self) -> Fraction:
        return self.adaptive_choice_value()-self.fixed_choice_value()

    @classmethod
    def from_values(
        cls, unseen_cards: int, prizes: int,
        families: Sequence[tuple[int,float]]
    ) -> "RankedFamilySearch":
        pairs=sorted(families,key=lambda x:x[1],reverse=True)
        return cls(
            unseen_cards,prizes,
            tuple(copies for copies,value in pairs),
            tuple(Fraction(str(value)) for copies,value in pairs),
        )
