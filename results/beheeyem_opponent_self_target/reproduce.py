"""Exact K0 opponent own-X access and Beheeyem reply objective regression."""
from fractions import Fraction
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))
from beheeyem_opponent_self_target import (
    evaluate_own_target_policy,observed_hand_mass,own_target_after_reset
)
from beheeyem_opponent_supporter_access import (
    probability_not_seen,optimal_reply_with_access
)


def run():
    for earned in range(3):
        states=[
            (a,j,x,observed_hand_mass(a,j,x,earned))
            for a in range(5) for j in range(5) for x in range(5)
        ]
        assert sum(w for _,_,_,w in states) == 1
        for idx in (0,1,2):
            present=sum(
                w for a,j,x,w in states if (a,j,x)[idx]>0
            )
            assert present==1-probability_not_seen(12,4,2,earned)
        for x in range(5):
            small=own_target_after_reset(x,earned,4)
            large=own_target_after_reset(x,earned,6)
            assert 0 < small < large < 1

    rows=[]
    checks=0
    for r,q in ((0,6),(1,6),(1,5),(2,6),(2,5),(2,4)):
        for lam in (Fraction(0),Fraction(1),Fraction(10),
                    Fraction(100),Fraction(10**6)):
            hidden=evaluate_own_target_policy(
                4,4,1,"computer_search",r,q,lam,False
            )
            public=evaluate_own_target_policy(
                4,4,1,"computer_search",r,q,lam,True
            )
            objective=lambda v: v["own_target_ready"]-(
                lam*v["beheeyem_joint_packet"]/v["first_packet"]
            )
            assert objective(public) >= objective(hidden)
            assert public["first_packet"]==hidden["first_packet"]
            assert sum(public[k] for k in (
                "pass_fraction","judge_fraction","ace_fraction"
            )) == 1
            assert 0 <= public["own_target_ready"] <= 1
            assert public["beheeyem_joint_packet"] <= public["first_packet"]
            if lam==10**6:
                baseline=optimal_reply_with_access(
                    4,4,1,"computer_search",r,q,12,4,4,2
                )
                assert (
                    hidden["beheeyem_joint_packet"]
                    == baseline["optimal_aggregate_joint"]
                )
                assert (
                    public["beheeyem_joint_packet"]
                    == baseline["optimal_public_tutor_signal_joint"]
                )
            checks+=2
            rows.append({
                "beheeyem_awarded":r,
                "opponent_prizes_left":q,
                "lambda":str(lam),
                "observes_first_tutor":True,
                "target_ready_percent":round(
                    100*float(public["own_target_ready"]),7
                ),
                "beheeyem_joint_percent":round(
                    100*float(public["beheeyem_joint_packet"]),7
                ),
                "respond_pass_percent":round(
                    100*float(public["pass_fraction"]),7
                ),
                "respond_judge_percent":round(
                    100*float(public["judge_fraction"]),7
                ),
                "respond_ace_percent":round(
                    100*float(public["ace_fraction"]),7
                )
            })
    assert checks==60
    return {"model_settings_checked":checks,"results":rows}


if __name__=="__main__":
    print(json.dumps(run(),indent=2))
