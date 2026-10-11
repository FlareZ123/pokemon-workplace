"""Physical 60-card Ultra Ball paid-search before Mysterious Noise lock."""
import json
from math import sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_prelock_k1_search import missed_under_item_lock


def run(pre,locked,earned,trials=200000,seed=20261111):
    rng=Random(seed)
    deck=["B"]*12+["U"]*4+["F"]*32+["O"]*12
    paid_before=paid_after=0
    accepted=0
    while accepted<trials:
        rng.shuffle(deck)
        hand=deck[:7]
        if "B" not in hand:
            continue
        accepted+=1
        prizes=list(deck[7:13])
        draw=list(deck[13:])
        rng.shuffle(prizes)
        before=hand+draw[:pre]+prizes[:earned]
        after=before+draw[pre:pre+locked]
        paid_before+=int(before.count("U")>=1 and before.count("F")>=2)
        paid_after+=int(after.count("U")>=1 and after.count("F")>=2)
    exact=missed_under_item_lock(pre,locked,earned)
    observed=(paid_before/trials,paid_after/trials)
    expected=(float(exact["K1_before_lock"]),
              float(exact["K1_if_items_remained_playable"]))
    for o,p in zip(observed,expected):
        sigma=sqrt(max(p*(1-p),1/trials)/trials)
        assert abs(o-p)<6*sigma+1/trials,(o,p)
    return {
        "early_draws":pre,"locked_draws":locked,"earned_prizes":earned,
        "trials":trials,"seed":seed,
        "physical_percent":[round(100*x,7) for x in observed],
        "exact_percent":[round(100*x,7) for x in expected]
    }


if __name__=="__main__":
    print(json.dumps([
        run(0,4,0,seed=20261110),
        run(2,4,0,seed=20261111),
        run(2,4,1,seed=20261112),
        run(4,0,2,seed=20261113)
    ],indent=2))
