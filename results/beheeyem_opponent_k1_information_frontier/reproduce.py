"""Exact rational global maximum of opponent K1 information advantage."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_opponent_k1_information_frontier import (
    exact_max_k1_information_gain
)
from beheeyem_opponent_k1_target import evaluate_k1_own_target_policy
from beheeyem_opponent_self_target import evaluate_own_target_policy


def direct_gain(r,q,lam,public):
    a=evaluate_k1_own_target_policy(
        4,4,1,"computer_search",r,q,lam,public
    )
    b=evaluate_own_target_policy(
        4,4,1,"computer_search",r,q,lam,public
    )
    return ((a["own_target_ready"]-b["own_target_ready"])-
            lam*(a["beheeyem_joint_packet"]-
                 b["beheeyem_joint_packet"])/a["first_packet"])


def run():
    report=[]
    for r,q,public in (
        (0,6,False),(0,6,True),
        (1,6,False),(1,6,True),
        (2,6,False),(2,6,True),
        (2,5,True),(2,4,True)
    ):
        result=exact_max_k1_information_gain(
            4,4,1,"computer_search",r,q,public
        )
        peak=result["maximizing_lambda"]
        gain=result["max_k1_utility_gain"]
        assert gain>0
        assert gain==direct_gain(r,q,peak,public)
        assert result["gain_at_zero"]==direct_gain(
            r,q,Fraction(0),public
        )
        for weight in (Fraction(0),Fraction(1),Fraction(2),
                       Fraction(5),Fraction(10),Fraction(20),
                       Fraction(50),Fraction(100),Fraction(1000),
                       Fraction(10**6),
                       peak/2,peak*2,peak+Fraction(1,10000)):
            assert direct_gain(r,q,weight,public) <= gain
        report.append({
            "beheeyem_prizes":r,
            "opponent_prizes_remaining":q,
            "tutor_route_public":public,
            "candidate_breakpoints":result["candidate_crossings"],
            "max_k1_utility_gain":str(gain),
            "max_k1_utility_gain_float":round(float(gain),11),
            "optimal_weight":str(peak),
            "optimal_weight_float":round(float(peak),9),
            "gain_at_weight_10":round(float(result["gain_at_ten"]),11)
        })
    return {"configurations":len(report),"results":report}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
