"""Independently enumerate full physical first-turn Item costs 0..3."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from basic_valid_discard_quota import basic_valid_discard_quota


def brute_quota(*,N,B,Q,F,h,p,m):
    ids=tuple(range(N))
    c={i:0 if i<B else 1 if i<B+Q else 2 if i<B+Q+F else 3 for i in ids}
    opens=[o for o in combinations(ids,h) if any(c[z]==0 for z in o)]
    total=len(opens)*comb(N-h,p)*(N-h-p)
    stats=defaultdict(int)
    for o in opens:
        active=next(x for x in o if c[x]==0)
        unseen=tuple(i for i in ids if i not in o)
        for prize in combinations(unseen,p):
            for draw in unseen:
                if draw in prize:continue
                hand=tuple(x for x in o if x!=active)+(draw,)
                b=sum(c[x]==0 for x in hand)
                q=sum(c[x]==1 for x in hand)
                f=sum(c[x]==2 for x in hand)
                stats['held']+=int(q>=1)
                stats['strict']+=int(q>=1 and f>=m)
                stats['spare']+=int(q>=1 and f+q-1>=m)
                stats['basic']+=int(q>=1 and f+q-1+b>=m)
    return tuple(Fraction(stats[s],total) for s in ('held','strict','spare','basic'))


def tests():
    count=0
    for N in (8,9,10):
        for B in (1,2,3):
            for Q in (1,2):
                for F in range(N-B-Q+1):
                    for m in range(4):
                        for p in (1,2):
                            if N-3-p<=0:continue
                            r=basic_valid_discard_quota(deck_size=N,basics=B,
                                source_copies=Q,disposable=F,opening_size=3,
                                prize_count=p,required_discards=m)
                            brute=brute_quota(N=N,B=B,Q=Q,F=F,h=3,p=p,m=m)
                            assert (r.source_held,r.strict_disposables,
                                    r.allow_spare_source_copies,r.allow_extra_basics)==brute,(
                                        N,B,Q,F,p,m,brute)
                            count+=1
    return count


def witness():
    modes=(('Quick Ball',4,1),('Ultra Ball',4,2),('Secret Box',1,3))
    saved=[]
    for name,cost_source,need in modes:
        r=basic_valid_discard_quota(source_copies=cost_source,
                                      required_discards=need,disposable=8)
        saved.append(r)
        print(name,'held/strict/spare/basic/strict-conditional (percent)',
              *(f'{float(100*x):.6f}' for x in
                (r.source_held,r.strict_disposables,r.allow_spare_source_copies,
                 r.allow_extra_basics,r.conditional_strict)))
    quick,ultra,secret=saved
    assert round(float(quick.strict_disposables*100),6)==27.619222
    assert round(float(ultra.strict_disposables*100),6)==9.453070
    assert round(float(secret.strict_disposables*100),6)==0.453336
    assert round(float(secret.conditional_strict*100),6)==3.581060
    assert round(float(secret.source_held*100),6)==12.659263
    assert quick.source_held==ultra.source_held
    assert quick.strict_disposables>ultra.strict_disposables>secret.strict_disposables
    for name,Q,need in modes:
        prev=Fraction()
        for F in range(60-12-Q+1):
            r=basic_valid_discard_quota(source_copies=Q,required_discards=need,disposable=F)
            assert r.strict_disposables>=prev
            prev=r.strict_disposables
    print('Strict payment monotonicity checked across all feasible F for three source designs')


if __name__=='__main__':
    print('Independent physical quota enumerations:',tests())
    witness()
