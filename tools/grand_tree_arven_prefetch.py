"""One-turn-ahead Arven prefetch of Pokémon Communication for Grand Tree.

Turn 1 going second: Arven searches the deck for Pokémon Communication,
then its Supporter allowance is spent. Turn 2: Gladion can take a
critical Prized evolution Pokémon into hand; Pokémon Communication
returns it into deck; Grand Tree evolves an eligible Basic.

This tightly constrained exact access event excludes alternate routes
and does not imply an actual win or unrestricted setup probability.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


def nchoosek(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class ArvenPrefetchOpening:
    total: int = 60
    basics: int = 4
    arven: int = 2
    gladion: int = 2
    opening: int = 7
    prizes: int = 6

    def __post_init__(self) -> None:
        if min(
            self.total, self.basics, self.arven, self.gladion,
            self.opening, self.prizes
        ) < 0:
            raise ValueError("Negative parameter")
        if self.total < self.basics + self.arven + self.gladion + 4:
            raise ValueError("Not enough cards for singleton slots")
        if self.opening > self.total:
            raise ValueError("Opening size exceeds deck")
        if self.prizes > self.total-self.opening:
            raise ValueError("Prize size exceeds deck")
        if self.total-self.opening-self.prizes < 3:
            raise ValueError("Arven prefetch plus two natural draws require three deck cards")
        if not nchoosek(self.total,self.opening) > nchoosek(
            self.total-self.basics,self.opening
        ):
            raise ValueError("There must be a possible Basic opening")

    def conditional_opening_probability(self) -> Fraction:
        """Basic+Grand Tree+Gladion+Arven, no S1/S2/Communication in hand."""
        filler = self.total-self.basics-self.arven-self.gladion-4
        favorable = 0
        for b in range(1,self.basics+1):
            for a in range(1,self.arven+1):
                for g in range(1,self.gladion+1):
                    f = self.opening-1-b-a-g
                    favorable += (
                        nchoosek(self.basics,b)
                        * nchoosek(self.arven,a)
                        * nchoosek(self.gladion,g)
                        * nchoosek(filler,f)
                    )
        accepted = (
            nchoosek(self.total,self.opening)
            - nchoosek(self.total-self.basics,self.opening)
        )
        return Fraction(favorable,accepted)

    def certificate_probability_going_second(self) -> Fraction:
        """Arven T1 fetches Comm, Gladion T2 rescues priced singleton S1."""
        N = self.total-self.opening
        deck_after_prizes = N-self.prizes
        prize_event = Fraction(
            nchoosek(N-3,self.prizes-1),
            nchoosek(N,self.prizes),
        )
        # First draw must leave both S2 and Communication in deck;
        # Arven then removes Communication; second draw must leave S2.
        first_draw = Fraction(deck_after_prizes-2,deck_after_prizes)
        next_deck = deck_after_prizes-2
        second_draw = Fraction(next_deck-1,next_deck)
        return (
            self.conditional_opening_probability()
            * prize_event * first_draw * second_draw
        )


def min_turn_to_use_both_supporters(*, going_first: bool) -> int:
    """Earliest actor-turn index with distinct Arven then Gladion plays."""
    return 3 if going_first else 2
