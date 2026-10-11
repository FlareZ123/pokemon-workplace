"""Exact early source cost thresholds against independent dynamic solver."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_paid_k1_cost_frontier import (
    early_source_cost_frontier,evaluate_frontier
)
from beheeyem_paid_k1_reward_prior import uncertain_reward_early_search
from beheeyem_prelock_k1_search import search_window_probabilities


def run():
    priors=(
        (Fraction(1,3),)*3,
        (Fraction(1,2),Fraction(1,2),Fraction()),
        (Fraction(),Fraction(1,2),Fraction(1,2)),
        (Fraction(1,10),Fraction(8,10),Fraction(1,10))
    )
    report=[]
    probes=0
    for prior in priors:
        f=early_source_cost_frontier(prior)
        assert f["total_physical_payable_mass"]==search_window_probabilities(2)["paid_search_feasible"]
        assert len(f["segments"])==f["num_positive_benefits"]+1
        assert f["max_positive_benefit"]>0
        previous_mass=None
        for index,interval in enumerate(f["segments"]):
            start=interval["from_tau"]
            end=interval["to_tau"]
            assert interval["search_probability_on_interior"]>=0
            if previous_mass is not None:
                assert interval["search_probability_on_interior"]<previous_mass
            previous_mass=interval["search_probability_on_interior"]
            trial_values=[start,interval["probe_tau"]]
            if end is not None:
                trial_values.append((start*3+end)/4)
            for cost in trial_values:
                x=evaluate_frontier(f,cost)
                direct=uncertain_reward_early_search(
                    prior,Fraction(10),cost
                )
                assert x["gain"]==direct["incremental_value"]
                assert x["use_probability"]==direct["prelock_paid_search_used"]
                probes+=1
        assert evaluate_frontier(
            f,f["max_positive_benefit"]
        )=={"use_probability":Fraction(),"gain":Fraction()}
        report.append({
            "reward_prior":[str(v) for v in prior],
            "positive_cost_switches":f["num_positive_benefits"],
            "num_payable_benefit_values":f["num_distinct_payable_benefits"],
            "max_willingness_to_pay":str(f["max_positive_benefit"]),
            "max_willingness_float":round(
                float(f["max_positive_benefit"]),10
            ),
            "source_chosen_tau_0_percent":round(
                100*float(evaluate_frontier(f,Fraction())["use_probability"]),8
            ),
            "source_chosen_tau_0_01_percent":round(
                100*float(evaluate_frontier(f,Fraction(1,100))["use_probability"]),8
            ),
            "source_chosen_tau_0_1_percent":round(
                100*float(evaluate_frontier(f,Fraction(1,10))["use_probability"]),8
            ),
            "exact_tradeoff_segments":len(f["segments"])
        })
    assert probes>=12
    return {"independent_exact_policy_probes":probes,"frontiers":report}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
