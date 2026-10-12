"""Exact Regidrago V + discarded Dragapult + VSTAR search in one Item window.

Physical Item actions: Battle VIP Pass puts Regidrago V on Bench;
Battle Compressor discards Dragapult from deck; Quick Ball and
Mysterious Treasure discard a held Dragapult (D=0; no invented filler)
to search their actual eligible Pokémon types. Mysterious Treasure can
search Dragon VSTAR or another Dragapult, permitting second-order Item
payment chains. Items are consumed once, deck cards are consumed on
search, and six Prizes are enumerated exactly. The policy sees hidden
Prize state when choosing an Item route: an optimistic full-info
existence envelope pending a K0 pre-search proof.

This remains early material access, not evolution, Energy or attack.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product

from tools.regidrago_joint_launch import Build, can_achieve_joint, choose


@lru_cache(maxsize=None)
def can_achieve_vstar(
    reg_in_play: bool, vstar_hand: bool, drag_hand: int,
    vip: int,quick: int,treasure: int,compressor: int,
    reg_deck: int,vstar_deck: int,drag_deck: int,loaded: bool,
) -> bool:
    """Finite monotonic Item DFS with truthful VSTAR/Dragon tutor targets."""
    if reg_in_play and vstar_hand and loaded:
        return True
    if compressor and drag_deck and can_achieve_vstar(
        reg_in_play,vstar_hand,drag_hand,vip,quick,treasure,compressor-1,
        reg_deck,vstar_deck,drag_deck-1,True):
        return True
    if vip and reg_deck and can_achieve_vstar(
        True,vstar_hand,drag_hand,vip-1,quick,treasure,compressor,
        reg_deck-1,vstar_deck,drag_deck,loaded):
        return True
    if drag_hand:
        if quick:
            if can_achieve_vstar(
                reg_in_play,vstar_hand,drag_hand-1,
                vip,quick-1,treasure,compressor,
                reg_deck,vstar_deck,drag_deck,True):
                return True
            if reg_deck and can_achieve_vstar(
                True,vstar_hand,drag_hand-1,
                vip,quick-1,treasure,compressor,
                reg_deck-1,vstar_deck,drag_deck,True):
                return True
        if treasure:
            # Pay with one held Dragapult, then take exactly one optional
            # Dragon/Psychic search target. No all-purpose infinite search.
            if can_achieve_vstar(
                reg_in_play,vstar_hand,drag_hand-1,
                vip,quick,treasure-1,compressor,
                reg_deck,vstar_deck,drag_deck,True):
                return True
            if reg_deck and can_achieve_vstar(
                True,vstar_hand,drag_hand-1,
                vip,quick,treasure-1,compressor,
                reg_deck-1,vstar_deck,drag_deck,True):
                return True
            if vstar_deck and can_achieve_vstar(
                reg_in_play,True,drag_hand-1,
                vip,quick,treasure-1,compressor,
                reg_deck,vstar_deck-1,drag_deck,True):
                return True
            if drag_deck and can_achieve_vstar(
                reg_in_play,vstar_hand,drag_hand,
                vip,quick,treasure-1,compressor,
                reg_deck,vstar_deck,drag_deck-1,True):
                return True
    return False


@dataclass(frozen=True)
class Frontier:
    reg_and_discard: Fraction
    reg_discard_and_vstar: Fraction

    @property
    def vstar_gate_fraction(self) -> Fraction:
        return (
            self.reg_discard_and_vstar/self.reg_and_discard
            if self.reg_and_discard else Fraction()
        )


def analyze(build: Build, vstar: int=3, *,
            opener: int=7,prizes: int=6) -> Frontier:
    if build.safe:
        raise ValueError("D=0 only; no exogenously expendable hand fillers")
    other=build.total-sum((
        build.regidrago_v,build.other_basics,build.dragapult,
        build.vip,build.quick_ball,build.treasure,build.compressor,
        build.safe,vstar))
    if other<0 or opener+1+prizes>build.total:
        raise ValueError("Invalid deck composition or opening")
    groups=(build.regidrago_v,build.other_basics,vstar,build.dragapult,
            build.vip,build.quick_ball,build.treasure,build.compressor,other)
    visible=opener+1
    denominator=reg_only=both=0

    for prefix in product(*(range(min(n,visible)+1) for n in groups[:-1])):
        f=visible-sum(prefix)
        if not 0<=f<=other:
            continue
        hand=(*prefix,f)
        basics=hand[0]+hand[1]
        placement=visible if basics>=2 else opener if basics==1 else 0
        if not placement:
            continue
        hand_ways=placement
        for n,c in zip(groups,hand):
            hand_ways*=choose(n,c)
        rv_left=build.regidrago_v-hand[0]
        vs_left=vstar-hand[2]
        dp_left=build.dragapult-hand[3]
        remaining=build.total-visible-rv_left-vs_left-dp_left
        for pr in range(min(prizes,rv_left)+1):
            for pv in range(min(prizes-pr,vs_left)+1):
                for pd in range(min(prizes-pr-pv,dp_left)+1):
                    pother=prizes-pr-pv-pd
                    prize_ways=(
                        choose(rv_left,pr)*choose(vs_left,pv)
                        *choose(dp_left,pd)*choose(remaining,pother))
                    if not prize_ways:
                        continue
                    weight=hand_ways*prize_ways
                    denominator+=weight
                    r=rv_left-pr
                    v=vs_left-pv
                    d=dp_left-pd
                    reg_only+=weight*can_achieve_joint(
                        hand[0]>0,hand[3],hand[4],hand[5],
                        hand[6],hand[7],0,r,d,False)
                    both+=weight*can_achieve_vstar(
                        hand[0]>0,hand[2]>0,hand[3],
                        hand[4],hand[5],hand[6],hand[7],
                        r,v,d,False)
    return Frontier(Fraction(reg_only,denominator),Fraction(both,denominator))
