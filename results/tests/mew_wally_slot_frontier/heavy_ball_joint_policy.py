"""Exact physical Prize-state and one-target Heavy Ball launch policy."""
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
from results.tests.mew_wally_tapu_variant.reproduce import exact as legacy_exact
from results.tests.mew_wally_slot_frontier.heavy_ball_prize_bridge import EXPECTED as LELE_RESCUE,verify_card

# Mew, Genesect, VMAX, Wally, DCE, VIP, Quick, Ultra, Lele, Heavy, other
EXPECTED={
  1:(Fraction(636040115150563,8681622274224900),Fraction(1171829613302,930173815095525),Fraction(4496884310383,3592395423817200)),
  2:(Fraction(207472683238253,2367715165697700),Fraction(13172246169671,10417946729069880),Fraction(144290444506111,104179467290698800))
}
LABELS=("baseline","heavy_lele","heavy_genesect")

def pool(w):
    x=(4,4,3,w,4,3,4,4,1,1,32-w)
    assert sum(x)==60
    return x

def route(h,p,d):
    if not h[4] or not d[2]:return None
    balls=h[6]+h[7]
    if h[3]:
        if h[1] or (d[1] and (h[5] or balls)):return "baseline"
    elif d[3]:
        use_lele_ball=int(not bool(h[8]))
        use_gene_ball=int(not bool(h[1] or h[5]))
        if (h[8] or d[8]) and balls>=use_lele_ball+use_gene_ball and (h[1] or d[1]):
            return "baseline"
    if not h[9]:return None
    if not h[3] and d[3] and not h[8] and p[8] and (
        h[1] or (d[1] and (h[5] or balls))
    ):return "heavy_lele"
    if not h[1] and p[1] and (
        h[3] or (d[3] and (h[8] or (d[8] and balls)))
    ):return "heavy_genesect"
    return None

def exact(pool,hand,prizes):
    n=sum(pool)
    den=comb(n,hand)*(n-hand)*comb(n-hand-1,prizes)
    hits=Counter()
    for opening,ways in opening_counts(pool,hand):
        if not opening[0]:continue
        for drawn,copies in enumerate(pool):
            available=copies-opening[drawn]
            if not available:continue
            h=list(opening);h[drawn]+=1
            if not h[4]:continue
            unseen=[a-b for a,b in zip(pool,h)]
            G,V,W,L=[unseen[i] for i in (1,2,3,8)]
            O=sum(unseen[i] for i in (0,4,5,6,7,9,10))
            for gp in range(min(G,prizes)+1):
                for vp in range(min(V,prizes-gp)+1):
                    if vp==V:continue
                    for wp in range(min(W,prizes-gp-vp)+1):
                        for lp in range(min(L,prizes-gp-vp-wp)+1):
                            op=prizes-gp-vp-wp-lp
                            if op>O:continue
                            p=[0]*11;p[1]=gp;p[2]=vp;p[3]=wp;p[8]=lp
                            d=unseen.copy()
                            for i in (1,2,3,8):d[i]-=p[i]
                            label=route(h,p,d)
                            if label:
                                mass=comb(G,gp)*comb(V,vp)*comb(W,wp)*comb(L,lp)*comb(O,op)
                                hits[label]+=ways*available*mass
    return {k:Fraction(v,den) for k,v in hits.items()}

def oracle(pool,hand,prizes):
    cards=tuple(k for k,copies in enumerate(pool) for _ in range(copies))
    n=len(cards);den=comb(n,hand)*comb(n-hand,prizes)*(n-hand-prizes)
    hits=Counter()
    for choice in combinations(range(n),hand):
        opening=set(choice)
        if not any(cards[i]==0 for i in opening):continue
        rest=set(range(n))-opening
        for ps in combinations(sorted(rest),prizes):
            prized=set(ps)
            p=Counter(cards[i] for i in prized)
            for draw in rest-prized:
                h=Counter(cards[i] for i in opening|{draw})
                d=Counter(cards[i] for i in rest-prized-{draw})
                label=route(h,p,d)
                if label:hits[label]+=1
    return {k:Fraction(v,den) for k,v in hits.items()}

def main():
    verify_card()
    toys=(((1,1,1,2,1,0,1,0,1,1,2),3,2),
          ((2,1,1,1,1,1,1,0,1,1,2),3,2),
          ((1,2,1,2,1,1,1,0,1,1,2),4,2))
    for pop,h,p in toys:
        assert exact(pop,h,p)==oracle(pop,h,p)
        print("Joint physical oracle PASSED",sum(pop))
    for w in (1,2):
        observed=exact(pool(w),7,6)
        assert tuple(observed.get(k,Fraction(0)) for k in LABELS)==EXPECTED[w]
        src=pool(w)
        original=sum(legacy_exact((*src[:9],src[9]+src[10]),7,6).values(),Fraction(0))
        assert original==observed["baseline"]
        assert observed["heavy_lele"]==LELE_RESCUE[w]
        for kind in LABELS:print(w,kind,f"{float(observed[kind]):.12%}",observed[kind])
        union=sum(observed.values(),Fraction(0))
        print("Exact joint launch union",w,f"{float(union):.12%}",union)
    print("Heavy Ball can recover Lele or Genesect once, with disjoint policy accounting")

if __name__=="__main__":main()
