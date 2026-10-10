"""Exact union of direct/drawn/Arven-fetched Communication on turn two.

The event begins with Grand Tree, Gladion, and one Basic in the opening
hand, singleton Gothorita in Prize, and singleton Gothitelle available
in deck through turn two. A singleton Pokémon Communication can be in
opening hand, drawn on T1/T2, or fetched by Arven on T1 if going second.
The returned Prize Gothorita is then put into deck by Communication.

This is a sharply scoped access certificate, not a win-rate model.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


def ch(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class ArvenUnionAccess:
    total: int = 60
    basics: int = 4
    gladion: int = 2
    arven: int = 2
    opening: int = 7
    prizes: int = 6

    def __post_init__(self) -> None:
        if min(
            self.total, self.basics, self.gladion, self.arven,
            self.opening, self.prizes,
        ) < 0:
            raise ValueError("Negative population")
        if self.total < self.basics + self.gladion + self.arven + 4:
            raise ValueError("Not enough deck slots")
        if not 0 <= self.opening <= self.total:
            raise ValueError("Invalid opening size")
        if not 0 <= self.prizes <= self.total-self.opening:
            raise ValueError("Invalid Prize population")
        if self.total-self.opening-self.prizes < 4:
            raise ValueError("Need at least four cards after Prize setting")
        if ch(self.total,self.opening)==ch(self.total-self.basics,self.opening):
            raise ValueError("No legal Basic opener can occur")

    def probability(self, *, going_second: bool) -> Fraction:
        """Accepted opening, actual Prize placement, then two actor draws."""
        deck_after_hand = self.total-self.opening
        deck_after_prizes = deck_after_hand-self.prizes
        filler = self.total-self.basics-self.gladion-self.arven-4
        accepted = ch(self.total,self.opening)-ch(
            self.total-self.basics,self.opening
        )
        answer = Fraction()
        for b in range(1,self.basics+1):
            for g in range(1,self.gladion+1):
                for a in range(self.arven+1):
                    for comm_hand in (0,1):
                        leftover = self.opening-1-b-g-a-comm_hand
                        ways = (
                            ch(self.basics,b)*ch(self.gladion,g)
                            *ch(self.arven,a)*ch(1,comm_hand)
                            *ch(filler,leftover)
                        )
                        if not ways:
                            continue
                        if comm_hand:
                            # Prize singleton Gothorita; Stage2 remains in deck.
                            prize = Fraction(
                                ch(deck_after_hand-2,self.prizes-1),
                                ch(deck_after_hand,self.prizes),
                            )
                            draw = Fraction(
                                deck_after_prizes-2,deck_after_prizes
                            )
                        else:
                            # Prize S1, keep both S2 and Communication in deck.
                            prize = Fraction(
                                ch(deck_after_hand-3,self.prizes-1),
                                ch(deck_after_hand,self.prizes),
                            )
                            if not going_second:
                                # First two natural draws contain Comm, no S2.
                                draw = Fraction(
                                    2*(deck_after_prizes-2),
                                    deck_after_prizes*(deck_after_prizes-1),
                                )
                            elif a:
                                # Can prefetch if first draw isn't S2 or Comm.
                                # Drawing Comm directly first is equally good.
                                draw = (
                                    Fraction(
                                        deck_after_prizes-2,
                                        deck_after_prizes*(deck_after_prizes-1),
                                    )
                                    + Fraction(
                                        deck_after_prizes-3,
                                        deck_after_prizes,
                                    )
                                )
                            else:
                                # Arven may be drawn on T1 but could be Prized.
                                # Under Prize condition, other category count
                                # is deck_after_hand-3; of these exactly
                                # prizes-1 are selected as further Prizes.
                                remaining_arven = self.arven-a
                                prizes_total = ch(
                                    deck_after_hand-3,self.prizes-1
                                )
                                draw = Fraction()
                                for prized_arven in range(remaining_arven+1):
                                    chance = Fraction(
                                        ch(remaining_arven,prized_arven)
                                        *ch(
                                            deck_after_hand-3-remaining_arven,
                                            self.prizes-1-prized_arven,
                                        ),
                                        prizes_total,
                                    )
                                    in_deck = remaining_arven-prized_arven
                                    D = deck_after_prizes
                                    first_comm = Fraction(D-2,D*(D-1))
                                    first_arven = Fraction(
                                        in_deck*(D-3),D*(D-2)
                                    )
                                    second_comm = Fraction(
                                        D-2-in_deck,D*(D-1)
                                    )
                                    draw += chance*(
                                        first_comm+first_arven+second_comm
                                    )
                        answer += Fraction(ways,accepted)*prize*draw
        return answer

    def going_second_advantage(self) -> Fraction:
        return (
            self.probability(going_second=True)
            - self.probability(going_second=False)
        )
