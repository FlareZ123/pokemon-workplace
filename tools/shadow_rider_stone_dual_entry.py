"""One-shot Forest Seal Stone fallback for a dual hand-to-Bench entry route.

The Stone is usable when naturally observed and an eligible Pokemon V is
observed, and may search one missing target, or Heavy Ball for a Prized target.
This intentionally omits Item->V-host, Fog->V-host and other hand engines.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb, prod

from tools.opponent_bonus_matching import allocations
from tools.shadow_rider_dual_entry_launch import ShadowRiderDualEntry, choose


@dataclass(frozen=True)
class ShadowRiderStoneDualEntry:
    base: ShadowRiderDualEntry = ShadowRiderDualEntry()
    v_hosts: int = 3
    stones: int = 1

    def __post_init__(self):
        if self.v_hosts < 0 or self.v_hosts > self.base.other_basics:
            raise ValueError('host count exceeds other Basics')
        if self.stones != 1 or self.base.capacities[-1] < 1:
            raise ValueError('exactly one Stone in other-filler class required')

    @staticmethod
    def _routes(held: int, in_deck: int, prized: int,
                heavy_held: int, heavy_in_deck: int):
        if held:
            return (('held',0,0,0,0),)
        routes=[]
        if in_deck:
            routes += [('normal',1,0,0,0), ('stone_target',0,0,1,0)]
        if prized and heavy_held:
            routes.append(('heavy_held',0,1,0,1))
        if prized and heavy_in_deck:
            routes.append(('stone_heavy',0,1,1,0))
        return tuple(routes)

    @classmethod
    def reachable_with_stone(cls,*,r_held:int,l_held:int,
            r_deck:int,r_prized:int,l_deck:int,l_prized:int,
            sources:int,heavy_held:int,heavy_deck:int,energy:int,
            payment:str,hand_size:int)->bool:
        for rr,ll in product(
            cls._routes(r_held,r_deck,r_prized,heavy_held,heavy_deck),
            cls._routes(l_held,l_deck,l_prized,heavy_held,heavy_deck),
        ):
            _,rnorm,rheavy,rstone,rhand_heavy=rr
            _,lnorm,lheavy,lstone,lhand_heavy=ll
            normals=rnorm+lnorm
            heavy_used=rheavy+lheavy
            stone_used=rstone+lstone
            if normals>sources or heavy_used>1 or stone_used>1:
                continue
            if payment=='energy':
                if normals>energy:
                    continue
            elif payment=='mechanical':
                # One Basic Active is out of hand, one Stone is attached,
                # each initially held search Item is consumed, and a
                # single retained copy of each target is protected.
                expendable=(hand_size-int(bool(r_held))-int(bool(l_held))
                            -1-normals-rhand_heavy-lhand_heavy)
                if expendable<normals:
                    continue
            else:
                raise ValueError('unknown payment policy')
            return True
        return False

    def probability(self,bonus_draws:int=0,*,payment:str='energy',
                    require_wonder_tag:bool=True)->tuple[Fraction,Fraction]:
        """Return (old direct routes, additional Stone-only success)."""
        base=self.base
        if not 0<=bonus_draws<=base.deck_size-base.opening_size-base.prizes-1:
            raise ValueError('bonus draws exceed available deck')
        if payment not in ('energy','mechanical'):
            raise ValueError('invalid discard policy')
        n,h=base.deck_size,base.opening_size
        s=h+bonus_draws+1
        unseen=n-s
        sizes=base.capacities
        accept=Fraction(choose(n,h)-choose(n-base.other_basics-1-base.lele,h),choose(n,h))
        original=increment=Fraction()
        for counts in allocations(sizes,s):
            other,r,l,v,treasure,quick,heavy,energy,filler=counts
            if base.vmax-v<base.required_vmax:
                continue
            weighted_roles=[]
            if (w:=choose(s,h)-choose(s-other,h)):
                weighted_roles.append((w,l))
            if (w:=choose(s-other,h)-choose(s-other-l,h)):
                weighted_roles.append((w,l-1))
            if not weighted_roles:
                continue
            present_stone_host=Fraction(filler,base.capacities[-1])*(
                1-Fraction(choose(base.other_basics-self.v_hosts,other),
                           choose(base.other_basics,other))
            )
            seen_mass=Fraction(
                prod(choose(cap,c) for cap,c in zip(sizes,counts)),choose(n,s))
            unseen_r=1-r
            unseen_l=base.lele-l
            unseen_v=base.vmax-v
            unseen_h=1-heavy
            unspecified=unseen-unseen_r-unseen_l-unseen_v-unseen_h
            for pr in range(unseen_r+1):
                for pl in range(unseen_l+1):
                    for pv in range(unseen_v+1):
                        if base.vmax-v-pv < base.required_vmax:
                            continue
                        for ph in range(unseen_h+1):
                            rest=base.prizes-pr-pl-pv-ph
                            if not 0<=rest<=unspecified:
                                continue
                            prize_mass=Fraction(
                                choose(unseen_r,pr)*choose(unseen_l,pl)
                                *choose(unseen_v,pv)*choose(unseen_h,ph)
                                *choose(unspecified,rest),choose(unseen,base.prizes))
                            for role_weight, lele_ready in weighted_roles:
                                if require_wonder_tag:
                                    lele_held=lele_ready
                                    lele_deck=base.lele-l-pl
                                    lele_prized=pl
                                else:
                                    lele_held=1
                                    lele_deck=lele_prized=0
                                eligible=Fraction(role_weight,choose(s,h))
                                old=base.reachable(
                                    radiant_held=r,lele_held=lele_held,
                                    r_deck=1-r-pr,r_prize=pr,
                                    l_deck=lele_deck,l_prize=lele_prized,
                                    sources=treasure+quick,heavy=heavy,
                                    energy=energy,payment=payment,hand_size=s-1)
                                mass=seen_mass*prize_mass*eligible
                                if old:
                                    original+=mass
                                elif present_stone_host and self.reachable_with_stone(
                                        r_held=r,l_held=lele_held,
                                        r_deck=1-r-pr,r_prized=pr,
                                        l_deck=lele_deck,l_prized=lele_prized,
                                        sources=treasure+quick,
                                        heavy_held=heavy,heavy_deck=1-heavy-ph,
                                        energy=energy,payment=payment,hand_size=s-1):
                                    increment+=mass*present_stone_host
        return original/accept,increment/accept
