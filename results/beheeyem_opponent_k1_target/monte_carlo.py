"""Physical remaining-Prize X count and full-shuffle K1 redraw validation."""
from math import sqrt
from pathlib import Path
from random import Random
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_opponent_k1_target import own_x_after_reset_k1


def run(earned: int,quota: int,seed: int,trials: int=150000):
    rng=Random(seed)
    cards=["B"]*12+["A"]*4+["J"]*4+["X"]*4+["F"]*36
    n=[0]*5
    found=[0]*5
    accepted=0
    while accepted<trials:
        rng.shuffle(cards)
        hand=cards[:7]
        if "B" not in hand:
            continue
        accepted+=1
        prizes=list(cards[7:13])
        deck=list(cards[13:])
        hand=list(hand)+deck[:2]
        deck=deck[2:]
        rng.shuffle(prizes)
        hand+=prizes[:earned]
        z=prizes[earned:].count("X")
        index=next(i for i,v in enumerate(hand) if v!="X")
        hand.pop(index)  # discard played non-X Supporter
        shuffled=deck+hand
        rng.shuffle(shuffled)
        n[z]+=1
        found[z]+=int("X" in shuffled[:quota])
    rows=[]
    for z,num in enumerate(n):
        if num<50:
            continue
        expected=float(own_x_after_reset_k1(z,earned,quota))
        obs=found[z]/num
        sigma=sqrt(max(expected*(1-expected),1/num)/num)
        assert abs(obs-expected)<6*sigma+1/num,(z,earned,quota,obs,expected)
        rows.append({
            "X_still_prized":z,"observed_states":num,
            "observed_success_percent":round(obs*100,6),
            "exact_success_percent":round(expected*100,6)
        })
    return {"earned":earned,"draw_quota":quota,"trials":trials,"states":rows}


if __name__=="__main__":
    print(json.dumps([
        run(0,4,20261102),run(1,6,20261103),run(2,6,20261104)
    ],indent=2))
