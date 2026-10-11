"""Exact payment gating for Item discard quotas under Basic-valid opening.

Examples from supplied card corpus: Quick Ball 1-other-card, Ultra Ball
2-other-card, Secret Box ACE SPEC 3-other-card requirement. Card search
outputs and future costs are outside this gate-only model.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from basic_valid_item_payment_geometry import (
    _choose,_avoids_after_setup,basic_valid_item_payment,
)


@dataclass(frozen=True)
class QuotaPayability:
    basic_valid_opening: Fraction
    source_held: Fraction
    strict_disposables: Fraction
    allow_spare_source_copies: Fraction
    allow_extra_basics: Fraction
    conditional_strict: Fraction
    conditional_spare_source: Fraction
    conditional_extra_basics: Fraction
    discard_count: int
    source_count: int


def basic_valid_discard_quota(
    *,deck_size:int=60, basics:int=12, source_copies:int=4,
    disposable:int=8, opening_size:int=7, prize_count:int=6,
    required_discards:int=2,
)->QuotaPayability:
    """Full-hand Item discard cost conditioned on one starting Active Basic.

    The source itself is consumed separately; required_discards counts
    *other* cards in the hand. Payment can use F, spare copies of the source,
    and optionally Basics left after the obligatory Active. Protected cards
    are never considered disposable. Prices of these cards are not modeled.
    """
    vals=(deck_size,basics,source_copies,disposable,opening_size,
          prize_count,required_discards)
    if any(type(x) is not int for x in vals):
        raise TypeError('all counts must be integers')
    if (basics<1 or source_copies<1 or disposable<0 or required_discards<0
       or deck_size<basics+source_copies+disposable
       or not 0<opening_size<deck_size-prize_count):
        raise ValueError('infeasible composition or starting setup')
    protected=deck_size-basics-source_copies-disposable
    source_held=1-_avoids_after_setup(deck_size=deck_size,basics=basics,
                                excluded=source_copies,opening_size=opening_size)
    valid=Fraction(_choose(deck_size,opening_size)-_choose(deck_size-basics,opening_size),
                   _choose(deck_size,opening_size))
    den=comb(deck_size,opening_size)
    sums=[Fraction(),Fraction(),Fraction()]
    for b,q,f,p in product(*(range(min(n,opening_size)+1) for n in
                             (basics,source_copies,disposable,protected))):
        if not b or b+q+f+p!=opening_size:continue
        p0=Fraction(comb(basics,b)*comb(source_copies,q)*comb(disposable,f)*
                    comb(protected,p),den)/valid
        for j,remain in enumerate((basics-b,source_copies-q,disposable-f,protected-p)):
            if remain<=0:continue
            hand=[b-1,q,f,p]
            hand[j]+=1
            bb,qq,ff,pp=hand
            mass=p0*Fraction(remain,deck_size-opening_size)
            if qq>=1:
                sums[0]+=mass*(ff>=required_discards)
                sums[1]+=mass*(ff+qq-1>=required_discards)
                sums[2]+=mass*(ff+qq-1+bb>=required_discards)
    a,b,c=sums
    assert 0<=a<=b<=c<=source_held<=1
    if required_discards==1:
        old=basic_valid_item_payment(deck_size=deck_size,basics=basics,
              item=source_copies,disposable=disposable,opening_size=opening_size,
              prize_count=prize_count)
        assert (source_held,a,b,c)==(old.item_held,old.item_plus_disposable,
               old.item_plus_disposable_or_spare_item,old.item_with_basic_fallback)
    return QuotaPayability(valid,source_held,a,b,c,a/source_held,
                            b/source_held,c/source_held,required_discards,source_copies)
