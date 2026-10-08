"""Joint Prize-aware access to a first-turn Sky Field payload and turn-two Gothitelle.

Counts one fixed 60-card no-draw-engine line under a pre-existing
Collapsed Stadium and live Stadium-from-hand lock: first-turn Quick Ball
must discard Sky Field, and Gothita must enter by end of that turn.
Quick Ball either searches Gothita from deck or uses a legal zero-result
Basic search when Gothita is already naturally observed.
Turn-two Rare Candy and Gothitelle must be available.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from gothitelle_natural_setup_window import legal_opener_probability
from gothitelle_quick_ball_first_turn import (
    QuickSetup, _after_search_success,
)


def choose(n:int,k:int)->int:
    return comb(n,k) if 0<=k<=n else 0


@dataclass(frozen=True)
class JointLineConfig:
    total:int=60
    opening:int=7
    prizes:int=6
    gothita:int=3
    gothitelle:int=2
    rare_candy:int=4
    other_basics:int=8
    quick_ball:int=4
    sky_field:int=2

    @property
    def categories(self)->tuple[int,...]:
        labels=(
            self.gothita,self.gothitelle,self.rare_candy,
            self.other_basics,self.quick_ball,self.sky_field
        )
        return labels+(self.total-sum(labels),)

    def __post_init__(self)->None:
        if (
            self.total<=0 or min(self.categories)<0
            or self.opening<1 or self.prizes<0
            or self.total-self.opening-self.prizes-2<1
        ):
            raise ValueError("invalid physical joint line pool")

    def with_quick_payment_as_sky(self)->QuickSetup:
        return QuickSetup(
            total=self.total,opening=self.opening,prizes=self.prizes,
            gothita=self.gothita,gothitelle=self.gothitelle,
            rare_candy=self.rare_candy,other_basics=self.other_basics,
            quick_ball=self.quick_ball,approved_discard=self.sky_field,
        )


@dataclass(frozen=True)
class JointLineProbability:
    found_gothita:Fraction
    gothita_already_seen:Fraction
    legal_opening:Fraction

    @property
    def full_line(self)->Fraction:
        return self.found_gothita+self.gothita_already_seen

    @property
    def conditional_on_valid_opener(self)->Fraction:
        return self.full_line/self.legal_opening


def exact_joint_line(case:JointLineConfig)->JointLineProbability:
    n=case.total
    dims=case.categories
    denominator=comb(n,case.opening)*(n-case.opening)
    fetched=Fraction(0)
    naturally_seen=Fraction(0)
    for g,t,c,o,q,s in product(*(
        range(min(size,case.opening)+1) for size in dims[:6]
    )):
        f=case.opening-g-t-c-o-q-s
        if f<0 or f>dims[6] or g+o==0:
            continue
        opening=(g,t,c,o,q,s,f)
        ways=1
        for present,size in zip(opening,dims):
            ways*=choose(size,present)
        remaining=tuple(size-present for size,present in zip(dims,opening))
        for first in range(len(dims)):
            count=remaining[first]
            if count==0:
                continue
            observed_g=g+int(first==0)
            observed_t=t+int(first==1)
            observed_c=c+int(first==2)
            observed_q=q+int(first==4)
            observed_s=s+int(first==5)
            if not (observed_q and observed_s):
                continue
            after=list(remaining)
            after[first]-=1
            weight=Fraction(ways*count,denominator)
            if observed_g:
                if observed_t and observed_c:
                    success=Fraction(1)
                elif observed_t:
                    success=Fraction(after[2],n-case.opening-1)
                elif observed_c:
                    success=Fraction(after[1],n-case.opening-1)
                else:
                    success=Fraction(0)
                naturally_seen+=weight*success
            else:
                prob=_after_search_success(
                    other_unknown=sum(after)-after[0],
                    remaining_gothita=after[0],
                    missing_evolution=after[1] if not observed_t else 0,
                    missing_candy=after[2] if not observed_c else 0,
                    prizes=case.prizes,
                )
                fetched+=weight*prob
    natural_case=case.with_quick_payment_as_sky()
    legal=legal_opener_probability(natural_case.natural_only())
    return JointLineProbability(fetched,naturally_seen,legal)
