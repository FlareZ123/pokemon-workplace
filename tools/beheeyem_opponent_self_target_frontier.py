"""Exact finite upper envelope of own-X versus Beheeyem-denial reply policies.

With each physical own-hand observation and (optionally) public first-packet
route, the available pass/Judge/Ace response has a linear utility in the
nonnegative lambda weighting packet denial. The response policy is
piecewise constant; all possible changes happen at rational pairwise
intersections. This module enumerates exact candidate intersections and
eliminates transitions invisible in the overall selected policy.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from functools import lru_cache

from beheeyem_physical_tutor import exact_physical_tutor
from beheeyem_prize_packet import exact_prize_take
from beheeyem_supporter_reset import exact_supporter_reset
from beheeyem_opponent_self_target import (
    observed_hand_mass,own_target_after_reset,
    evaluate_own_target_policy
)


@lru_cache(maxsize=None)
def policy_frontier(B: int,T: int,d: int,tutor: str,r: int,
                    opponent_prizes_left: int,public_route: bool) -> dict:
    """Return piecewise-constant interval tradeoffs for nonnegative lambda.

    Every finite interval is [lower, upper), understood as excluding points
    where exact ties change only secondary tie-breaking. The last upper
    bound is None (+infinity). Values are exact Fractions.
    """
    earned=6-opponent_prizes_left
    intact=exact_prize_take(B,T,d,tutor,r)
    judge=exact_supporter_reset(B,T,d,tutor,r,"Judge")
    ace_legal=opponent_prizes_left>6-r
    responses={"pass":intact,"judge":judge}
    if ace_legal:
        responses["ace"]=exact_supporter_reset(
            B,T,d,tutor,r,"Ace Trainer"
        )
    first=intact[0]
    direct=exact_physical_tutor(B,T,d,tutor)[0]
    route_masses=(direct,first-direct)

    def own(action: str,x: int) -> Fraction:
        return (Fraction(int(x>0)) if action=="pass" else
                own_target_after_reset(x,earned,6 if action=="ace" else 4))

    def enemy(action: str,route: int) -> Fraction:
        return (responses[action][3]/first if route==0 else
                responses[action][route]/route_masses[route-1])

    positive={Fraction(0)}
    meaningful_state=0
    for a in (0,1):
        for j in (0,1):
            for x in range(5):
                if not observed_hand_mass(a,j,x,earned):
                    continue
                actions=["pass"]
                if j:
                    actions.append("judge")
                if a and ace_legal:
                    actions.append("ace")
                for route in ((1,2) if public_route else (0,)):
                    if route and route_masses[route-1]==0:
                        continue
                    meaningful_state+=1
                    for one,two in combinations(actions,2):
                        denom=enemy(one,route)-enemy(two,route)
                        if not denom:
                            continue
                        crossing=(own(one,x)-own(two,x))/denom
                        if crossing>0:
                            positive.add(crossing)
    cuts=sorted(positive)
    intervals=[]
    for i,lower in enumerate(cuts):
        upper=cuts[i+1] if i+1<len(cuts) else None
        probe=(lower+upper)/2 if upper is not None else lower+1
        model=evaluate_own_target_policy(
            B,T,d,tutor,r,opponent_prizes_left,probe,public_route
        )
        state=(
            model["own_target_ready"],
            model["beheeyem_joint_packet"],
            model["pass_fraction"],
            model["judge_fraction"],
            model["ace_fraction"]
        )
        if intervals and intervals[-1]["state"]==state:
            intervals[-1]["upper"]=upper
        else:
            intervals.append({
                "lower":lower,"upper":upper,"state":state
            })
    assert intervals[0]["lower"]==0 and intervals[-1]["upper"] is None
    assert all(
        intervals[i]["upper"]==intervals[i+1]["lower"]
        for i in range(len(intervals)-1)
    )
    for i in range(len(intervals)-1):
        low=intervals[i]["state"]
        high=intervals[i+1]["state"]
        assert high[0]<=low[0]  # own-X objective weakens with lambda.
        assert high[1]<=low[1]  # Beheeyem packet risk also drops.
    return {
        "candidate_crossings":len(cuts)-1,
        "parameter_state_cases":meaningful_state,
        "true_intervals":len(intervals),
        "intervals":intervals
    }
