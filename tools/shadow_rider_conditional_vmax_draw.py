"""Exact conditional in-deck VMAX survival under optional extra mulligan draws."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


def choose(n:int,k:int)->int:
    return comb(n,k) if 0<=k<=n else 0


@dataclass(frozen=True)
class ConditionalVMAXDraw:
    deck_size:int=60
    opening_size:int=7
    prizes:int=6
    vmax_total:int=4
    vmax_in_opening:int=0
    min_remaining:int=2

    def __post_init__(self)->None:
        if not 0<=self.vmax_in_opening<=self.vmax_total<=self.deck_size:
            raise ValueError('invalid VMAX counts')
        if not 0<self.opening_size<self.deck_size:
            raise ValueError('invalid deck or opening')
        if not 0<=self.prizes<=self.deck_size-self.opening_size:
            raise ValueError('invalid Prize count')
        if self.vmax_in_opening>self.opening_size:
            raise ValueError('opening contains more VMAX than cards')
        if not 0<=self.min_remaining<=self.vmax_total:
            raise ValueError('invalid target requirement')

    def probability(self,draws:int)->Fraction:
        """Given opening VMAX count, chance >= minimum targets stay in deck."""
        unseen=self.deck_size-self.opening_size
        deck=unseen-self.prizes
        vmax_unseen=self.vmax_total-self.vmax_in_opening
        if not 0<=draws<=deck:
            raise ValueError('draw count exceeds deck')
        result=Fraction()
        for p in range(min(vmax_unseen,self.prizes)+1):
            prize_mass=Fraction(
                choose(vmax_unseen,p)*choose(unseen-vmax_unseen,self.prizes-p),
                choose(unseen,self.prizes),
            )
            after_prizes=vmax_unseen-p
            for consumed in range(min(after_prizes,draws)+1):
                if after_prizes-consumed<self.min_remaining:
                    continue
                draw_mass=Fraction(
                    choose(after_prizes,consumed)*choose(deck-after_prizes,draws-consumed),
                    choose(deck,draws),
                )
                result+=prize_mass*draw_mass
        return result

    def one_extra_draw_loss(self,already_drawn:int=1)->Fraction:
        p0=self.probability(already_drawn)
        p1=self.probability(already_drawn+1)
        assert p1<=p0
        return p0-p1
