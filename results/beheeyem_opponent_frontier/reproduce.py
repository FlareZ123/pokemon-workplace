"""Exact breakpoint enumeration and non-dominated outcome checks."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_opponent_self_target_frontier import policy_frontier
from beheeyem_opponent_self_target import evaluate_own_target_policy


def run():
    rows=[]
    for r,q in ((0,6),(1,6),(2,6),(2,5),(2,4)):
        for public in (False,True):
            z=policy_frontier(4,4,1,"computer_search",r,q,public)
            levels=z["intervals"]
            assert z["true_intervals"]>=2
            for i,entry in enumerate(levels):
                lo,hi=entry["lower"],entry["upper"]
                probe=(lo+hi)/2 if hi is not None else lo+1
                expected=evaluate_own_target_policy(
                    4,4,1,"computer_search",r,q,probe,public
                )
                state=(
                    expected["own_target_ready"],
                    expected["beheeyem_joint_packet"],
                    expected["pass_fraction"],
                    expected["judge_fraction"],
                    expected["ace_fraction"]
                )
                assert state==entry["state"]
                if i+1<len(levels):
                    assert levels[i+1]["lower"]==entry["upper"]
            end=levels[-1]
            assert end["state"]==tuple(
                evaluate_own_target_policy(
                    4,4,1,"computer_search",r,q,Fraction(10**12),public
                )[key] for key in (
                    "own_target_ready","beheeyem_joint_packet",
                    "pass_fraction","judge_fraction","ace_fraction"
                )
            )
            rows.append({
                "r_beheeyem":r,"q_opponent_remaining":q,
                "public_route":public,
                "candidate_pairwise_crossings":z["candidate_crossings"],
                "true_tradeoff_segments":z["true_intervals"],
                "first_nonzero_switch_lambda":(
                    str(levels[1]["lower"]) if len(levels)>1 else None
                ),
                "first_switch_float":(
                    round(float(levels[1]["lower"]),8)
                    if len(levels)>1 else None
                ),
                "final_switch_float":(
                    round(float(levels[-1]["lower"]),8)
                    if len(levels)>1 else None
                )
            })
    return {"scenarios":len(rows),"frontier_structure":rows}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
