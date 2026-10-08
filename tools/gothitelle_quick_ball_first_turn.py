"""Exact turn-two Gothitelle setup with one first-turn Quick Ball option.

Starting from a legal seven-card opener, the player draws once on turn one.
If a Gothita is already in opening/first-draw hand, put it into play.
Otherwise, play Quick Ball if it is present, an approved other card can pay
its one discard, and a Gothita remains unprized in deck; search and bench it.
Draw once more on turn two. The Gothic evolution + Rare Candy are required.

This marginalizes random Prizes exactly while retaining searchability, a
per-card compulsory payment, and the change in deck count after searching.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from gothitelle_natural_setup_window import (
    GothitelleSetup,
    SetupOdds,
    exact_unassisted_turn_two,
    legal_opener_probability,
)


def choose(n:int,k:int)->int:
    return comb(n,k) if 0<=k<=n else 0


@dataclass(frozen=True)
class QuickSetup:
    total:int=60
    opening:int=7
    prizes:int=6
    gothita:int=3
    gothitelle:int=2
    rare_candy:int=4
    other_basics:int=8
    quick_ball:int=4
    approved_discard:int=12

    def __post_init__(self)->None:
        counts=self.categories
        if (
            min(counts)<0 or sum(counts)!=self.total
            or self.opening<1 or self.prizes<0
            or self.total-self.opening-self.prizes-2<=0
        ):
            raise ValueError("invalid Quick Ball setup partition or window")

    @property
    def categories(self)->tuple[int,...]:
        focal=(
            self.gothita,self.gothitelle,self.rare_candy,
            self.other_basics,self.quick_ball,self.approved_discard,
        )
        return focal+(self.total-sum(focal),)

    def natural_only(self)->GothitelleSetup:
        return GothitelleSetup(
            total=self.total,opening=self.opening,prizes=self.prizes,
            gothita=self.gothita,gothitelle=self.gothitelle,
            rare_candy=self.rare_candy,other_basics=self.other_basics,
        )


@dataclass(frozen=True)
class QuickSetupResults:
    natural:SetupOdds
    quick_enabled:SetupOdds

    @property
    def improvement_conditional_legal(self)->Fraction:
        return (
            self.quick_enabled.conditional_valid_opener
            - self.natural.conditional_valid_opener
        )


def _after_search_success(
    *,
    other_unknown:int,
    remaining_gothita:int,
    missing_evolution:int,
    missing_candy:int,
    prizes:int,
)->Fraction:
    """Average exactly over prizes after the first turn's observed draw."""
    if remaining_gothita==0:
        return Fraction(0)
    if missing_evolution and missing_candy:
        return Fraction(0)
    if prizes>other_unknown+remaining_gothita:
        raise ValueError("invalid Prize count")
    denominator=choose(other_unknown+remaining_gothita,prizes)
    deck_after_search=other_unknown+remaining_gothita-prizes-1
    if deck_after_search<=0:
        return Fraction(0)

    probability=Fraction(0)
    for g_prizes in range(0,min(remaining_gothita,prizes)+1):
        if g_prizes==remaining_gothita:
            continue
        ways=(
            choose(remaining_gothita,g_prizes)
            *choose(other_unknown,prizes-g_prizes)
        )
        if not ways:
            continue
        prize_weight=Fraction(ways,denominator)
        if missing_evolution:
            # Given G prize count, remaining Prizes are sampled from
            # the non-G category uniformly.
            remaining_missing=Fraction(
                missing_evolution*(other_unknown-(prizes-g_prizes)),
                other_unknown,
            )
            draw_chance=remaining_missing/deck_after_search
        elif missing_candy:
            remaining_missing=Fraction(
                missing_candy*(other_unknown-(prizes-g_prizes)),
                other_unknown,
            )
            draw_chance=remaining_missing/deck_after_search
        else:
            draw_chance=Fraction(1)
        probability+=prize_weight*draw_chance
    return probability


def exact_quick_setup(case:QuickSetup)->QuickSetupResults:
    natural=exact_unassisted_turn_two(case.natural_only())
    n=case.total
    dims=case.categories
    attempts=comb(n,case.opening)*(n-case.opening)
    outcome=Fraction(0)
    for g,t,c,o,q,d in product(*(
        range(min(s,case.opening)+1) for s in dims[:6]
    )):
        f=case.opening-g-t-c-o-q-d
        if f<0 or f>dims[6] or g+o==0:
            continue
        opener=(g,t,c,o,q,d,f)
        weight=1
        for avail,got in zip(dims,opener):
            weight*=choose(avail,got)
        remaining=tuple(avail-got for avail,got in zip(dims,opener))
        for first in range(7):
            count=remaining[first]
            if count==0:
                continue
            after_first=list(remaining)
            after_first[first]-=1
            t_seen=t+(first==1)
            c_seen=c+(first==2)
            g_seen=g+(first==0)
            q_seen=q+(first==4)
            d_seen=d+(first==5)
            if g_seen:
                # No search: the second natural draw is exchangeable
                # among the N-8 cards not seen in opening or first draw.
                if t_seen and c_seen:
                    second_chance=Fraction(1)
                elif t_seen:
                    second_chance=Fraction(after_first[2],n-case.opening-1)
                elif c_seen:
                    second_chance=Fraction(after_first[1],n-case.opening-1)
                else:
                    second_chance=Fraction(0)
            elif q_seen and d_seen:
                # A Gothita is still required, and must survive the
                # random Prize assignment for first-turn Quick Ball.
                second_chance=_after_search_success(
                    other_unknown=sum(after_first)-after_first[0],
                    remaining_gothita=after_first[0],
                    missing_evolution=after_first[1] if not t_seen else 0,
                    missing_candy=after_first[2] if not c_seen else 0,
                    prizes=case.prizes,
                )
            else:
                second_chance=Fraction(0)
            outcome+=Fraction(weight*count,attempts)*second_chance

    legal=legal_opener_probability(case.natural_only())
    enriched=SetupOdds(
        per_seven_card_attempt=outcome,
        legal_opener=legal,
        conditional_valid_opener=outcome/legal,
    )
    return QuickSetupResults(natural=natural,quick_enabled=enriched)
