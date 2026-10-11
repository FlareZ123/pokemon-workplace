"""Independent shuffled 60-card test of opponent Supporter reachability."""
import json
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from beheeyem_opponent_supporter_access import opponent_supporter_access


def simulate(prizes_earned: int,trials: int=200000,seed: int=20261011):
    rng=Random(seed)
    population=["B"]*12+["A"]*4+["J"]*4+["F"]*40
    counts={"neither":0,"ace_only":0,"judge_only":0,"both":0}
    accepted=0
    while accepted<trials:
        rng.shuffle(population)
        opener=population[:7]
        if "B" not in opener:
            continue
        accepted+=1
        prizes=population[7:13]
        deck=population[13:]
        reward=rng.sample(prizes,prizes_earned)
        observed=opener+deck[:2]+reward
        has_a="A" in observed
        has_j="J" in observed
        key=("both" if has_a and has_j else
             "ace_only" if has_a else
             "judge_only" if has_j else "neither")
        counts[key]+=1
    exact=opponent_supporter_access(12,4,4,2,prizes_earned)
    for label,prob in exact.items():
        p=float(prob)
        observed=counts[label]/trials
        sigma=sqrt(max(p*(1-p),1/trials)/trials)
        assert abs(observed-p)<6*sigma+1/trials, (
            prizes_earned,label,observed,p,sigma
        )
    return {
        "prizes_earned":prizes_earned,"seed":seed,"trials":trials,
        "physical_observed_percent":{
            key:round(100*value/trials,6) for key,value in counts.items()
        },
        "exact_percent":{
            key:round(100*float(value),6) for key,value in exact.items()
        }
    }


if __name__=="__main__":
    print(json.dumps([
        simulate(s,seed=20261011+s) for s in (0,1,2)
    ],indent=2))
