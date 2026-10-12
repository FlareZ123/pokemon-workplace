"""K0 nonanticipative first-Item audit for the Regidrago+Energy triple gate.

An Item and any discard payment must be chosen before the first deck
search reveals the initial Prizes. The target of that first search and
subsequent Item actions may adapt after the first inspection. The
Energy payoff uses the pre-search future natural draw reference from
regidrago_joint_energy_gate, leaving future Energy unknown at decision.
This study restricts disposable hand payment to held Dragapult (D=0).
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from tools.regidrago_joint_energy_gate import energy_conditional
from tools.regidrago_joint_launch import Build,can_achieve_joint,choose


@dataclass(frozen=True)
class Result:
    clairvoyant: Fraction
    k0_first_item: Fraction
    legal_visible_hands: int
    positive_oracle_hands: int
    perfect_universal_hands: int

    @property
    def gap(self) -> Fraction:
        return self.clairvoyant-self.k0_first_item


def actions(hand: tuple[int,...]) -> tuple[str,...]:
    rv,other,dp,vip,qb,mt,bc,safe,filler=hand
    if safe:
        raise ValueError("D=0 only")
    found = []
    if bc: found.append("bc")
    if vip: found.append("vip")
    if qb and dp: found.append("qb_dp")
    if mt and dp: found.append("mt_dp")
    return tuple(found)


def forced(
    action: str,hand: tuple[int,...],rv_deck: int,dp_deck: int,
) -> bool:
    rv,_,dp,vip,qb,mt,bc,safe,_=hand
    held=rv>0
    if action=="bc":
        return can_achieve_joint(
            held,dp,vip,qb,mt,bc-1,safe,rv_deck,
            dp_deck-int(dp_deck>0),dp_deck>0)
    if action=="vip":
        return bool(
            (rv_deck and can_achieve_joint(
                True,dp,vip-1,qb,mt,bc,safe,rv_deck-1,dp_deck,False))
            or can_achieve_joint(
                held,dp,vip-1,qb,mt,bc,safe,rv_deck,dp_deck,False)
        )
    if action not in ("qb_dp","mt_dp"):
        raise ValueError("invalid physically payable first action")
    nq=qb-int(action=="qb_dp")
    nm=mt-int(action=="mt_dp")
    return bool(
        can_achieve_joint(held,dp-1,vip,nq,nm,bc,safe,
                          rv_deck,dp_deck,True)
        or (rv_deck and can_achieve_joint(
            True,dp-1,vip,nq,nm,bc,safe,rv_deck-1,dp_deck,True))
        or (action=="mt_dp" and dp_deck and can_achieve_joint(
            held,dp,vip,nq,nm,bc,safe,rv_deck,dp_deck-1,True))
    )


def analyze(
    build: Build, double_dragon: int=4, basic_energy: int=6,
    *, opener: int=7, prizes: int=6,
) -> Result:
    if build.safe:
        raise ValueError("D=0 protected-payment setting required")
    other=build.total-sum((
        build.regidrago_v,build.other_basics,build.dragapult,build.vip,
        build.quick_ball,build.treasure,build.compressor,build.safe))
    if other<double_dragon+basic_energy or opener+1+prizes>=build.total:
        raise ValueError("Invalid card allocation or remaining draw horizon")
    visible=opener+1
    groups=(build.regidrago_v,build.other_basics,build.dragapult,build.vip,
            build.quick_ball,build.treasure,build.compressor,build.safe,other)
    denominator=0
    perfect=best_nonanticipative=Fraction()
    hand_classes=positive=universal=0
    for prefix in product(*(range(min(n,visible)+1) for n in groups[:-1])):
        filler_held=visible-sum(prefix)
        if not 0<=filler_held<=other:
            continue
        hand=(*prefix,filler_held)
        basics=hand[0]+hand[1]
        placements=visible if basics>=2 else opener if basics==1 else 0
        if not placements:
            continue
        hand_classes+=1
        hand_weight=placements
        for count,held in zip(groups,hand):
            hand_weight*=choose(count,held)
        rv_left=build.regidrago_v-hand[0]
        dp_left=build.dragapult-hand[2]
        unknown_other=build.total-visible-rv_left-dp_left
        candidates=actions(hand)
        value={a:Fraction() for a in candidates}
        oracle=Fraction()
        prize_mass=0
        for pr in range(min(prizes,rv_left)+1):
            for pd in range(min(prizes-pr,dp_left)+1):
                po=prizes-pr-pd
                ways=(
                    choose(rv_left,pr)*choose(dp_left,pd)
                    *choose(unknown_other,po))
                if not ways:
                    continue
                prize_mass+=ways
                rv_deck=rv_left-pr
                dp_deck=dp_left-pd
                source=can_achieve_joint(
                    hand[0]>0,hand[2],hand[3],hand[4],hand[5],
                    hand[6],hand[7],rv_deck,dp_deck,False)
                if not source and not candidates:
                    continue
                energy=energy_conditional(
                    filler_held,po,unknown_other,other,
                    double_dragon,basic_energy,build.total-visible-prizes)
                if source:
                    oracle+=ways*energy
                for action in candidates:
                    if forced(action,hand,rv_deck,dp_deck):
                        value[action]+=ways*energy
        if oracle:
            positive+=1
        best=max(value.values(),default=Fraction())
        if best==oracle and oracle:
            universal+=1
        assert best<=oracle
        denominator+=hand_weight*prize_mass
        perfect+=hand_weight*oracle
        best_nonanticipative+=hand_weight*best
    return Result(
        perfect/denominator,best_nonanticipative/denominator,
        hand_classes,positive,universal)
