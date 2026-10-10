"""Complete exact five-Prize Item frontier, including Jirachi Stellar Wish.

Extends the non-Jirachi exact 5/6 Tool+Artazon Prize census by enumerating
Jirachi-start openings, the first draw, and hypergeometric next-five
presence masks for G&H, Tag Call, TM, Artazon and the ACE SPEC.

The two Prize families remain disjoint from each other and the all-six
alternative-Tool/Artazon-Prized event. State transitions use the original
unmodified Aichi compressed planner for both Box output masks and baseline.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from five_prize_item_frontier import (
    FULL,TOOL,STADIUM,GNH,TAG,TM,JET,ACE,BUN,FAN,JIR,BASIC,
    SUPPORT,TAG_OTHER,SPECIAL_OTHER,FILLER,
    HAND,DECK,HAND_INDEX,DECK_INDEX,
    ACTIVE_MULTIPLIER,composition,starters,mkstate,
)
from aichi_vileplume_secret_box import _core_possible

STELLAR=(GNH,TAG,TM,STADIUM,ACE)
TOPWAYS=comb(46,5)

@lru_cache(maxsize=None)
def top_masks(stocks):
    other=46-sum(stocks)
    assert other>=0
    out=[]
    for mask in range(32):
        ways=0
        subset=mask
        while True:
            allowed=other+sum(
                stocks[i] for i in range(5) if subset&(1<<i)
            )
            if allowed>=5:
                ways+=(-1 if (mask.bit_count()-subset.bit_count())%2 else 1) \
                      *comb(allowed,5)
            if subset==0:
                break
            subset=(subset-1)&mask
        assert ways>=0
        if ways:
            out.append((mask,ways))
    assert sum(x for _,x in out)==TOPWAYS
    return tuple(out)

def convert_baseline(state):
    hand,deck,*flags=state
    hand=list(hand)
    deck=list(deck)
    held=hand[HAND_INDEX["secret_box"]]
    hand[HAND_INDEX["other"]]+=held
    hand[HAND_INDEX["secret_box"]]=0
    deck[DECK_INDEX["secret_box"]]=0
    return tuple(hand),tuple(deck),*flags

def pick(state,category):
    hand,deck,*flags=state
    hand=list(hand)
    deck=list(deck)
    h=HAND_INDEX[HAND[category]]
    d=DECK_INDEX[DECK[category]]
    assert deck[d]>0
    hand[h]+=1
    deck[d]-=1
    return tuple(hand),tuple(deck),*flags

def possible(state,mask):
    return _core_possible(state,mask)

def outcomes_for_stellar(pool,opening,draw,topmask):
    assert opening[JIR]>0
    s=mkstate(pool,opening,draw,"basic")  # Jirachi Active removes one "other".
    held=bool(s[0][HAND_INDEX["secret_box"]])
    visible_box=bool(topmask & 16)
    if not (held or visible_box):
        return (False,False,False)

    picks=(None,)+tuple(
        cat for bit,cat in enumerate(STELLAR)
        if topmask&(1<<bit)
    )

    def exists(source,mask):
        initial=s if source else convert_baseline(s)
        for category in picks:
            if category==ACE and not source:
                continue
            state=initial if category is None else pick(initial,category)
            if possible(state,mask):
                return True
        return False

    no_item=exists(True,14)
    if no_item:
        return (False,False,False)
    full=exists(True,15)
    if not full:
        return (False,False,False)
    baseline=exists(False,15)
    return (True,not baseline,held)

def count_family(fixed,missing):
    after5=tuple(x-y for x,y in zip(FULL,fixed))
    assert sum(after5)==55 and after5[missing]==1
    totals=defaultdict(int)
    examples={}
    subcases=0
    for sixth,choices in enumerate(after5):
        if not choices or sixth==missing:
            continue
        pool=list(after5)
        pool[sixth]-=1
        pool=tuple(pool)
        assert sum(pool)==54 and pool[missing]==1
        for opening in composition(7,pool):
            if not opening[JIR]:
                active_options=starters(opening)
            else:
                active_options=(("jirachi",ACTIVE_MULTIPLIER),)
            if not active_options:
                continue
            hand_weight=1
            for copies,n in zip(opening,pool):
                hand_weight*=comb(n,copies)
            for draw,n in enumerate(pool):
                available=n-opening[draw]
                if available<=0:
                    continue
                after=tuple(n-opening[i]-int(draw==i)
                            for i,n in enumerate(pool))
                assert sum(after)==46
                for active,act_weight in active_options:
                    if active=="jirachi":
                        masks=top_masks(tuple(after[i] for i in STELLAR))
                        for mask,top_ways in masks:
                            full_only,incremental,held=outcomes_for_stellar(
                                pool,opening,draw,mask
                            )
                            if not full_only:
                                continue
                            w=choices*hand_weight*available*act_weight*top_ways
                            totals["full_only"]+=w
                            if incremental:
                                bucket="jirachi_box_held" if held \
                                    else "jirachi_stellar_only"
                                totals["incremental"]+=w
                                totals[bucket]+=w
                                examples.setdefault(bucket,
                                                    (sixth,opening,draw,mask))
                    else:
                        if not (opening[ACE] or draw==ACE):
                            continue
                        raw=mkstate(pool,opening,draw,active)
                        if possible(raw,14) or not possible(raw,15):
                            continue
                        w=choices*hand_weight*available*act_weight*TOPWAYS
                        totals["full_only"]+=w
                        if not possible(convert_baseline(raw),15):
                            totals["incremental"]+=w
                            totals["non_jirachi_box_held"]+=w
                            examples.setdefault("non_jirachi_box_held",
                                                (sixth,opening,draw,active))
                subcases+=1
            if _core_possible.cache_info().currsize>320_000:
                _core_possible.cache_clear()
        print("sixth",sixth,"physical_choices",choices,
              "incremental_weight",totals["incremental"],flush=True)

    assert totals["full_only"]>=totals["incremental"]>0
    return totals,examples,subcases

def main():
    a,ex_a,n_a=count_family((0,)*13+(4,1),STADIUM)
    b,ex_b,n_b=count_family((0,)*13+(3,2),TOOL)
    weighted=defaultdict(int)
    for key,val in a.items():
        weighted[key]+=2*val
    for key,val in b.items():
        weighted[key]+=4*val
    accepted=1-Fraction(comb(46,7),comb(60,7))
    denominator=comb(60,6)*comb(54,7)*47*ACTIVE_MULTIPLIER*TOPWAYS*accepted
    exact={key:Fraction(val,1)/denominator
           for key,val in weighted.items()}
    assert exact["non_jirachi_box_held"] == \
        Fraction(506271,2136694380620800)
    assert exact["incremental"]>=exact["non_jirachi_box_held"]
    assert exact["incremental"]<=exact["full_only"]
    assert (exact["non_jirachi_box_held"]+
            exact.get("jirachi_box_held",0)+
            exact.get("jirachi_stellar_only",0))==exact["incremental"]
    all_six=Fraction(35905391051,11715529476053936332800)
    combined=all_six+exact["incremental"]
    print("Grouped opening/draw cases:",n_a+n_b)
    print("Representative nonzero Jirachi cases:",ex_a,ex_b)
    for key,val in sorted(exact.items()):
        print(key,val,float(val))
    print("Combined disjoint global Item-loss lower bound",
          combined,float(combined))
    print("Complete exact five-Prize Item frontier passed.")


if __name__=="__main__":
    main()
