"""Exact enumeration and card-text regression for Iono versus N access."""
from __future__ import annotations
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from iono_n_access_comparison import compare_iono_n


def independent_hit(pool: tuple[int,...],outs: frozenset[int],draw:int)->Fraction:
    d=min(draw,len(pool))
    samples=list(combinations(pool,d))
    return Fraction(sum(any(card in outs for card in sample) for sample in samples),len(samples))


def exact_enumeration()->int:
    checked=0
    for deck_size in range(1,6):
        for hand_size in range(5):
            deck=tuple(range(deck_size))
            hand=tuple(range(deck_size,deck_size+hand_size))
            for deck_outs in range(deck_size+1):
                for hand_outs in range(hand_size+1):
                    targets=frozenset(deck[:deck_outs]+hand[:hand_outs])
                    for prizes in range(deck_size+hand_size+2):
                        for opponent_hand in (0,1):
                            result=compare_iono_n(
                                deck_size=deck_size,hand_size=hand_size,
                                deck_outs=deck_outs,hand_outs=hand_outs,
                                prizes_remaining=prizes,opponent_hand_size=opponent_hand)
                            n=independent_hit(deck+hand,targets,prizes)
                            if not hand_size and not opponent_hand:
                                iono=Fraction(0)
                            elif prizes<=deck_size:
                                iono=independent_hit(deck,targets,prizes)
                            elif deck_outs>0:
                                iono=Fraction(1)
                            else:
                                iono=independent_hit(hand,targets,prizes-deck_size)
                            assert (result.iono_hit,result.n_hit,result.iono_minus_n)==(iono,n,iono-n), (
                                deck_size,hand_size,deck_outs,hand_outs,prizes,opponent_hand)
                            checked+=1
    return checked


def snapshot_source_check()->None:
    cases=(("sv2-185","Iono","If either player put any cards on the bottom of their deck"),
           ("bw3-92","N","Then, each player draws a card for each"))
    for card_id,name,phrase in cases:
        set_id=card_id.split("-",1)[0]
        cards=json.loads((ROOT/"resources"/"cards"/"en"/f"{set_id}.json").read_text(encoding="utf-8"))
        card=next(c for c in cards if c["id"]==card_id)
        assert card["name"]==name and any(phrase in rule for rule in card["rules"])
    print("Paper-Expanded print text witnesses verified")


def witnesses()->None:
    d={"deck_size":46,"hand_size":5,"prizes_remaining":6,"opponent_hand_size":2}
    # 8 total outs, alternate placement between hand and deck.
    values=[]
    for r in range(6):
        x=compare_iono_n(**d,deck_outs=8-r,hand_outs=r)
        values.append(x.iono_minus_n)
    assert values[0]>0 and values[1]<0
    assert round(100*float(values[0]),6)==4.378415
    assert round(100*float(values[1]),6)==-0.980309
    # A hand that starts empty may still draw with Iono due to other player.
    x=compare_iono_n(deck_size=46,hand_size=0,deck_outs=3,hand_outs=0,
                      prizes_remaining=6,opponent_hand_size=1)
    assert x.iono_hit==x.n_hit
    y=compare_iono_n(deck_size=46,hand_size=0,deck_outs=3,hand_outs=0,
                      prizes_remaining=6,opponent_hand_size=0)
    assert y.iono_hit==0 and y.n_hit>0
    # One retained hand out: enough deck outs make bottoming better immediately.
    thresholds={}
    for prize_count in range(1,7):
        passing=[k for k in range(47) if compare_iono_n(
            deck_size=46,hand_size=5,deck_outs=k,hand_outs=1,
            prizes_remaining=prize_count,opponent_hand_size=1).iono_minus_n>=0]
        thresholds[prize_count]=min(passing)
    assert thresholds=={1:10,2:10,3:9,4:9,5:9,6:9}
    print("Six-draw delta at 8 total outs: R0 +4.378415 pp; R1 -0.980309 pp")
    print("One hand out break-even K by prize count 1..6:",thresholds)


if __name__=="__main__":
    snapshot_source_check()
    print("Exact enumerated cases:",exact_enumeration())
    witnesses()
