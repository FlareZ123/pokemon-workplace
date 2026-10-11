"""Independent physical Ultra Ball whiff then locked-turn Supporter redraw.

Valid Basic opener, six Prizes, two prelock draws, optional paid Ultra Ball,
one reply draw. Compare actual Judge/Ace physical full reshuffle to exact
remaining-X-Prized combinatorics, conditional on the Supporter being held.
"""
import json
from math import sqrt,comb
from pathlib import Path
from random import Random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_prelock_k1_search import search_window_probabilities


def simulate(source="J",quota=4,trials=200000,seed=20261121):
    rng=Random(seed)
    population=["B"]*12+["A"]*4+["J"]*4+["X"]*4+["U"]*4+["F"]*32
    accepted=eligible=0
    counts={"early_paid":0,"unpaid":0}
    observed={"early_paid":0,"unpaid":0}
    expected={"early_paid":0.0,"unpaid":0.0}
    while accepted<trials:
        rng.shuffle(population)
        opener=list(population[:7])
        if "B" not in opener:
            continue
        accepted+=1
        prizes=population[7:13]
        top=population[13:]
        pre=opener+top[:2]
        if "U" not in pre or pre.count("F")<2:
            continue
        eligible+=1
        z=prizes.count("X")
        for kind in ("early_paid","unpaid"):
            hand=list(pre)
            deck=list(top[2:])
            if kind=="early_paid":
                hand.remove("U")
                hand.remove("F")
                hand.remove("F")
                # Empty-result constrained search, then shuffle deck.
                rng.shuffle(deck)
            hand.append(deck.pop(0))  # first reply draw, Items now locked
            if source not in hand:
                continue
            hand.remove(source)  # play Judge/Ace Trainer from hand
            deck.extend(hand)
            rng.shuffle(deck)
            counts[kind]+=1
            observed[kind]+=int("X" in deck[:quota])
            n=len(deck)
            assert n==(50 if kind=="early_paid" else 53)
            expected[kind]+=1-comb(n-(4-z),quota)/comb(n,quota)

    direct=search_window_probabilities(2)["paid_search_feasible"]
    p_eligible=eligible/accepted
    sigma=sqrt(max(float(direct)*(1-float(direct)),1/trials)/trials)
    assert abs(p_eligible-float(direct))<6*sigma+1/trials
    output={
        "supporter":source,"draw_quota":quota,"trials":trials,
        "paid_source_eligible_percent":round(100*p_eligible,7),
        "exact_source_eligible_percent":round(100*float(direct),7)
    }
    for kind in counts:
        n=counts[kind]
        assert n>1000
        p_expected=expected[kind]/n
        p_observed=observed[kind]/n
        sigma=sqrt(max(p_expected*(1-p_expected),1/n)/n)
        assert abs(p_observed-p_expected)<6*sigma+1/n
        output[kind]={
            "eligible_and_supporter_held":n,
            "observed_own_X_after_percent":round(100*p_observed,7),
            "exact_conditional_X_after_percent":round(100*p_expected,7)
        }
    return output


if __name__=="__main__":
    print(json.dumps([
        simulate("J",4,seed=20261121),
        simulate("A",6,seed=20261122)
    ],indent=2))
