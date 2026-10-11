"""Independent physical test for Basic-valid discard-resource gate geometry."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from basic_valid_item_payment_geometry import basic_valid_item_payment


def brute_physical(N,B,Q,F,h,p):
    all_cards=tuple(range(N))
    classes={c:(0 if c<B else 1 if c<B+Q else 2 if c<B+Q+F else 3)
             for c in all_cards}
    open_valid=[x for x in combinations(all_cards,h)
                if any(classes[y]==0 for y in x)]
    count=0
    categories=defaultdict(int)
    for opened in open_valid:
        a=next(c for c in opened if classes[c]==0)
        pool=tuple(c for c in all_cards if c not in opened)
        for prize in combinations(pool,p):
            for draw in pool:
                if draw in prize:continue
                final=tuple(c for c in opened if c!=a)+(draw,)
                q=sum(classes[c]==1 for c in final)
                f=sum(classes[c]==2 for c in final)
                b=sum(classes[c]==0 for c in final)
                categories['held']+=int(q>=1)
                categories['strict']+=int(q>=1 and f>=1)
                categories['spare']+=int(q>=1 and (f>=1 or q>=2))
                categories['basic']+=int(q>=1 and (f>=1 or q>=2 or b>=1))
                count+=1
    assert count==len(open_valid)*comb(N-h,p)*(N-h-p)
    return tuple(Fraction(categories[k],count) for k in ('held','strict','spare','basic'))


def exact_checks():
    count=0
    for N in (8,9,10,11):
        for B in (1,2,3):
            for Q in (1,2):
                for F in range(N-B-Q+1):
                    for opening,p in ((3,1),(3,2)):
                        if N-opening-p<=0:continue
                        observed=brute_physical(N,B,Q,F,opening,p)
                        r=basic_valid_item_payment(deck_size=N,basics=B,item=Q,
                                                  disposable=F,opening_size=opening,
                                                  prize_count=p)
                        predicted=(r.item_held,r.item_plus_disposable,
                                   r.item_plus_disposable_or_spare_item,
                                   r.item_with_basic_fallback)
                        assert predicted==observed,(N,B,Q,F,opening,p,predicted,observed)
                        count+=1
    return count


def witness():
    vals={f:basic_valid_item_payment(disposable=f) for f in (0,2,4,8,12,20,28)}
    held=vals[8].item_held
    assert round(float(held),12)==0.427388244289
    assert all(v.item_held==held for v in vals.values())
    assert round(float(vals[8].item_plus_disposable),12)==0.276192223055
    assert round(float(vals[8].item_plus_disposable_or_spare_item),12)==0.306934596410
    assert round(float(vals[8].item_with_basic_fallback),12)==0.387883633380
    assert vals[0].item_plus_disposable==0
    assert round(float(vals[0].item_plus_disposable_or_spare_item),12)==0.073890546701
    assert round(float(vals[0].item_with_basic_fallback),12)==0.284218387010
    assert round(float(vals[28].item_plus_disposable),12)==0.423912352445
    previous=Fraction()
    for F in range(45):
        value=basic_valid_item_payment(disposable=F).item_plus_disposable
        assert value>=previous
        previous=value
    print('Q physically held probability for B12 Q4:',float(held))
    print('F8 strict/discard spare Q/extra Basic payment gates:',
          *(float(v) for v in (vals[8].item_plus_disposable,
                                vals[8].item_plus_disposable_or_spare_item,
                                vals[8].item_with_basic_fallback)))
    print('F0: spare-Q gate',float(vals[0].item_plus_disposable_or_spare_item),
          'Basic fallback',float(vals[0].item_with_basic_fallback))
    print('F28 strict gate',float(vals[28].item_plus_disposable))


if __name__=='__main__':
    print('Independent labeled opening-Prize-draw models:',exact_checks())
    witness()
