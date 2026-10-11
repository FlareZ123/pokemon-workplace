"""Independent physical opposing hand-draw test of own-X target availability."""
import json
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_opponent_self_target import (
    observed_hand_mass,own_target_after_reset
)


def simulate(prizes_earned: int,quota: int,trials: int=160000,seed: int=102611):
    rng=Random(seed)
    pool=["B"]*12+["A"]*4+["J"]*4+["X"]*4+["F"]*36
    seen_x=[0]*5
    ready_x=[0]*5
    achieved=0
    while achieved<trials:
        rng.shuffle(pool)
        hand=list(pool[:7])
        if "B" not in hand:
            continue
        achieved+=1
        prizes=list(pool[7:13])
        deck=list(pool[13:])
        hand+=deck[:2]
        deck=deck[2:]
        rng.shuffle(prizes)
        hand+=prizes[:prizes_earned]

        x=hand.count("X")
        seen_x[x]+=1
        assert len(hand)==9+prizes_earned and len(deck)==45
        # In this independent physical test, assume a separate named
        # Supporter has been chosen from hand and discarded. To avoid
        # skewing the hand-conditioned presence of X, remove a random
        # NON-X card. It matches resetting with a distinct Supporter.
        nonx=next(i for i,v in enumerate(hand) if v!="X")
        hand.pop(nonx)
        deck.extend(hand)
        rng.shuffle(deck)
        sample=deck[:quota]
        ready_x[x]+=int("X" in sample)

    results=[]
    for x,n in enumerate(seen_x):
        if n<100:
            continue
        obs=ready_x[x]/n
        expected=float(own_target_after_reset(x,prizes_earned,quota))
        sigma=sqrt(max(expected*(1-expected),1/n)/n)
        assert abs(obs-expected)<6*sigma+1/n,(x,n,obs,expected)
        observed_x=n/trials
        true_x=sum(
            observed_hand_mass(a,j,x,prizes_earned)
            for a in range(5) for j in range(5)
        )
        sigma_x=sqrt(max(float(true_x)*(1-float(true_x)),1/trials)/trials)
        assert abs(observed_x-float(true_x))<6*sigma_x+1/trials
        results.append({
            "X_held_before_reset":x,
            "trials_with_this_held_X":n,
            "observed_X_after_percent":round(100*obs,6),
            "exact_X_after_percent":round(100*expected,6)
        })
    return {
        "awarded_opponent_prizes":prizes_earned,
        "supporter_draw_quota":quota,
        "trials":trials,"seed":seed,"results":results
    }


if __name__=="__main__":
    print(json.dumps([
        simulate(s,q,seed=20261030+s*10+q)
        for s,q in ((0,4),(1,6),(2,6))
    ],indent=2))
