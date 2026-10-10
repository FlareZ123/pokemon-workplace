"""Exact search for Item indispensability with *exactly four* of six
non-TM Tool/Artazon cards Prized, excluding Jirachi-start openings.

Enumerates 15 choose-four key-Prize layouts, all two-card nonkey Prize
pairs, physically weighted accepted opening seven, first draw and
non-Jirachi starting Active. The source Aichi first-turn-core solver tests
Secret Box output mask 15 against mask 14 and Grand Tree baseline.

This is a counterexample search with an exact incidence if any is found,
not a claim about cases involving Jirachi or fewer/more key Prize cards.
"""
from collections import defaultdict
from fractions import Fraction
from itertools import combinations_with_replacement
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from five_prize_item_frontier import (
    FULL,TOOL,STADIUM,ACE,JIR,
    ACTIVE_MULTIPLIER,composition,starters,mkstate,
    HAND_INDEX,_core_possible,
)

NONKEY=tuple(range(13))
NCHOOSE=comb(54,2)

def baseline(s):
    hand,deck,*flags=s
    hand=list(hand)
    hand[HAND_INDEX["other"]]+=hand[HAND_INDEX["secret_box"]]
    hand[HAND_INDEX["secret_box"]]=0
    return (tuple(hand),deck,*flags)

def scan():
    group_results=[]
    total=0
    for num_tools in (2,3,4):
        num_art=4-num_tools
        assert 0<=num_art<=2
        fixed=(0,)*13+(num_tools,num_art)
        remaining=tuple(n-p for n,p in zip(FULL,fixed))
        assert sum(remaining)==56
        mult=comb(4,num_tools)*comb(2,num_art)
        group_gain=0
        pair_with_gain=0
        group_checked=0
        witnesses=[]
        for x,y in combinations_with_replacement(NONKEY,2):
            pairways=(comb(remaining[x],2) if x==y
                      else remaining[x]*remaining[y])
            if pairways==0:
                continue
            after=list(remaining)
            after[x]-=1
            after[y]-=1
            pool=tuple(after)
            assert sum(pool)==54
            gain=0
            checked=0
            for opening in composition(7,pool):
                if opening[JIR]:
                    continue
                active_variants=starters(opening)
                if not active_variants:
                    continue
                hand_weight=1
                for n,qty in zip(pool,opening):
                    hand_weight*=comb(n,qty)
                for draw,n in enumerate(pool):
                    draws=n-opening[draw]
                    if draws<=0 or not (opening[ACE] or draw==ACE):
                        continue
                    for active,active_weight in active_variants:
                        w=pairways*hand_weight*draws*active_weight
                        s=mkstate(pool,opening,draw,active)
                        checked+=w
                        if _core_possible(s,14) or not _core_possible(s,15):
                            continue
                        if _core_possible(baseline(s),15):
                            continue
                        gain+=w
                        if len(witnesses)<3:
                            witnesses.append((x,y,opening,draw,active))
                if _core_possible.cache_info().currsize>260_000:
                    _core_possible.cache_clear()
            group_gain+=gain
            group_checked+=checked
            pair_with_gain+=int(gain>0)
        total+=mult*group_gain
        group_results.append((num_tools,num_art,mult,
                              group_gain,pair_with_gain,group_checked,
                              witnesses))
        print("fixed_key_Prizes",num_tools,"Tools",num_art,
              "Artazon","physical_mult",mult,
              "positive_pair_groups",pair_with_gain,
              "weighted_incremental",group_gain,
              "witnesses",witnesses,flush=True)

    A=1-Fraction(comb(46,7),comb(60,7))
    p=Fraction(total,1)/(comb(60,6)*comb(54,7)*47*ACTIVE_MULTIPLIER*A)
    print("Exactly-four-key-Prized, no-Jirachi Item necessity:",p,float(p))
    print("Total weighted qualifying combinations:",total)
    print("Group classes:",group_results)
    print("Exact four-key-Prize search completed.")


if __name__=="__main__":
    scan()
