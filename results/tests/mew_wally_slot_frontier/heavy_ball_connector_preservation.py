"""Prize-aware option to preserve one paid Ball search by using Heavy Ball.

The endpoint is an available alternative action, not an additional success:
Hisuian Heavy Ball recovers Prized Genesect V while a Quick/Ultra Ball
that would have fetched Genesect V from deck can stay unspent.
"""
from __future__ import annotations
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from results.tests.mew_wally_first_attack.reproduce import opening_counts
from results.tests.mew_wally_slot_frontier.heavy_ball_joint_policy import pool
from results.tests.mew_wally_slot_frontier.heavy_ball_prize_bridge import verify_card

EXPECTED={
  1:Fraction(1070405768252,1302243341133735),
  2:Fraction(737040664592,723468522852075),
}

def option(h,p,d):
    balls=h[6]+h[7]
    if not (
        h[4] and d[2] and h[9] and p[1]
        and not h[1] and not h[5] and d[1] and balls
    ):
        return False
    if h[3]:return True
    return bool(d[3] and (h[8] or (d[8] and balls>=2)))

def exact(pool,hand,prizes):
    n=sum(pool)
    den=comb(n,hand)*(n-hand)*comb(n-hand-1,prizes)
    hits=0
    for opening,ways in opening_counts(pool,hand):
        if not opening[0]:continue
        for drawn,copies in enumerate(pool):
            available=copies-opening[drawn]
            if not available:continue
            h=list(opening);h[drawn]+=1
            if not h[4] or not h[9]:continue
            unseen=[a-b for a,b in zip(pool,h)]
            G,V,W,L=[unseen[i] for i in (1,2,3,8)]
            O=sum(unseen[i] for i in (0,4,5,6,7,9,10))
            for gp in range(1,min(G,prizes)+1):
                for vp in range(min(V,prizes-gp)+1):
                    if vp==V:continue
                    for wp in range(min(W,prizes-gp-vp)+1):
                        for lp in range(min(L,prizes-gp-vp-wp)+1):
                            op=prizes-gp-vp-wp-lp
                            if op>O:continue
                            p=[0]*11;p[1]=gp;p[2]=vp;p[3]=wp;p[8]=lp
                            d=unseen.copy()
                            for i in (1,2,3,8):d[i]-=p[i]
                            if option(h,p,d):
                                hits+=ways*available*comb(G,gp)*comb(V,vp)*comb(W,wp)*comb(L,lp)*comb(O,op)
    return Fraction(hits,den)

def oracle(pool,hand,prizes):
    physical=tuple(k for k,copies in enumerate(pool) for _ in range(copies))
    n=len(physical);den=comb(n,hand)*comb(n-hand,prizes)*(n-hand-prizes)
    hits=0
    for chosen in combinations(range(n),hand):
        opening=set(chosen)
        if not any(physical[i]==0 for i in opening):continue
        left=set(range(n))-opening
        for selected in combinations(sorted(left),prizes):
            prized=set(selected);p=Counter(physical[i] for i in prized)
            for drawn in left-prized:
                h=Counter(physical[i] for i in opening|{drawn})
                d=Counter(physical[i] for i in left-prized-{drawn})
                if option(h,p,d):hits+=1
    return Fraction(hits,den)

def main():
    verify_card()
    for fixture,hand,prizes in (
        ((1,2,1,2,1,0,2,0,1,1,1),4,2),
        ((2,2,1,1,1,0,2,0,1,1,2),4,2),
        ((1,2,1,2,1,0,2,0,1,1,2),4,2),
    ):
        a=exact(fixture,hand,prizes)
        b=oracle(fixture,hand,prizes)
        assert a==b,(fixture,a,b)
        print(f"Physical Ball-preservation oracle PASSED N={sum(fixture)}: {a}")
    for w,expected in EXPECTED.items():
        rate=exact(pool(w),7,6)
        assert rate==expected,(w,rate,expected)
        print(f"Wally={w} paid Ball alternative: {float(rate):.12%}; {rate}")
    print("OPTIONALITY ONLY: this probability is included in baseline launch success.")

if __name__=="__main__":main()
