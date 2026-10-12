"""Exact Item-joint plus naturally supplied turn-two Regidrago Energy gate.

This is a deliberately restricted three-channel intersection:
(1) first-turn Regidrago V availability, (2) Dragapult ex discarded
by a legal finite Item sequence, and (3) a naturally observed pair of
Energy cards capable of paying Apex Dragon via two manual attachments.
It neither requires VSTAR nor proves a playable turn-two attack.

The future turn-two natural draw is sampled from the untouched shuffled
post-Prize deck for this comparison, before modeled Item card removal.
Our Items only remove *non-Energy* targets, so thinning can improve
subsequent real Energy draws. This defines a conservative source-access
reference, without making an unmodeled item draw-order assumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb

from tools.regidrago_joint_launch import Build, can_achieve_joint, choose


@dataclass(frozen=True)
class ThreeChannel:
    item_joint: Fraction
    energy_pair: Fraction
    item_and_natural_energy: Fraction

    @property
    def naive_independent_product(self) -> Fraction:
        return self.item_joint*self.energy_pair


@lru_cache(maxsize=None)
def energy_conditional(
    other_held: int, nonreg_prized: int, nonreg_unseen: int,
    other_group: int, double_dragon: int, basic_energy: int,
    deck_after_prizes: int,
) -> Fraction:
    """P(Energy pair) given an Item-state hand and Reg/Dragon Prize count.

    The OTHER Item-planner category contains all Energy and filler.
    DDE and basic Energy occupy physical slots in that group.
    Remaining Prizes are uniformly selected among non-Reg/non-Dragapult
    slots, so their expected remaining Energy is hypergeometric.
    """
    filler = other_group-double_dragon-basic_energy
    if filler < 0:
        raise ValueError("Energy categories exceed Item planner filler pool")
    numerator = Fraction()
    for d in range(min(other_held,double_dragon)+1):
        for b in range(min(other_held-d,basic_energy)+1):
            f=other_held-d-b
            if f > filler:
                continue
            weight=Fraction(
                choose(double_dragon,d)*choose(basic_energy,b)
                *choose(filler,f),choose(other_group,other_held),
            )
            if d>=1 and d+b>=2:
                chance=Fraction(1)
            elif d>=1:
                chance=(
                    Fraction(double_dragon-d+basic_energy-b,deck_after_prizes)
                    *Fraction(nonreg_unseen-nonreg_prized,nonreg_unseen)
                )
            elif b>=1:
                chance=(
                    Fraction(double_dragon-d,deck_after_prizes)
                    *Fraction(nonreg_unseen-nonreg_prized,nonreg_unseen)
                )
            else:
                chance=Fraction()
            numerator += weight*chance
    return numerator


def analyze(
    build: Build, double_dragon: int = 4, basic_energy: int = 6,
    *, opener: int = 7, prizes: int = 6,
) -> ThreeChannel:
    if build.safe:
        raise ValueError("Restricted study only supports D=0 payment policy")
    other = build.total-sum((
        build.regidrago_v,build.other_basics,build.dragapult,build.vip,
        build.quick_ball,build.treasure,build.compressor,build.safe,
    ))
    if min(build.__dict__.values()) < 0 or other < double_dragon+basic_energy:
        raise ValueError("Invalid source/energy card composition")
    groups=(
        build.regidrago_v,build.other_basics,build.dragapult,build.vip,
        build.quick_ball,build.treasure,build.compressor,build.safe,other,
    )
    visible=opener+1
    if visible+prizes>=build.total:
        raise ValueError("No next-turn natural draw remains")

    weight_all = weight_joint = 0
    weighted_energy = weighted_triple = Fraction()
    for prefix in product(*(range(min(n,visible)+1) for n in groups[:-1])):
        other_hand=visible-sum(prefix)
        if not 0<=other_hand<=other:
            continue
        hand=(*prefix,other_hand)
        basics=hand[0]+hand[1]
        opening_placements=visible if basics>=2 else visible-1 if basics==1 else 0
        if not opening_placements:
            continue
        hand_ways=opening_placements
        for count,held in zip(groups,hand):
            hand_ways*=choose(count,held)
        unseen_reg=build.regidrago_v-hand[0]
        unseen_drag=build.dragapult-hand[2]
        nonreg_unseen=build.total-visible-unseen_reg-unseen_drag
        for prized_reg in range(min(prizes,unseen_reg)+1):
            for prized_drag in range(min(prizes-prized_reg,unseen_drag)+1):
                nonreg_prized=prizes-prized_reg-prized_drag
                prize_ways=(
                    choose(unseen_reg,prized_reg)
                    *choose(unseen_drag,prized_drag)
                    *choose(nonreg_unseen,nonreg_prized)
                )
                if not prize_ways:
                    continue
                weight=hand_ways*prize_ways
                weight_all+=weight
                energy=energy_conditional(
                    other_hand,nonreg_prized,nonreg_unseen,other,
                    double_dragon,basic_energy,build.total-visible-prizes,
                )
                weighted_energy+=weight*energy
                joint=can_achieve_joint(
                    hand[0]>0,hand[2],hand[3],hand[4],hand[5],hand[6],
                    hand[7],unseen_reg-prized_reg,unseen_drag-prized_drag,
                    False,
                )
                if joint:
                    weight_joint+=weight
                    weighted_triple+=weight*energy

    return ThreeChannel(
        Fraction(weight_joint,weight_all),
        weighted_energy/weight_all,
        weighted_triple/weight_all,
    )
