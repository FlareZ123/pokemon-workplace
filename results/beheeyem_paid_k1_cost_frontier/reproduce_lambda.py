"""Two-dimensional sensitivity: exact source-cost frontier by denial weight."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_paid_k1_cost_frontier import (
    early_source_cost_frontier,evaluate_frontier
)
from beheeyem_paid_k1_reward_prior import uncertain_reward_early_search


def run():
    prior=(Fraction(1,3),)*3
    rows=[]
    previous=None
    for denial in (0,1,3,5,10,20,50,100,10000):
        lam=Fraction(denial)
        frontier=early_source_cost_frontier(prior,lam)
        for extra in (Fraction(),Fraction(1,1000),Fraction(1,100)):
            approximate=evaluate_frontier(frontier,extra)
            exact=uncertain_reward_early_search(
                prior,lam,extra
            )
            assert approximate["gain"]==exact["incremental_value"]
            assert approximate["use_probability"]==(
                exact["prelock_paid_search_used"]
            )
        result=evaluate_frontier(frontier,Fraction())
        rows.append({
            "lambda":denial,
            "positive_source_cost_thresholds":frontier["num_positive_benefits"],
            "max_extra_cost_worth_paying":round(
                float(frontier["max_positive_benefit"]),10
            ),
            "source_use_percent_at_zero_cost":round(
                float(result["use_probability"])*100,7
            ),
            "source_gain_at_zero_cost":round(float(result["gain"]),10),
            "source_use_percent_at_cost_0_01":round(
                float(evaluate_frontier(
                    frontier,Fraction(1,100)
                )["use_probability"])*100,7
            ),
            "pure_K1_component_if_all_payable_source":round(
                float(frontier["pure_k1_information"]),10
            ),
            "physical_thinning_component_if_all_payable_source":round(
                float(frontier["gross_neutral_thinning"]),10
            )
        })
    assert len(rows)==9
    assert all(0 <= row["source_use_percent_at_zero_cost"] <= 46.477077
               for row in rows)
    return {"source_sensitivity_by_denial_weight":rows}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
