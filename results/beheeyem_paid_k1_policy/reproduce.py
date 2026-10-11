"""Exact sequential Ultra Ball early search, hand reset and K1 payoff test."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_paid_k1_policy import (
    initial_prelock_masses,exact_early_search_policy
)
from beheeyem_prelock_k1_search import search_window_probabilities


def run():
    masses=initial_prelock_masses(2)
    assert sum(masses.values())==1
    assert sum(w for (a,j,x,ok),w in masses.items() if ok)==(
        search_window_probabilities(2)["paid_search_feasible"]
    )
    rows=[]
    for r in (0,1,2):
        for weight in (0,10,100):
            previous_gain=None
            previous_search=None
            for cost in (
                Fraction(),Fraction(1,10000),
                Fraction(1,1000),Fraction(1,100),
                Fraction(1,10)
            ):
                result=exact_early_search_policy(
                    r=r,lambda_weight=Fraction(weight),
                    tau=cost,route_observed=True
                )
                assert result["optimal_with_optional_search_utility"]>=(
                    result["baseline_no_search_utility"]
                )
                assert 0<=result["early_search_chosen_mass"]<=(
                    result["eligible_prelock_search"]
                )
                assert result["paid_K1_information_gain_if_all_payable_played"]>=0
                assert result["paid_thinning_alone_gain_if_all_payable_played"]>=0
                if previous_gain is not None:
                    assert result["gain_over_no_search"]<=previous_gain
                    assert result["early_search_chosen_mass"]<=previous_search
                previous_gain=result["gain_over_no_search"]
                previous_search=result["early_search_chosen_mass"]
                rows.append({
                    "r":r,"lambda":weight,"cost_tau":str(cost),
                    "prelock_paid_U_eligible_percent":round(
                        100*float(result["eligible_prelock_search"]),7
                    ),
                    "early_U_actually_used_percent":round(
                        100*float(result["early_search_chosen_mass"]),7
                    ),
                    "gain_over_baseline_utility":round(
                        float(result["gain_over_no_search"]),10
                    ),
                    "baseline_utility":round(
                        float(result["baseline_no_search_utility"]),8
                    )
                })
            assert exact_early_search_policy(
                r=r,lambda_weight=Fraction(weight),tau=Fraction(1,10)
            )["early_search_chosen_mass"]==0
    assert len(rows)==45
    return {"states":len(masses),"settings":len(rows),"rows":rows}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
