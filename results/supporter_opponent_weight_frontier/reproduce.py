"""Independent physical opponent Prize enumeration and rational utility frontier."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))

from prize_three_supporter_choice import three_supporter_choice
from supporter_opponent_tradeoff_frontier import (
    opponent_next_draw_readiness, weighted_supporter_choice,
    candidate_weight_frontier, ACTIONS,
)


def raw_draw_hit(pool: tuple[int,...], targets: set[int], draw:int) -> Fraction:
    n=min(draw,len(pool))
    hit=sum(bool(set(subset).intersection(targets))
            for subset in combinations(pool,n))
    return Fraction(hit,comb(len(pool),n))


def brute_opponent(D:int,P:int,U:int,Q:int,Y:int):
    all_unknown=tuple(range(D+P))
    unknown_outs=set(all_unknown[:U])
    hand=tuple(range(D+P,D+P+Q))
    hand_outs=set(hand[:Y])
    counts=[Fraction(),Fraction(),Fraction()]
    assignments=0
    for prize in combinations(all_unknown,P):
        deck=tuple(x for x in all_unknown if x not in prize)
        targets=unknown_outs.intersection(deck)
        payoffs=(raw_draw_hit(deck,targets,P+1),
                 raw_draw_hit(deck+hand,targets|hand_outs,P+1),
                 Fraction(1) if hand_outs else raw_draw_hit(deck,targets,1))
        for i,r in enumerate(payoffs):counts[i]+=r
        assignments+=1
    return tuple(v/assignments for v in counts)


def test_opponent():
    checks=0
    for D in range(2,6):
        for P in range(1,min(3,D-1)+1):
            for U in range(D+P+1):
                for Q in range(4):
                    for Y in range(Q+1):
                        r=opponent_next_draw_readiness(
                            deck_size=D,prizes_hidden=P,unknown_outs=U,
                            hand_size=Q,hand_outs=Y)
                        assert r.as_tuple()==brute_opponent(D,P,U,Q,Y),(D,P,U,Q,Y)
                        checks+=1
    return checks


def test_observed_own():
    checks=0
    # Pure K1 own information, with opponent L correctly marginalized first.
    op=opponent_next_draw_readiness(
        deck_size=4,prizes_hidden=2,unknown_outs=3,
        hand_size=2,hand_outs=1)
    for D in range(1,5):
        for P in range(1,3):
            for U in range(D+P+1):
                for H in range(3):
                    for R in range(H+1):
                        Q=2
                        if H+Q==0: continue
                        own=three_supporter_choice(
                            deck_size=D,prizes_hidden=P,unknown_outs=U,
                            hand_size=H,hand_outs=R,
                            prize_draw_count=P,opponent_hand_size=Q)
                        for lam in (Fraction(0),Fraction(1,10),Fraction(1,2),Fraction(2)):
                            e=weighted_supporter_choice(weight=lam,opponent=op,own=own)
                            expected=[sum((p*(v-lam*op.as_tuple()[i])
                                           for _,p,*a in own.rows for v in [a[i]]),Fraction())
                                      for i in range(3)]
                            informed=sum((p*max(v-lam*q for v,q in zip(a,op.as_tuple()))
                                          for _,p,*a in own.rows),Fraction())
                            assert e.payoff.best_fixed_value==max(expected)
                            assert e.payoff.observed_value==informed
                            assert e.payoff.information_value==informed-max(expected)
                            checks+=1
    return checks


def test_exact_frontier():
    own=three_supporter_choice(
        deck_size=46,prizes_hidden=6,unknown_outs=10,
        hand_size=5,hand_outs=1,prize_draw_count=6,opponent_hand_size=5)
    op=opponent_next_draw_readiness(
        deck_size=46,prizes_hidden=6,unknown_outs=4,
        hand_size=5,hand_outs=1)
    q=op.as_tuple()
    assert [round(float(v),12) for v in q]==[
        0.449644473174,0.499534387026,1.0]
    f=candidate_weight_frontier(opponent=op,own=own)
    assert len(f.candidates)==22
    assert round(float(f.peak_weight),12)==0.101780177265
    assert round(float(f.peak_value*100),9)==0.118469577
    assert f.peak_policy==( "N","N","N","Professor's Research",
                              "Professor's Research","Iono","Iono")
    at=lambda w:weighted_supporter_choice(weight=w,opponent=op,own=own).payoff
    assert at(0).information_value==0
    assert at(Fraction(1,10)).information_value>0
    assert at(1).information_value==0
    for left,right in zip(f.candidates,f.candidates[1:]):
        a,b=at(left),at(right)
        mid=at((left+right)/2)
        assert 2*mid.information_value==a.information_value+b.information_value
        assert mid.information_value<=f.peak_value
    assert at(f.candidates[-1]+100).information_value<=f.peak_value
    print("Opponent future target readiness Iono/N/Research:",
          *(f"{float(v*100):.6f}%" for v in q))
    print("Exact candidate crossing count:",len(f.candidates))
    print("Maximum information premium:",f"{float(f.peak_value*100):.9f} pp",
          "at opponent-denial weight",f"{float(f.peak_weight):.12f}")
    print("Policy by K=4..10 at maximum:", f.peak_policy)
    print("Information gain at weights 0, 0.1 and 1:",
          *(f"{float(at(w).information_value*100):.9f} pp"
            for w in (0,Fraction(1,10),1)))
    return len(f.candidates)-1


if __name__=="__main__":
    print("Independent opposing Prize/readiness physical cases:",test_opponent())
    print("Independent own-state utility-envelope checks:",test_observed_own())
    print("Piecewise-affine frontier intervals validated:",test_exact_frontier())
