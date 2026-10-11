"""Exact first-turn item presence versus state-dependent discard payment.

Setup uses N cards, B starting Basics, Q copies of an Item with one extra
card-discard requirement, F acceptable non-Item discard cards, P protected.
Initial h cards must contain a Basic, one Basic becomes Active, p Prizes are
placed, one natural card is drawn, then the Item-payability gate is assessed.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb


@dataclass(frozen=True)
class ItemPaymentGeometry:
    basic_valid_opening: Fraction
    item_held: Fraction
    item_plus_disposable: Fraction
    item_plus_disposable_or_spare_item: Fraction
    item_with_basic_fallback: Fraction
    displayed_conditionals: tuple[Fraction,Fraction,Fraction]
    enumerated_hands: int


def _choose(n:int,k:int)->int:
    return comb(n,k) if 0<=k<=n else 0


def _avoids_after_setup(*,deck_size:int,basics:int,excluded:int,
                        opening_size:int) -> Fraction:
    """Probability no excluded-category card in hand after setup | Basic-valid.

    Excluded cards are disjoint from Basics. One Basic is removed to Active.
    Random Prize placement marginalizes; following natural card draw samples
    from cards not present in the initial opening.
    """
    denominator=_choose(deck_size,opening_size)-_choose(deck_size-basics,opening_size)
    numerator=_choose(deck_size-excluded,opening_size)-_choose(
        deck_size-excluded-basics,opening_size)
    return Fraction(numerator,denominator)*Fraction(
        deck_size-opening_size-excluded,deck_size-opening_size)


def basic_valid_item_payment(
    *,deck_size:int=60,basics:int=12,item:int=4,
    disposable:int=8,opening_size:int=7,prize_count:int=6,
)->ItemPaymentGeometry:
    """Three discard policies: F only; F or spare Q; F/spare Q/extra B.

    All three preserve targets/other protected cards. Extra Basic fallback
    assumes any Basic left in hand after Active is discardable at zero future
    cost, an explicit hypothetical DCI choice rather than a recommendation.
    """
    fields=(deck_size,basics,item,disposable,opening_size,prize_count)
    if any(type(x) is not int for x in fields):
        raise TypeError('all category and setup counts must be integers')
    if (basics<1 or item<1 or disposable<0 or basics+item+disposable>deck_size
            or not 0<opening_size<deck_size-prize_count
            or deck_size-opening_size<=0):
        raise ValueError('invalid deck/setup class counts')
    protected=deck_size-basics-item-disposable
    valid=Fraction(_choose(deck_size,opening_size)-_choose(deck_size-basics,opening_size),
                   _choose(deck_size,opening_size))
    absent_Q=_avoids_after_setup(deck_size=deck_size,basics=basics,
                                  excluded=item,opening_size=opening_size)
    absent_F=_avoids_after_setup(deck_size=deck_size,basics=basics,
                                  excluded=disposable,opening_size=opening_size)
    absent_QF=_avoids_after_setup(deck_size=deck_size,basics=basics,
                                  excluded=item+disposable,opening_size=opening_size)
    item_held=1-absent_Q
    strict=1-absent_Q-absent_F+absent_QF
    # Independent multivariate enumeration for spare-Q and extra-B gates.
    den=_choose(deck_size,opening_size)
    masses:dict[tuple[int,...],Fraction]={}
    for b,q,f,p in product(*(range(min(n,opening_size)+1)
                               for n in (basics,item,disposable,protected))):
        if b<1 or b+q+f+p!=opening_size:continue
        initial=Fraction(_choose(basics,b)*_choose(item,q)*_choose(disposable,f)*
                         _choose(protected,p),den)/valid
        for draw_class,n_rem in enumerate((basics-b,item-q,disposable-f,protected-p)):
            if n_rem<=0:continue
            counts=[b-1,q,f,p]
            counts[draw_class]+=1
            h=tuple(counts)
            masses[h]=masses.get(h,Fraction())+initial*Fraction(n_rem,deck_size-opening_size)
    assert sum(masses.values(),Fraction())==1
    strict_brute=sum((p for (b,q,f,r),p in masses.items() if q>=1 and f>=1),Fraction())
    held_brute=sum((p for (b,q,f,r),p in masses.items() if q>=1),Fraction())
    assert strict==strict_brute and item_held==held_brute
    spare=sum((p for (b,q,f,r),p in masses.items() if q>=1 and (f>=1 or q>=2)),Fraction())
    basic=sum((p for (b,q,f,r),p in masses.items()
               if q>=1 and (f>=1 or q>=2 or b>=1)),Fraction())
    assert 0<=strict<=spare<=basic<=item_held<=1
    return ItemPaymentGeometry(valid,item_held,strict,spare,basic,
        (strict/item_held,spare/item_held,basic/item_held),len(masses))
