"""Validate early K1 purchase without knowing future first-attack Prize award."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_paid_k1_reward_prior import uncertain_reward_early_search
from beheeyem_paid_k1_policy import exact_early_search_policy


def run():
    checks=0
    for r in range(3):
        prior=tuple(Fraction(int(i==r)) for i in range(3))
        for lam in (0,10,100):
            for tau in (Fraction(),Fraction(1,100)):
                exact=uncertain_reward_early_search(
                    prior,Fraction(lam),tau
                )
                earlier=exact_early_search_policy(
                    r=r,lambda_weight=Fraction(lam),tau=tau
                )
                assert exact["prior_aware_optimum"]==(
                    earlier["optimal_with_optional_search_utility"]
                )
                assert exact["baseline_no_early_search"]==(
                    earlier["baseline_no_search_utility"]
                )
                assert exact["prelock_paid_search_used"]==(
                    earlier["early_search_chosen_mass"]
                )
                assert exact["value_of_future_reward_information"]==0
                checks+=1

    rows=[]
    mixed=(
        (Fraction(1,3),Fraction(1,3),Fraction(1,3)),
        (Fraction(1,2),Fraction(1,2),Fraction()),
        (Fraction(),Fraction(1,2),Fraction(1,2)),
        (Fraction(1,10),Fraction(8,10),Fraction(1,10))
    )
    for prior in mixed:
        previous_gain=previous_used=None
        for tau in (
            Fraction(),Fraction(1,1000),
            Fraction(1,100),Fraction(1,10)
        ):
            z=uncertain_reward_early_search(
                prior,Fraction(10),tau
            )
            assert (
                z["prior_aware_optimum"]
                <= z["clairvoyant_future_reward_optimum"]
            )
            assert z["incremental_value"]>=0
            assert z["value_of_future_reward_information"]>=0
            if previous_gain is not None:
                assert z["incremental_value"]<=previous_gain
                assert z["prelock_paid_search_used"]<=previous_used
            previous_gain=z["incremental_value"]
            previous_used=z["prelock_paid_search_used"]
            rows.append({
                "prior_r0_r1_r2":[str(q) for q in prior],
                "cost_tau":str(tau),
                "prelock_K1_used_percent":round(
                    100*float(z["prelock_paid_search_used"]),8
                ),
                "gain_above_no_search":round(
                    float(z["incremental_value"]),11
                ),
                "clairvoyant_reward_advantage":round(
                    float(z["value_of_future_reward_information"]),11
                ),
                "pure_K1_component_if_always_paid":round(
                    float(z["unconditionally_paid_K1_component"]),11
                ),
                "pure_thinning_component_if_always_paid":round(
                    float(z["unconditionally_paid_thinning_component"]),11
                )
            })
            checks+=1
    assert checks==34
    return {"checks":checks,"mixed_reward_policies":rows}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
