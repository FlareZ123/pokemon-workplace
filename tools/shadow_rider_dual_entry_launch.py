"""Exact Aichi Shadow Rider first-turn Radiant + Wonder Tag + dual VMAX access.

One Radiant Eternatus and two Tapu Lele-GX copies are ordinary Basics.
Their hand-to-Bench Abilities require distinct unconsumed physical cards;
Mysterious Treasure and Quick Ball each fetch one, and Hisuian Heavy Ball
can recover at most one Prized Basic. Search payments are policy dependent.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb, prod

from tools.opponent_bonus_matching import allocations


def choose(n: int,k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class ShadowRiderDualEntry:
    deck_size: int = 60
    opening_size: int = 7
    prizes: int = 6
    other_basics: int = 11
    lele: int = 2
    vmax: int = 4
    treasure: int = 4
    quick_ball: int = 1
    heavy_ball: int = 1
    energy: int = 11
    required_vmax: int = 2

    @property
    def capacities(self) -> tuple[int,...]:
        # Other Basics, Radiant, Tapu Lele, VMAX, Treasure, Quick,
        # Heavy Ball, Psychic Energy, and neutral other.
        categories=(self.other_basics,1,self.lele,self.vmax,
                    self.treasure,self.quick_ball,self.heavy_ball,self.energy)
        return (*categories,self.deck_size-sum(categories))

    def __post_init__(self) -> None:
        if not 0 < self.opening_size < self.deck_size:
            raise ValueError('invalid opening')
        if not 0 <= self.prizes <= self.deck_size-self.opening_size:
            raise ValueError('invalid Prize count')
        if not 0 <= self.required_vmax <= self.vmax:
            raise ValueError('invalid VMAX requirement')
        if self.lele < 1 or any(n<0 for n in self.capacities):
            raise ValueError('invalid deck classes')

    @staticmethod
    def reachable(*, radiant_held:int, lele_held:int, r_deck:int,
                  r_prize:int, l_deck:int, l_prize:int, sources:int,
                  heavy:int, energy:int, payment:str, hand_size:int) -> bool:
        r_routes=('none',) if radiant_held else tuple(
            x for x,ok in (('normal',r_deck>0),('heavy',r_prize>0)) if ok
        )
        l_routes=('none',) if lele_held else tuple(
            x for x,ok in (('normal',l_deck>0),('heavy',l_prize>0)) if ok
        )
        for r in r_routes:
            for l in l_routes:
                normal=(r=='normal')+(l=='normal')
                prize_search=(r=='heavy')+(l=='heavy')
                if normal>sources or prize_search>heavy:
                    continue
                if payment=='energy':
                    if normal>energy: continue
                elif payment=='mechanical':
                    # After selecting the starting Active, preserve one
                    # hand copy of each entry trigger and the used Items.
                    expendable=(hand_size-radiant_held-int(lele_held>0)
                                -normal-prize_search)
                    if expendable<normal:continue
                else:
                    raise ValueError('unknown payment policy')
                return True
        return False

    def probability(self, bonus_draws:int=0, *,
                    payment:str='energy',require_wonder_tag:bool=True,
                    role_aware:bool=True) -> Fraction:
        if not 0 <= bonus_draws <= self.deck_size-self.opening_size-self.prizes-1:
            raise ValueError('bonus draws and one natural draw exceed deck')
        if payment not in ('energy','mechanical'):
            raise ValueError('unknown payment policy')
        n,h=self.deck_size,self.opening_size
        s=h+1+bonus_draws  # one natural first-turn draw going second
        unseen=n-s
        sizes=self.capacities
        accept=Fraction(choose(n,h)-choose(n-self.other_basics-1-self.lele,h),choose(n,h))
        result=Fraction()
        for counts in allocations(sizes,s):
            other,r,l,v,treasure,quick,heavy,energy,_=counts
            if self.vmax-v<self.required_vmax:
                continue
            weights=[]
            # With an unrelated opening Basic, retain all observed Lele.
            w_other=choose(s,h)-choose(s-other,h)
            if w_other:weights.append((w_other,l))
            # Without an unrelated Basic, lead one opening Lele.
            w_lele=choose(s-other,h)-choose(s-other-l,h)
            if role_aware:
                if w_lele:weights.append((w_lele,l-1))
            else:
                # The role-blind oracle overcredits Basic setup copies,
                # including a forced Active Radiant or Lele.
                w_all=choose(s-other-l,h)-choose(s-other-l-r,h)
                weights=[(w_other+w_lele+w_all,l)]
            if not weights:
                continue
            observed_weight=Fraction(prod(choose(cap,k) for cap,k in zip(sizes,counts)),choose(n,s))
            unseen_r=1-r
            unseen_l=self.lele-l
            unseen_v=self.vmax-v
            other_unseen=unseen-unseen_r-unseen_l-unseen_v
            for pr in range(unseen_r+1):
                for pl in range(max(0,self.prizes-pr-other_unseen-unseen_v), min(unseen_l,self.prizes-pr)+1):
                    for pv in range(min(unseen_v,self.prizes-pr-pl)+1):
                        rest=self.prizes-pr-pl-pv
                        if not 0 <= rest <= other_unseen or self.vmax-v-pv < self.required_vmax:
                            continue
                        prize_weight=Fraction(
                            choose(unseen_r,pr)*choose(unseen_l,pl)
                            *choose(unseen_v,pv)*choose(other_unseen,rest),
                            choose(unseen,self.prizes)
                        )
                        for w,lele_in_hand in weights:
                            if not require_wonder_tag:
                                # Simpler Radiant-only launch contract.
                                success=self.reachable(radiant_held=r,lele_held=1,
                                    r_deck=1-r-pr,r_prize=pr,
                                    l_deck=0,l_prize=0,sources=treasure+quick,
                                    heavy=heavy,energy=energy,payment=payment,
                                    hand_size=s-1)
                            else:
                                success=self.reachable(
                                    radiant_held=r,lele_held=lele_in_hand,
                                    r_deck=1-r-pr,r_prize=pr,
                                    l_deck=self.lele-l-pl,l_prize=pl,
                                    sources=treasure+quick,heavy=heavy,
                                    energy=energy,payment=payment,
                                    hand_size=s-1)
                            if success:
                                result+=observed_weight*prize_weight*Fraction(w,choose(s,h))
        return result/accept
