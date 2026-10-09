"""Independent Prize-subset enumeration for K0 versus K1 Iono/N choice."""
from __future__ import annotations
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from prize_informed_iono_n_choice import prize_uncertain_choice


def brute_hit(deck_size:int,hand_size:int,deck_outs:int,hand_outs:int,
              draw_count:int,opponent_hand_size:int):
    deck=tuple(range(deck_size))
    hand=tuple(range(deck_size,deck_size+hand_size))
    outs=set(deck[:deck_outs]+hand[:hand_outs])
    draw_iono=min(draw_count,len(deck))
    if hand_size+opponent_hand_size==0:
        p_iono=Fraction(0)
    elif draw_count<=deck_size:
        samples=list(combinations(deck,draw_iono))
        p_iono=Fraction(sum(bool(outs.intersection(x)) for x in samples),len(samples))
    else:
        # Every deck card is drawn before sampling the shuffled old hand.
        if deck_outs:
            p_iono=Fraction(1)
        else:
            samples=list(combinations(hand,min(draw_count-deck_size,hand_size)))
            p_iono=Fraction(sum(bool(outs.intersection(x)) for x in samples),len(samples))
    full=deck+hand
    samples=list(combinations(full,min(draw_count,len(full))))
    p_n=Fraction(sum(bool(outs.intersection(x)) for x in samples),len(samples))
    return p_iono,p_n


def brute_prior(*,D:int,P:int,U:int,H:int,R:int,d:int,Q:int):
    unknown=tuple(range(D+P))
    outs=set(range(U))
    prize_states=list(combinations(unknown,P))
    pairs=[]
    for prize in prize_states:
        remaining=set(unknown)-set(prize)
        k=len(remaining & outs)
        pairs.append(brute_hit(D,H,k,R,d,Q))
    pi=sum((a for a,b in pairs),Fraction(0))/len(pairs)
    pn=sum((b for a,b in pairs),Fraction(0))/len(pairs)
    adaptive=sum((max(a,b) for a,b in pairs),Fraction(0))/len(pairs)
    return max(pi,pn),adaptive,pi,pn


def test_small():
    checks=0
    for D in range(1,5):
        for P in range(4):
            for U in range(D+P+1):
                for H in range(4):
                    for R in range(H+1):
                        for d in range(4):
                            for Q in (0,1):
                                result=prize_uncertain_choice(
                                    deck_size=D,prizes_hidden=P,unknown_outs=U,
                                    hand_size=H,hand_outs=R,prize_draw_count=d,
                                    opponent_hand_size=Q)
                                expected=brute_prior(D=D,P=P,U=U,H=H,R=R,d=d,Q=Q)
                                assert (result.before_information,result.after_information,
                                        result.fixed_iono,result.fixed_n)==expected,(
                                    D,P,U,H,R,d,Q)
                                assert result.information_gain==expected[1]-expected[0]
                                checks+=1
    return checks


def witness():
    r=prize_uncertain_choice(
        deck_size=46,prizes_hidden=6,unknown_outs=10,
        hand_size=5,hand_outs=1,prize_draw_count=6,opponent_hand_size=2)
    assert len(r.rows)==7 and r.rows[0].deck_outs==4 and r.rows[-1].deck_outs==10
    assert [row.optimal_choice for row in r.rows]==["N"]*5+["Iono"]*2
    assert round(100*float(r.fixed_iono),6)==74.232970
    assert round(100*float(r.fixed_n),6)==74.206755
    assert round(100*float(r.after_information),6)==74.401981
    assert round(100*float(r.information_gain),6)==0.169011
    print("K0 best = Iono, 74.232970%; K1 adaptive = 74.401981%; pure info = +0.169011 pp")
    print("K1 chooses N for K=4..8 and Iono for K=9..10")


if __name__=="__main__":
    print("Independent exact Prize-subset and draw subset checks:",test_small())
    witness()
