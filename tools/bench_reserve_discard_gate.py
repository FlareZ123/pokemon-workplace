"""State-dependent Basic reserve in discard-gated Item first-turn payability.

The model reserves a number of extra Basics remaining in hand after the
mandatory Active Basic; only Basics in excess of reserve may be discarded.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from basic_valid_discard_quota import basic_valid_discard_quota


@dataclass(frozen=True)
class BenchReserveGate:
    basic_valid_opening: Fraction
    source_held: Fraction
    payable_with_reserved_basics: Fraction
    conditional_payable: Fraction
    required_discards: int
    reserved_extra_basics: int


def bench_reserve_discard_gate(
    *,deck_size:int=60,basics:int=12,source_copies:int=4,
    disposable:int=8,opening_size:int=7,prize_count:int=6,
    required_discards:int=2,reserved_extra_basics:int=1,
) -> BenchReserveGate:
    """Allow F, Q duplicates and max(0,B_in_hand-reserved_extra_basics).

    Protecting a held Basic is a proxy for preserving a later Bench/evolution
    line. The actual game can obtain or deploy Bench Pokémon by many effects;
    none of those future uses is modeled here.
    """
    args=(deck_size,basics,source_copies,disposable,opening_size,
          prize_count,required_discards,reserved_extra_basics)
    if any(type(x) is not int for x in args):
        raise TypeError('counts must be integers')
    if (basics<1 or source_copies<1 or disposable<0 or required_discards<0
        or reserved_extra_basics<0 or basics+source_copies+disposable>deck_size
        or not 0<opening_size<deck_size-prize_count):
        raise ValueError('infeasible deck, discard or reserve configuration')
    other=deck_size-basics-source_copies-disposable
    den=comb(deck_size,opening_size)
    valid=Fraction(den-comb(deck_size-basics,opening_size),den)
    held=payable=Fraction()
    for b,q,f,p in product(*(range(min(n,opening_size)+1) for n in
                            (basics,source_copies,disposable,other))):
        if not b or b+q+f+p!=opening_size:continue
        prior=Fraction(comb(basics,b)*comb(source_copies,q)*comb(disposable,f)*
                       comb(other,p),den)/valid
        for j,rest in enumerate((basics-b,source_copies-q,disposable-f,other-p)):
            if rest<=0:continue
            h=[b-1,q,f,p]
            h[j]+=1
            bb,qq,ff,pp=h
            if not qq:continue
            mass=prior*Fraction(rest,deck_size-opening_size)
            held+=mass
            can_discard=ff+qq-1+max(0,bb-reserved_extra_basics)
            payable+=mass*(can_discard>=required_discards)
    assert 0<=payable<=held<=1
    if reserved_extra_basics==0 or reserved_extra_basics>=opening_size:
        prior=basic_valid_discard_quota(deck_size=deck_size,basics=basics,
                source_copies=source_copies,disposable=disposable,
                opening_size=opening_size,prize_count=prize_count,
                required_discards=required_discards)
        assert held==prior.source_held
        assert payable==(prior.allow_extra_basics if reserved_extra_basics==0
                         else prior.allow_spare_source_copies)
    return BenchReserveGate(valid,held,payable,payable/held,required_discards,
                             reserved_extra_basics)
