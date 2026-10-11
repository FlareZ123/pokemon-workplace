"""Independent physical random shuffles after losing target/non-target cards."""
import json
from math import sqrt
from random import Random
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from discard_target_hit_probability import hit_probability


def run(N,K,n,m,t,trials=200000,seed=20261126):
    rng=Random(seed)
    remaining=["X"]*(K-t)+["F"]*(N-K-(m-t))
    success=0
    for _ in range(trials):
        rng.shuffle(remaining)
        success+=int("X" in remaining[:n])
    observed=success/trials
    exact=float(hit_probability(N-m,K-t,n))
    sigma=sqrt(max(exact*(1-exact),1/trials)/trials)
    assert abs(observed-exact)<6*sigma+1/trials
    return {
        "N":N,"K":K,"draws":n,"discarded_total":m,
        "discarded_targets":t,"trials":trials,
        "observed_hit_percent":round(observed*100,7),
        "exact_hit_percent":round(exact*100,7)
    }


if __name__=="__main__":
    print(json.dumps([
        run(53,4,6,3,0,seed=20261126),
        run(53,4,6,3,1,seed=20261127),
        run(7,2,3,3,1,seed=20261128)
    ],indent=2))
