"""Independent labeled-card physical frontier and exact rational threshold checks."""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from physical_quick_ball_cost_frontier import quick_ball_cost_frontier
from physical_quick_ball_search_option import physical_quick_ball_option
from supporter_opponent_tradeoff_frontier import opponent_next_draw_readiness


def card_draw_hit(pool:tuple[int,...], targets:set[int], n:int)->Fraction:
    d=min(n,len(pool))
    return Fraction(sum(bool(targets.intersection(subset)) for subset in combinations(pool,d)),
                    comb(len(pool),d))


def physical_buckets(counts,opening,prizes,q,weight):
    """Enumerate actual card IDs for openings, Prize piles, natural draw,
    discarding the exact Quick Ball+filler and subsequent redraw subsets.
    """
    ids=tuple(range(sum(counts)))
    classes={}
    position=0
    for cls,n in enumerate(counts):
        for c in range(position,position+n):classes[c]=cls
        position+=n
    openings=[hand for hand in combinations(ids,opening)
              if any(classes[c]==0 for c in hand)]
    total=len(openings)*comb(len(ids)-opening,prizes)*(len(ids)-opening-prizes)
    sample_mass=Fraction(1,total)
    grouped=defaultdict(lambda:defaultdict(lambda:dict(mass=Fraction())))
    for first in openings:
        active=next(c for c in first if classes[c]==0)
        unknown=tuple(c for c in ids if c not in first)
        for prize in combinations(unknown,prizes):
            for draw in unknown:
                if draw in prize:continue
                hand=tuple(c for c in first if c!=active)+(draw,)
                h=tuple(sum(classes[c]==j for c in hand) for j in range(7))
                deck=tuple(c for c in unknown if c not in prize and c!=draw)
                k=sum(classes[c]==4 for c in deck)
                state=grouped[h][k]
                if state['mass']:
                    state['mass']+=sample_mass
                    continue
                state['mass']=sample_mass
                outs={c for c in ids if classes[c]==4}
                for paid in (False,True):
                    if paid and not(h[5] and h[6]):continue
                    actual_hand=hand
                    if paid:
                        q_card=next(c for c in actual_hand if classes[c]==6)
                        f_card=next(c for c in actual_hand if classes[c]==5)
                        actual_hand=tuple(c for c in actual_hand if c not in (q_card,f_card))
                    payoffs={'Pass':Fraction(int(bool(outs.intersection(actual_hand))))-weight*q[3]}
                    for cls,name,qi in ((1,'Iono',0),(2,'N',1),(3,'Research',2)):
                        if not any(classes[c]==cls for c in actual_hand):continue
                        supporter=next(c for c in actual_hand if classes[c]==cls)
                        residual=tuple(c for c in actual_hand if c!=supporter)
                        if name=='Iono':
                            hit=card_draw_hit(deck,outs,prizes) if prizes<=len(deck) else (
                                Fraction(1) if bool(outs.intersection(deck)) else
                                card_draw_hit(residual,outs,prizes-len(deck)))
                        elif name=='N':
                            hit=card_draw_hit(deck+residual,outs,prizes)
                        else:
                            hit=card_draw_hit(deck,outs,7)
                        payoffs[name]=hit-weight*q[qi]
                    state[paid]=payoffs
    buckets=defaultdict(Fraction)
    payable=Fraction()
    for hand,values in grouped.items():
        mass=sum((st['mass'] for st in values.values()),Fraction())
        if not (hand[5] and hand[6]):continue
        payable+=mass
        base=max(sum((st['mass']/mass * st[False][a] for st in values.values()),Fraction())
                 for a in next(iter(values.values()))[False])
        informed=sum((st['mass']/mass*max(st[True].values()) for st in values.values()),Fraction())
        delta=informed-base
        if delta>0:
            buckets[delta]+=mass
    return payable,tuple(sorted(buckets.items()))


def check_small():
    tests=0
    q=(Fraction(1,5),Fraction(1,2),Fraction(1),Fraction(1))
    for cards in ((2,1,1,1,1,2,1),(2,1,2,1,2,1,1),(3,1,1,1,1,2,1)):
        for p in (1,2):
            for lam in (Fraction(0),Fraction(1,2),Fraction(2)):
                model=quick_ball_cost_frontier(counts=cards,opening_size=3,
                      prize_count=p,opponent_penalties=q,weight=lam)
                payable,buckets=physical_buckets(cards,3,p,q,lam)
                assert (model.source_payable,model.positive_thresholds)==(payable,buckets),(
                    cards,p,lam,model.positive_thresholds,buckets)
                candidate={Fraction(0),Fraction(1,1000)}
                for d,_ in buckets:
                    candidate.add(d)
                    candidate.add(d/2)
                    candidate.add(d+1)
                for tau in candidate:
                    gain=sum((mass*max(Fraction(),d-tau) for d,mass in buckets),Fraction())
                    use=sum((mass for d,mass in buckets if d>tau),Fraction())
                    assert model.evaluate(tau)==(gain,use)
                tests+=1
    return tests


def witness():
    z=opponent_next_draw_readiness(deck_size=46,prizes_hidden=6,
                                  unknown_outs=4,hand_size=5,hand_outs=1)
    q=z.as_tuple()+(z.research,)
    f0=quick_ball_cost_frontier(opponent_penalties=q,weight=0)
    assert len(f0.positive_thresholds)==1
    threshold=Fraction(1353050739,110231206540)
    assert f0.maximum_willingness_to_pay==threshold
    assert round(float(f0.source_payable),12)==0.423912352445
    assert round(float(f0.zero_cost_use_probability),12)==0.040155844060
    assert round(float(100*f0.zero_cost_gain),12)==0.049289939016
    assert f0.evaluate(threshold)==(0,0)
    assert f0.evaluate(Fraction(1,100))==(f0.zero_cost_gain-Fraction(1,100)*f0.zero_cost_use_probability,
                                          f0.zero_cost_use_probability)
    f1=quick_ball_cost_frontier(opponent_penalties=q,weight=Fraction(1,10))
    assert len(f1.positive_thresholds)==3
    assert f1.positive_thresholds[0][0]==Fraction(4594208356,72339229291875)
    assert f1.positive_thresholds[1][0]==Fraction(2444621,4188115750)
    assert f1.positive_thresholds[2][0]==threshold
    assert round(float(f1.zero_cost_gain*100),12)==0.051818963349
    assert round(float(f1.zero_cost_use_probability),12)==0.107819190102
    f2=quick_ball_cost_frontier(opponent_penalties=q,weight=2)
    assert len(f2.positive_thresholds)==6
    assert f2.maximum_willingness_to_pay==Fraction(677809,50896300)
    for f in (f0,f1,f2):
        v=physical_quick_ball_option(opponent_penalties=q,weight=f.weight)
        assert f.evaluate(0)==(v.optimal_net_improvement,v.searched_probability)
        for (left,_),(right,_) in zip(f.positive_thresholds,f.positive_thresholds[1:]):
            m=(left+right)/2
            xl,pl=f.evaluate(left); xr,pr=f.evaluate(right);xm,pm=f.evaluate(m)
            assert 2*xm==xl+xr
            assert pl>=pm>=pr
    print('lambda0 zero-source-cost gain pp',float(f0.zero_cost_gain*100),
          'fraction of hands search chosen',float(f0.zero_cost_use_probability))
    print('exact maximum lambda0 extra source cost',f0.maximum_willingness_to_pay,
          'decimal',float(f0.maximum_willingness_to_pay))
    print('lambda0.1 exact thresholds:',f1.positive_thresholds)
    print('lambda2 exact thresholds:',f2.positive_thresholds)


if __name__=='__main__':
    print('Independent labeled-physical cost threshold models:',check_small())
    witness()
