"""Exact maximum free K1 Prize-X information value across all lambda >= 0.

For every opponent observed hand, K1 Prize-X outcome and visible Beheeyem
first-packet route, action utility is affine in lambda. Hence K1 and K0
optimal expected utilities are continuous piecewise-affine. Their
difference attains its nonnegative finite maximum at lambda=0 or at a
positive rational pairwise utility crossing of either policy. Compute all
these exact candidates, then evaluate the winning information value.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations

from beheeyem_physical_tutor import exact_physical_tutor
from beheeyem_prize_packet import exact_prize_take
from beheeyem_supporter_reset import exact_supporter_reset
from beheeyem_opponent_self_target import (
    observed_hand_mass,own_target_after_reset,evaluate_own_target_policy
)
from beheeyem_opponent_self_target_frontier import policy_frontier
from beheeyem_opponent_k1_target import (
    prize_x_posterior,own_x_after_reset_k1,evaluate_k1_own_target_policy
)


@lru_cache(maxsize=None)
def exact_max_k1_information_gain(
    B: int,T: int,d: int,tutor: str,r: int,
    opposing_prizes_left: int,route_observed: bool
) -> dict:
    earned=6-opposing_prizes_left
    intact=exact_prize_take(B,T,d,tutor,r)
    judge=exact_supporter_reset(B,T,d,tutor,r,"Judge")
    ace_legal=opposing_prizes_left>6-r
    responses={"pass":intact,"judge":judge}
    if ace_legal:
        responses["ace"]=exact_supporter_reset(B,T,d,tutor,r,"Ace Trainer")
    first=intact[0]
    direct=exact_physical_tutor(B,T,d,tutor)[0]
    route_masses=(direct,first-direct)

    def own(action,x,z):
        return (Fraction(int(x>0)) if action=="pass" else
                own_x_after_reset_k1(z,earned,6 if action=="ace" else 4))

    def enemy(action,route):
        return (responses[action][3]/first if route==0 else
                responses[action][route]/route_masses[route-1])

    k0=policy_frontier(B,T,d,tutor,r,opposing_prizes_left,route_observed)
    candidates={a["lower"] for a in k0["intervals"]}
    possible_k1_crossings=0
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
                for z in range(5):
                    if not prize_x_posterior(x,earned,z):
                        continue
                    for route in ((1,2) if route_observed else (0,)):
                        if route and not route_masses[route-1]:
                            continue
                        for one,two in combinations(actions,2):
                            delta_enemy=enemy(one,route)-enemy(two,route)
                            if not delta_enemy:
                                continue
                            crossing=(own(one,x,z)-own(two,x,z))/delta_enemy
                            if crossing>0:
                                candidates.add(crossing)
                                possible_k1_crossings+=1

    def gain(lam):
        result_k1=evaluate_k1_own_target_policy(
            B,T,d,tutor,r,opposing_prizes_left,lam,route_observed
        )
        result_k0=evaluate_own_target_policy(
            B,T,d,tutor,r,opposing_prizes_left,lam,route_observed
        )
        return ((result_k1["own_target_ready"]-
                 lam*result_k1["beheeyem_joint_packet"]/first)
                -(result_k0["own_target_ready"]-
                  lam*result_k0["beheeyem_joint_packet"]/first))

    max_gain=Fraction(-1)
    maximizers=[]
    for candidate in sorted(candidates):
        value=gain(candidate)
        assert value>=0
        if value>max_gain:
            max_gain=value
            maximizers=[candidate]
        elif value==max_gain:
            maximizers.append(candidate)
    assert max_gain>=0
    if not maximizers:
        raise AssertionError("No candidate extrema")
    representative=min(maximizers)
    return {
        "candidate_crossings":len(candidates),
        "raw_positive_k1_intersections":possible_k1_crossings,
        "max_k1_utility_gain":max_gain,
        "maximizing_lambda":representative,
        "maximizing_lambda_values":tuple(maximizers),
        "gain_at_zero":gain(Fraction(0)),
        "gain_at_first":gain(Fraction(1)),
        "gain_at_ten":gain(Fraction(10)),
        "gain_at_hundred":gain(Fraction(100))
    }
