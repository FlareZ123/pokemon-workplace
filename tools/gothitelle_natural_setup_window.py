"""Exact turn-two unassisted Gothitelle + Rare Candy availability.

Setup timeline:
  opening seven drawn;
  six Prizes set from remaining deck;
  first personal turn draw: one card, Gothita may be placed;
  second personal turn draw: one card, Rare Candy may evolve the
      established Gothita into Gothitelle.

Other Basic Pokémon permit a legal initial seven-card hand without Gothita.
Opponent attacks, search, Supporters, Item/Ability locks, mulligan bonuses,
and any need to move Gothitelle to Active are out of scope.

Random Prize locations are marginalized; the two natural draws are
exchangeable uniform draws from cards remaining after the opener.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from math import comb


@dataclass(frozen=True)
class GothitelleSetup:
    total: int = 60
    opening: int = 7
    prizes: int = 6
    gothita: int = 3
    gothitelle: int = 2
    rare_candy: int = 4
    other_basics: int = 8

    def __post_init__(self) -> None:
        counts = (self.gothita, self.gothitelle,
                  self.rare_candy, self.other_basics)
        if min(counts) < 0 or sum(counts) > self.total:
            raise ValueError("invalid disjoint card counts")
        if not (0 < self.opening and 0 <= self.prizes
                and self.opening + self.prizes + 2 <= self.total):
            raise ValueError("not enough cards for setup and two draws")


@dataclass(frozen=True)
class SetupOdds:
    per_seven_card_attempt: Fraction
    legal_opener: Fraction
    conditional_valid_opener: Fraction


def legal_opener_probability(case: GothitelleSetup) -> Fraction:
    basics = case.gothita + case.other_basics
    return Fraction(
        comb(case.total, case.opening)
        - comb(case.total-basics, case.opening),
        comb(case.total, case.opening),
    )


def exact_unassisted_turn_two(case: GothitelleSetup) -> SetupOdds:
    n, opening = case.total, case.opening
    sizes = (case.gothita,case.gothitelle,case.rare_candy,
             case.other_basics,n-case.gothita-case.gothitelle-
             case.rare_candy-case.other_basics)
    denominator = comb(n,opening) * (n-opening) * (n-opening-1)
    numerator = 0
    for g,t,c,o in product(
        range(min(sizes[0],opening)+1),
        range(min(sizes[1],opening)+1),
        range(min(sizes[2],opening)+1),
        range(min(sizes[3],opening)+1),
    ):
        f=opening-g-t-c-o
        if f<0 or f>sizes[4] or g+o==0:
            continue
        opener=(g,t,c,o,f)
        opener_weight = 1
        for capacity,count in zip(sizes,opener):
            opener_weight *= comb(capacity,count)
        remains=tuple(a-b for a,b in zip(sizes,opener))
        for first in range(5):
            if remains[first]==0:
                continue
            if g+(first==0)==0:
                continue
            after_first=list(remains)
            after_first[first]-=1
            for second in range(5):
                if after_first[second]==0:
                    continue
                if t+(first==1)+(second==1)==0:
                    continue
                if c+(first==2)+(second==2)==0:
                    continue
                numerator += (
                    opener_weight*remains[first]*after_first[second]
                )
    event=Fraction(numerator,denominator)
    legal=legal_opener_probability(case)
    return SetupOdds(
        per_seven_card_attempt=event,
        legal_opener=legal,
        conditional_valid_opener=event/legal,
    )


def exhaustive_small(case: GothitelleSetup) -> SetupOdds:
    """Enumerate labeled opener, Prize, first draw and second draw."""
    cards=(
        "G"*case.gothita+"T"*case.gothitelle
        +"C"*case.rare_candy+"O"*case.other_basics
    )
    cards+="F"*(case.total-len(cards))
    ids=tuple(range(case.total))
    total=good=legal=0
    for opener in combinations(ids,case.opening):
        opener_set=set(opener)
        a=[cards[i] for i in opener]
        valid=("G" in a or "O" in a)
        remaining=tuple(i for i in ids if i not in opener_set)
        for prizes in combinations(remaining,case.prizes):
            prize_set=set(prizes)
            available=tuple(i for i in remaining if i not in prize_set)
            for first in available:
                for second in available:
                    if second==first:
                        continue
                    total+=1
                    if valid:
                        legal+=1
                    if (
                        valid
                        and ("G" in a or cards[first]=="G")
                        and ("T" in a or cards[first]=="T" or cards[second]=="T")
                        and ("C" in a or cards[first]=="C" or cards[second]=="C")
                    ):
                        good+=1
    event=Fraction(good,total)
    valid=Fraction(legal,total)
    return SetupOdds(event,valid,event/valid)
