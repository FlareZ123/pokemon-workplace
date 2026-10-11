"""K1 opponent Prize knowledge changes its optimal hand-reset Supporter choice.

A hypothetical four-copy own target X can be in the opponent's current hand,
remaining deck or remaining face-down Prize cards. K0 knows only the hand's
X count. After a genuine deck search, K1 infers the remaining X Prize count,
allowing conditional prediction of any Judge/Ace full-deck reshuffle.
The information itself is granted for free in this controlled value-of-
information upper-bound; source/cost for inspecting deck is not modeled.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import choose,exact_physical_tutor
from beheeyem_prize_packet import exact_prize_take
from beheeyem_supporter_reset import exact_supporter_reset
from beheeyem_opponent_self_target import (
    observed_hand_mass,evaluate_own_target_policy,
    own_target_after_reset
)


@lru_cache(maxsize=None)
def prize_x_posterior(x_held: int,earned: int,z_prized: int,
                      total_x: int=4,draws: int=2) -> Fraction:
    """Probability z copies of X remain Prized given h observed cards."""
    h=7+draws+earned
    unseen=60-h
    pr=6-earned
    return Fraction(
        choose(total_x-x_held,z_prized)*
        choose(unseen-(total_x-x_held),pr-z_prized),
        comb(unseen,pr)
    )


@lru_cache(maxsize=None)
def own_x_after_reset_k1(z_prized: int,earned: int,quota: int,
                         total_x: int=4) -> Fraction:
    """K1 target redraw probability after the played Supporter is discarded."""
    N=60-(6-earned)-1
    available=total_x-z_prized
    if not (0 <= z_prized <= total_x and 0 <= quota <= N):
        raise ValueError("Invalid Prize X count or replacement quota")
    return 1-Fraction(choose(N-available,quota),comb(N,quota))


@lru_cache(maxsize=None)
def evaluate_k1_own_target_policy(
    B: int,T: int,d: int,tutor: str,r: int,opposing_prizes_left: int,
    lambda_weight: Fraction=Fraction(1),route_observed: bool=False
) -> dict[str,Fraction]:
    """Opponent hand+Prize-X-aware policy, averaged over physical K1 states.

    Returns own X readiness conditional first packet and Beheeyem joint
    two-packet rate under optimized legal Supporter/no-reset response.
    """
    if not (0 <= opposing_prizes_left <= 6 and lambda_weight >= 0):
        raise ValueError("Invalid opposing Prize count or lambda")
    earned=6-opposing_prizes_left
    intact=exact_prize_take(B,T,d,tutor,r)
    judge=exact_supporter_reset(B,T,d,tutor,r,"Judge")
    ace_legal=opposing_prizes_left > 6-r
    ace=exact_supporter_reset(B,T,d,tutor,r,"Ace Trainer") if ace_legal else None
    direct_first=exact_physical_tutor(B,T,d,tutor)[0]
    first=intact[0]
    branch_masses=(direct_first,first-direct_first)
    responses={"pass":intact,"judge":judge}
    if ace_legal:
        responses["ace"]=ace
    assert all(v[0]==first for v in responses.values())

    def choose_action(actions,x,z,route) -> str:
        def value(action):
            own=(Fraction(int(x>0)) if action=="pass" else
                 own_x_after_reset_k1(
                     z,earned,6 if action=="ace" else 4
                 ))
            enemy=(responses[action][3]/first if route==0 else
                   responses[action][route]/branch_masses[route-1])
            return (own-lambda_weight*enemy,own,int(action=="pass"))
        return max(actions,key=value)

    own_ready=second_joint=Fraction()
    actions_taken={name:Fraction() for name in ("pass","judge","ace")}
    mass=Fraction()
    for a in range(5):
        for j in range(5):
            for x in range(5):
                hand_weight=observed_hand_mass(a,j,x,earned)
                if not hand_weight:
                    continue
                actions=["pass"]
                if j:
                    actions.append("judge")
                if a and ace_legal:
                    actions.append("ace")
                for z in range(5):
                    pz=prize_x_posterior(x,earned,z)
                    if not pz:
                        continue
                    state_weight=hand_weight*pz
                    mass+=state_weight
                    for route,branch in ((1,branch_masses[0]),
                                         (2,branch_masses[1])):
                        if not branch:
                            continue
                        action=choose_action(
                            actions,x,z,route if route_observed else 0
                        )
                        w=state_weight*branch/first
                        actions_taken[action]+=w
                        own_ready+=w*(Fraction(int(x>0))
                            if action=="pass" else
                            own_x_after_reset_k1(
                                z,earned,6 if action=="ace" else 4
                            ))
                        second_joint+=state_weight*responses[action][route]
    assert mass==1
    assert sum(actions_taken.values())==1

    k0=evaluate_own_target_policy(
        B,T,d,tutor,r,opposing_prizes_left,lambda_weight,route_observed
    )
    k1_utility=own_ready-lambda_weight*second_joint/first
    k0_utility=(k0["own_target_ready"]-
                lambda_weight*k0["beheeyem_joint_packet"]/first)
    assert k1_utility>=k0_utility  # free information cannot hurt
    return {
        "first_packet":first,
        "own_target_ready":own_ready,
        "beheeyem_joint_packet":second_joint,
        "pass_fraction":actions_taken["pass"],
        "judge_fraction":actions_taken["judge"],
        "ace_fraction":actions_taken["ace"],
        "k1_utility_gain":k1_utility-k0_utility
    }
