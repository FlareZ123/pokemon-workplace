"""Sequential early Ultra Ball K1 policy with UNKNOWN future KO Prize reward.

The existing paid-K1 response model conditions the early search decision on
a future r=0,1,2 Prize count, which the opponent has not yet observed.
This solver instead accepts an exogenous rational prior (p0,p1,p2).
The early Ultra Ball decision only sees its current hand; the later
Judge/Ace/no-reset choice sees realized r, the public first tutor route
if enabled, reply draw, and X Prize count if K1 was acquired.

Actual KO feasibility, matchup-specific reward likelihood, and effects of
early Item play on board remain outside the model. This fixes the tactical
information-timing constraint, conditional on the chosen r prior.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import choose,exact_physical_tutor
from beheeyem_prize_packet import exact_prize_take
from beheeyem_supporter_reset import exact_supporter_reset
from beheeyem_paid_k1_policy import initial_prelock_masses,exact_early_search_policy


@lru_cache(maxsize=None)
def uncertain_reward_early_search(
    reward_prior: tuple[Fraction,Fraction,Fraction],
    lambda_weight: Fraction=Fraction(10),tau: Fraction=Fraction(),
    k_pre: int=2,k_reply: int=1,route_observed: bool=True,
    B: int=4,T: int=4,d: int=1,tutor: str="computer_search"
) -> dict[str,Fraction]:
    if not (len(reward_prior)==3 and all(p>=0 for p in reward_prior)
            and sum(reward_prior)==1 and lambda_weight>=0 and tau>=0
            and 0<=k_pre<=5 and 0<=k_reply<=5):
        raise ValueError("Invalid three-Prize reward prior or cost")
    cases={}
    direct_first=exact_physical_tutor(B,T,d,tutor)[0]
    for r,prior in enumerate(reward_prior):
        if prior==0:
            continue
        intact=exact_prize_take(B,T,d,tutor,r)
        responses={
            "pass":intact,
            "judge":exact_supporter_reset(B,T,d,tutor,r,"Judge")
        }
        if r>0: # Opponent q=6: Ace legal iff r>0.
            responses["ace"]=exact_supporter_reset(
                B,T,d,tutor,r,"Ace Trainer"
            )
        first=intact[0]
        cases[r]=(prior,responses,(
            (1,direct_first/first),(2,(first-direct_first)/first)
        ))

    @lru_cache(maxsize=None)
    def value_reply(r,a,j,x,spent,k1):
        _,responses,branches=cases[r]
        available=["pass"]
        if j:
            available.append("judge")
        if a and r>0:
            available.append("ace")
        N=50 if spent else 53
        h=7+k_pre+k_reply
        unseen=60-h
        possible=[]
        for z in range(5):
            ways=(choose(4-x,z)*choose(unseen-(4-x),6-z))
            if ways:
                possible.append((z,Fraction(ways,comb(unseen,6))))
        assert sum(w for z,w in possible)==1

        def own(action,z):
            if action=="pass":
                return Fraction(int(x>0))
            n=6 if action=="ace" else 4
            return 1-Fraction(choose(N-(4-z),n),comb(N,n))

        utility=Fraction()
        for route,p_route in branches:
            if not p_route:
                continue
            def packet(action):
                response=responses[action]
                if not route_observed:
                    return response[3]/response[0]
                return response[route]/(
                    direct_first if route==1
                    else response[0]-direct_first
                )

            if k1:
                v=sum(
                    w*max(
                        own(action,z)-lambda_weight*packet(action)
                        for action in available
                    ) for z,w in possible
                )
            else:
                v=max(
                    sum(w*own(action,z) for z,w in possible)
                    -lambda_weight*packet(action)
                    for action in available
                )
            utility+=p_route*v
        return utility

    @lru_cache(maxsize=None)
    def future(r,a,j,x,spent,k1):
        total=Fraction()
        other=51-(4-a)-(4-j)-(4-x)
        for da in range(min(4-a,k_reply)+1):
            for dj in range(min(4-j,k_reply-da)+1):
                for dx in range(min(4-x,k_reply-da-dj)+1):
                    do=k_reply-da-dj-dx
                    ways=(choose(4-a,da)*choose(4-j,dj)*
                          choose(4-x,dx)*choose(other,do))
                    if ways:
                        total+=Fraction(ways,comb(51,k_reply))*value_reply(
                            r,a+da,j+dj,x+dx,spent,k1
                        )
        return total

    baseline=optimal=forced=thin_only=pure_k1=Fraction()
    paid_available=paid_used=Fraction()
    for (a,j,x,payable),mass in initial_prelock_masses(k_pre).items():
        no=sum(pr*future(r,a,j,x,False,False)
               for r,(pr,_,_) in cases.items())
        baseline+=mass*no
        if not payable:
            optimal+=mass*no
            forced+=mass*no
            thin_only+=mass*no
            continue
        paid_available+=mass
        paid_blind=sum(pr*future(r,a,j,x,True,False)
                       for r,(pr,_,_) in cases.items())
        paid_k1=sum(pr*future(r,a,j,x,True,True)
                    for r,(pr,_,_) in cases.items())
        assert paid_k1>=paid_blind>=no
        pure_k1+=mass*(paid_k1-paid_blind)
        thin_only+=mass*paid_blind
        forced+=mass*(paid_k1-tau)
        if paid_k1-tau>no:
            optimal+=mass*(paid_k1-tau)
            paid_used+=mass
        else:
            optimal+=mass*no

    clairvoyant=sum(
        prior*exact_early_search_policy(
            B=B,T=T,d=d,tutor=tutor,r=r,
            lambda_weight=lambda_weight,tau=tau,
            k_pre=k_pre,k_reply=k_reply,route_observed=route_observed
        )["optimal_with_optional_search_utility"]
        for r,prior in enumerate(reward_prior) if prior
    )
    assert baseline<=optimal<=clairvoyant
    return {
        "reward_prior":reward_prior,
        "prelock_paid_search_available":paid_available,
        "prelock_paid_search_used":paid_used,
        "baseline_no_early_search":baseline,
        "prior_aware_optimum":optimal,
        "incremental_value":optimal-baseline,
        "clairvoyant_future_reward_optimum":clairvoyant,
        "value_of_future_reward_information":clairvoyant-optimal,
        "unconditionally_paid_thinning_component":thin_only-baseline,
        "unconditionally_paid_K1_component":pure_k1,
        "forced_paid_search_value":forced
    }
