"""Exact accepted-opening access for one Gladion+Communication Grand Tree rescue.

The event is a narrow, rules-consistent card-access certificate, not a
game-win or full gameplay probability: starting seven holds a Basic Gothita,
the singleton Grand Tree, Gladion and Pokémon Communication; singleton
Gothorita is Prized; singleton Gothitelle avoids hand, Prizes and subsequent
natural draws, remaining searchable by Grand Tree on the second turn.

All ordinary cards are sampled without replacement and the opening is
conditioned on at least one Basic Gothita.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class OpeningRescueModel:
    total: int = 60
    basics: int = 4
    gladion: int = 2
    communication: int = 2
    opening: int = 7
    prizes: int = 6
    draws: int = 2

    def __post_init__(self) -> None:
        if min(
            self.total, self.basics, self.gladion, self.communication,
            self.opening, self.prizes, self.draws,
        ) < 0:
            raise ValueError("Negative population parameter")
        if self.total < self.basics + self.gladion + self.communication + 3:
            raise ValueError("Not enough slots for the three critical singletons")
        if self.opening > self.total:
            raise ValueError("Opening exceeds population")
        if self.prizes > self.total - self.opening:
            raise ValueError("Prize sample exceeds remaining deck")
        if self.draws > self.total - self.opening - self.prizes:
            raise ValueError("Draw horizon exceeds the deck")
        if choose(self.total, self.opening) == choose(
            self.total-self.basics, self.opening
        ):
            raise ValueError("No eligible Basic opener can be drawn")

    def accepted_opening_hands(self) -> int:
        return (
            choose(self.total, self.opening)
            - choose(self.total-self.basics, self.opening)
        )

    def qualifying_opening_hands(self) -> int:
        """Opening holds Basic+Grand Tree+Gladion+Communication, no evolutions."""
        filler = self.total-self.basics-self.gladion-self.communication-3
        ways = 0
        for b in range(1, self.basics + 1):
            for g in range(1, self.gladion + 1):
                for c in range(1, self.communication + 1):
                    n = self.opening-1-b-g-c
                    ways += (
                        choose(self.basics, b)
                        * choose(self.gladion, g)
                        * choose(self.communication, c)
                        * choose(filler, n)
                    )
        return ways

    def probability(self) -> Fraction:
        """Conditional on accepted seven, then six Prizes and natural draws."""
        hand = Fraction(
            self.qualifying_opening_hands(),
            self.accepted_opening_hands(),
        )
        remaining_after_hand = self.total - self.opening
        prize = Fraction(
            choose(remaining_after_hand-2, self.prizes-1),
            choose(remaining_after_hand, self.prizes),
        )
        remaining_after_prizes = remaining_after_hand - self.prizes
        keep_stage2_in_deck = Fraction(
            remaining_after_prizes-self.draws,
            remaining_after_prizes,
        )
        return hand * prize * keep_stage2_in_deck
