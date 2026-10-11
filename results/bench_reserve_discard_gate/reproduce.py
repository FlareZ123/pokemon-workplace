"""Independent physical Bench-reserved discard quota enumerator."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from bench_reserve_discard_gate import bench_reserve_discard_gate


def brute(*,N,B,Q,F,h,p,m,reserve):
    cards=tuple(range(N))
    cls={c:0 if c<B else 1 if c<B+Q else 2 if c<B+Q+F else 3 for c in cards}
    starts=[t for t in combinations(cards,h) if any(cls[c]==0 for c in t)]
    events=len(starts)*comb(N-h,p)*(N-h-p)
    source=payable=0
    for initial in starts:
        active=next(c for c in initial if cls[c]==0)
        remaining=tuple(c for c in cards if c not in initial)
        for prizes in combinations(remaining,p):
            for draw in remaining:
                if draw in prizes:continue
                hand=tuple(c for c in initial if c!=active)+(draw,)
                b=sum(cls[c]==0 for c in hand)
                q=sum(cls[c]==1 for c in hand)
                f=sum(cls[c]==2 for c in hand)
                source+=int(q>0)
                payable+=int(q>0 and f+q-1+max(0,b-reserve)>=m)
    return Fraction(source,events),Fraction(payable,events)


def check_small():
    tests=0
    for N in (8,9,10):
        for B in (1,2,3):
            for Q in (1,2):
                for F in range(N-B-Q+1):
                    for m in (1,2,3):
                        for reserve in (0,1,2,3):
                            p=1+((N+B+Q+F+m+reserve)%2)
                            result=bench_reserve_discard_gate(deck_size=N,basics=B,
                                source_copies=Q,disposable=F,opening_size=3,
                                prize_count=p,required_discards=m,
                                reserved_extra_basics=reserve)
                            held,payable=brute(N=N,B=B,Q=Q,F=F,h=3,p=p,m=m,
                                               reserve=reserve)
                            assert (result.source_held,result.payable_with_reserved_basics)==(held,payable),(
                                N,B,Q,F,p,m,reserve)
                            tests+=1
    return tests


def witness():
    cases=(('Quick Ball',4,1,(38.788363,33.982272,31.479100,30.693460)),
           ('Ultra Ball',4,2,(26.718521,17.081308,13.516184,12.786962)),
           ('Secret Box',1,3,(2.695779,0.885039,0.494577,0.453336)))
    for label,q,m,expected in cases:
        outputs=[]
        for reserve in (0,1,2,7):
            a=bench_reserve_discard_gate(source_copies=q,required_discards=m,
                                        reserved_extra_basics=reserve)
            outputs.append(round(float(100*a.payable_with_reserved_basics),6))
        assert tuple(outputs)==expected,(label,outputs,expected)
        print(label,'reserve 0/1/2/7 probabilities (percent)',outputs)
    for q,m,_ in ((4,1,()),(4,2,()),(1,3,())):
        prior=Fraction(1)
        for reserve in range(8):
            value=bench_reserve_discard_gate(source_copies=q,required_discards=m,
                           reserved_extra_basics=reserve).payable_with_reserved_basics
            assert value<=prior
            prior=value
    print('All reserve thresholds exactly monotone nonincreasing')


if __name__=='__main__':
    print('Independent physical reserved-Basic payability cases:',check_small())
    witness()
