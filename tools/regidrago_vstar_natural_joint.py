"""Exact four-channel Regidrago material exposure with natural VSTAR card.

Same physical Item planner and pre-search turn-two reference as
regidrago_joint_energy_gate, now additionally require Regidrago VSTAR
naturally in the first nine exposed cards. The turn-two draw can provide
VSTAR or a missing Energy, but cannot provide both simultaneously.
Mysterious Treasure searching for VSTAR is deliberately excluded:
this is a restrictive material sub-event, not full attack readiness.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product

from tools.regidrago_joint_launch import Build,can_achieve_joint,choose


@dataclass(frozen=True)
class FourChannel:
    item_joint: Fraction
    energy_and_vstar: Fraction
    item_energy_and_vstar: Fraction

    @property
    def naive_product(self) -> Fraction:
        return self.item_joint*self.energy_and_vstar


@lru_cache(maxsize=None)
def natural_pair_and_vstar(
    other_held: int,prized_nonreg: int,nonreg_unseen: int,
    other_group: int,double_dragon: int,basic_energy: int,vstar: int,
    unprized_deck: int,
) -> Fraction:
    """Material gate inside a known Item hand/Reg+Dragon Prize class."""
    filler=other_group-double_dragon-basic_energy-vstar
    if filler<0:
        raise ValueError("Material categories exceed other deck cards")
    chance=Fraction()
    for d in range(min(other_held,double_dragon)+1):
        for b in range(min(other_held-d,basic_energy)+1):
            for v in range(min(other_held-d-b,vstar)+1):
                f=other_held-d-b-v
                if f>filler:
                    continue
                ways=(
                    choose(double_dragon,d)*choose(basic_energy,b)
                    *choose(vstar,v)*choose(filler,f))
                share=Fraction(ways,choose(other_group,other_held))
                deck_survival=Fraction(
                    nonreg_unseen-prized_nonreg,nonreg_unseen)
                if v:
                    if d>=1 and d+b>=2:
                        source=Fraction(1)
                    elif d>=1:
                        source=(
                            Fraction(double_dragon-d+basic_energy-b,unprized_deck)
                            *deck_survival)
                    elif b:
                        source=(
                            Fraction(double_dragon-d,unprized_deck)
                            *deck_survival)
                    else:
                        source=Fraction()
                else:
                    if d>=1 and d+b>=2:
                        source=Fraction(vstar,unprized_deck)*deck_survival
                    else:
                        source=Fraction()
                chance+=share*source
    return chance


def analyze(
    build: Build,double_dragon: int=4,basic_energy: int=6,vstar: int=3,
    *,opener: int=7,prizes: int=6,
) -> FourChannel:
    if build.safe:
        raise ValueError("D=0 Item-payment policy required")
    other=build.total-sum((
        build.regidrago_v,build.other_basics,build.dragapult,build.vip,
        build.quick_ball,build.treasure,build.compressor,build.safe))
    if other<double_dragon+basic_energy+vstar or opener+1+prizes>=build.total:
        raise ValueError("Invalid VSTAR/energy allocation or draw horizon")

    groups=(build.regidrago_v,build.other_basics,build.dragapult,build.vip,
            build.quick_ball,build.treasure,build.compressor,build.safe,other)
    visible=opener+1
    denom=joint_items=0
    materials=four=Fraction()
    for prefix in product(*(range(min(n,visible)+1) for n in groups[:-1])):
        f=visible-sum(prefix)
        if not 0<=f<=other:
            continue
        hand=(*prefix,f)
        basics=hand[0]+hand[1]
        opening_placements=visible if basics>=2 else opener if basics==1 else 0
        if not opening_placements:
            continue
        hand_ways=opening_placements
        for n,k in zip(groups,hand):
            hand_ways*=choose(n,k)
        rv_left=build.regidrago_v-hand[0]
        dp_left=build.dragapult-hand[2]
        unseen_other=build.total-visible-rv_left-dp_left
        for rprized in range(min(prizes,rv_left)+1):
            for dprized in range(min(prizes-rprized,dp_left)+1):
                pr_other=prizes-rprized-dprized
                prize_ways=(
                    choose(rv_left,rprized)*choose(dp_left,dprized)
                    *choose(unseen_other,pr_other))
                if not prize_ways:
                    continue
                weight=hand_ways*prize_ways
                denom+=weight
                source=natural_pair_and_vstar(
                    f,pr_other,unseen_other,other,
                    double_dragon,basic_energy,vstar,
                    build.total-visible-prizes)
                materials+=weight*source
                item=can_achieve_joint(
                    hand[0]>0,hand[2],hand[3],hand[4],hand[5],
                    hand[6],hand[7],rv_left-rprized,dp_left-dprized,False)
                if item:
                    joint_items+=weight
                    four+=weight*source
    return FourChannel(
        Fraction(joint_items,denom),materials/denom,four/denom)
