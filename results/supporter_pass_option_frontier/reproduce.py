"""Exact no-Supporter cancellation and finite-action cost-frontier checks."""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from pathlib import Path
from random import Random
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))

from action_information_weight_frontier import evaluate_linear_choice,exact_linear_frontier
from multi_action_information_envelope import action_information_envelope
from supporter_opponent_tradeoff_frontier import weighted_supporter_choice
from supporter_pass_option_frontier import build_pass_option_model


def generic_checks():
    checks=0
    # Two actions and two states, exact exhaustive affine envelopes.
    for wa in (Fraction(1,4),Fraction(1,2),Fraction(3,4)):
        for rewards in product((-1,0,1),repeat=4):
            for costs in product((0,1,2),repeat=2):
                rows=(
                    (wa,{"a":(rewards[0],costs[0]),"b":(rewards[1],costs[1])}),
                    (1-wa,{"a":(rewards[2],costs[0]),"b":(rewards[3],costs[1])}),
                )
                f=exact_linear_frontier(rows)
                evalr=lambda x:evaluate_linear_choice(rows,x)
                assert f.peak_information_value>=0
                assert f.peak_envelope.information_value==f.peak_information_value
                for left,right in zip(f.candidates,f.candidates[1:]):
                    m=(left+right)/2
                    assert 2*evalr(m).information_value == (
                        evalr(left).information_value+evalr(right).information_value)
                assert evalr(f.candidates[-1]+10).information_value<=f.peak_information_value
                checks+=1
    # Deterministic 3+ action cases with heterogeneous intercepts and
    # *state-independent* penalties.
    rng=Random(20261011)
    for _ in range(600):
        names=tuple("abc"[:rng.randint(2,3)])
        costs={n:Fraction(rng.randrange(5),3) for n in names}
        masses=(Fraction(1,3),Fraction(2,3))
        states=tuple((m,{n:(Fraction(rng.randrange(-6,7),5),costs[n])
                         for n in names}) for m in masses)
        f=exact_linear_frontier(states)
        for left,right in zip(f.candidates,f.candidates[1:]):
            mid=(left+right)/2
            vals=[evaluate_linear_choice(states,t).information_value
                  for t in (left,mid,right)]
            assert 2*vals[1]==vals[0]+vals[2]
        assert evaluate_linear_choice(states,f.candidates[-1]+100).information_value<=f.peak_information_value
        checks+=1
    # Explicit invalid global extrapolation: state-specific costs can
    # produce unbounded information gain as weight increases.
    bad=((Fraction(1,2),{"a":(0,0),"b":(0,1)}),
         (Fraction(1,2),{"a":(0,1),"b":(0,0)}))
    assert evaluate_linear_choice(bad,3).information_value==Fraction(3,2)
    try:
        exact_linear_frontier(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("global peak accepted state-dependent cost slopes")
    return checks


def scenario():
    kw=dict(own_deck_size=46,own_prizes_hidden=6,own_unknown_outs=10,
            own_hand_size=5,own_hand_outs=1,
            opponent_deck_size=46,opponent_prizes_hidden=6,
            opponent_unknown_outs=4,opponent_hand_size=5,opponent_hand_outs=1)
    model=build_pass_option_model(**kw)
    f=model.frontier()
    assert len(f.candidates)==38
    assert f.peak_weight==Fraction(374699,800316)
    assert f.peak_information_value==Fraction(207557493001,12375020344400)
    assert f.peak_envelope.optimal_after_observation==(
        "Pass","Pass","Pass","Pass","Pass","Iono","Iono")
    assert f.peak_envelope.best_fixed_action=="Iono"
    assert model.evaluate(0).information_value==0
    assert model.evaluate(Fraction(1,10)).information_value==0
    assert model.evaluate(2).information_value==0
    assert round(float(model.evaluate(Fraction(1,2)).information_value*100),9)==1.109136964
    print("Exact four-action crossing candidates:",len(f.candidates))
    print("Peak no-Supporter-option information weight:", f.peak_weight,
          "decimal",f"{float(f.peak_weight):.12f}")
    print("Peak information value:",f.peak_information_value,
          "pp",f"{float(f.peak_information_value*100):.9f}")
    print("Policy by known own K=4..10:",f.peak_envelope.optimal_after_observation)
    print("Without optional Pass, conditional Supporter K1 at lambda0.1:",
          f"{float(weighted_supporter_choice(weight=Fraction(1,10),opponent=model.opponent,own=model.own).payoff.information_value*100):.9f} pp")
    print("With Pass, same lambda0.1:",f"{float(model.evaluate(Fraction(1,10)).information_value*100):.9f} pp")

    for left,right in zip(f.candidates,f.candidates[1:]):
        m=(left+right)/2
        assert 2*model.evaluate(m).information_value==(
            model.evaluate(left).information_value+model.evaluate(right).information_value)
    # If no known out is held, Pass has no own access and Research has
    # the same opponent penalty, so Research weakly dominates Pass.
    no_out=build_pass_option_model(**{**kw,"own_hand_outs":0})
    for w in (0,Fraction(1,10),Fraction(1,2),1,2):
        original=weighted_supporter_choice(weight=Fraction(w),opponent=no_out.opponent,own=no_out.own)
        new=no_out.evaluate(Fraction(w))
        assert new.observed_value==original.payoff.observed_value
        assert new.best_fixed_value==original.payoff.best_fixed_value
        assert new.information_value==original.payoff.information_value
    print("R=0 negative control: Pass is weakly dominated by Research for 5 weights")
    return len(f.candidates)-1


if __name__=="__main__":
    print("Exact generic weight-frontier configurations:",generic_checks())
    print("Scenario affine regions:",scenario())
