"""Opposing Supporter decisions with both-side limited card access and own target.

Opponent's 60-card hypothetical deck has 12 Basics, 4 Ace Trainer, 4 Judge,
4 distinct own attack-target cards X, and 36 neutral filler. Its valid
Basic-containing 7-card opener, k=2 subsequent deck draws and s earned
Prizes comprise an exchangeable observed hand of size h=7+k+s, conditioned
on opener Basic validity. Remaining original Prizes are hidden (K0).
A Supporter reset physically discards that Supporter, shuffles its owner's
other hand cards into the deck, and redraws six (Ace) or four (Judge).

The opponent chooses its Supporter using its OWN observed hand X/Ace/Judge
counts, public Beheeyem first-packet tutor-use route if enabled, and Prize
counts. It trades own probability of holding X after response against
lambda times the conditional Beheeyem second-packet success chance.
This is a deliberately narrow utility, not full match win probability.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import choose,exact_physical_tutor
from beheeyem_prize_packet import exact_prize_take
from beheeyem_supporter_reset import exact_supporter_reset


@lru_cache(maxsize=None)
def observed_hand_mass(ace: int,judge: int,target: int,earned: int,
                       basics: int = 12,ace_total: int = 4,
                       judge_total: int = 4,target_total: int = 4,
                       draws: int = 2) -> Fraction:
    """Exactly P(observed counts | first 7 of 7+draws+earned have Basic).

    The later natural draws and uniformly awarded original Prizes together
    form an unordered sample independent of labels in the original opener.
    """
    if not (0 <= earned <= 6 and 0 <= draws <= 47):
        raise ValueError("Invalid opposing draw/Prize counts")
    h=7+draws+earned
    filler=60-basics-ace_total-judge_total-target_total
    valid_openers=comb(60,7)-choose(60-basics,7)
    denominator=comb(60,h)*comb(h,7)*valid_openers
    numerator=0
    for basic in range(min(basics,h)+1):
        f=h-basic-ace-judge-target
        ways=(choose(basics,basic)*choose(ace_total,ace)*
              choose(judge_total,judge)*choose(target_total,target)*
              choose(filler,f))
        if not ways:
            continue
        number_valid_first7=comb(h,7)-choose(h-basic,7)
        numerator+=ways*number_valid_first7*comb(60,7)
    return Fraction(numerator,denominator)


@lru_cache(maxsize=None)
def own_target_after_reset(held_target: int,earned: int,draw_quota: int,
                           basics: int=12,ace_total: int=4,
                           judge_total: int=4,target_total: int=4,
                           draws: int=2) -> Fraction:
    """K0 expectation for at least one own target after full-hand reset.

    Opposing player knows held-target count; original remaining Prize cards
    are uninspected and exchangeable over the other 60-h identities.
    The played Supporter is distinct from X, removed before shuffling.
    """
    h=7+draws+earned
    prize_left=6-earned
    unseen=60-h
    deck_after_shuffle=60-prize_left-1
    if not (0 <= held_target <= target_total and
            0 <= draw_quota <= deck_after_shuffle):
        raise ValueError("Invalid target or replacement draw count")

    probability=Fraction()
    for x_prized in range(target_total-held_target+1):
        ways=(choose(target_total-held_target,x_prized)*
              choose(unseen-(target_total-held_target),
                     prize_left-x_prized))
        if not ways:
            continue
        unprized_target=target_total-x_prized
        miss=Fraction(
            choose(deck_after_shuffle-unprized_target,draw_quota),
            comb(deck_after_shuffle,draw_quota)
        )
        probability+=Fraction(ways,comb(unseen,prize_left))*(1-miss)
    return probability


@lru_cache(maxsize=None)
def evaluate_own_target_policy(
    B: int,T: int,d: int,tutor: str,r: int,
    opposing_prizes_remaining: int,
    lambda_weight: Fraction=Fraction(1),
    route_observed: bool=False
) -> dict[str,Fraction]:
    """Choose response maximizing P(own X ready) - lambda*P(next Beheeyem).

    Outputs own target rate conditioned on first attack; Beheeyem joint
    next-packet rate within the fixed three-Basic opening model.
    """
    if not 0 <= opposing_prizes_remaining <= 6:
        raise ValueError("Invalid opponent Prize count")
    if lambda_weight < 0:
        raise ValueError("Nonnegative lambda required")
    earned=6-opposing_prizes_remaining
    direct_first=exact_physical_tutor(B,T,d,tutor)[0]
    intact=exact_prize_take(B,T,d,tutor,r)
    judge=exact_supporter_reset(B,T,d,tutor,r,"Judge")
    ace_legal=opposing_prizes_remaining > 6-r
    ace=exact_supporter_reset(B,T,d,tutor,r,"Ace Trainer") if ace_legal else None
    assert intact[0]==judge[0] and direct_first<=intact[0]
    assert ace is None or ace[0]==intact[0]
    first=intact[0]
    branch_grounds=(direct_first,first-direct_first)
    assert sum(branch_grounds)==first
    all_responses={"pass":intact,"judge":judge}
    if ace is not None:
        all_responses["ace"]=ace

    def choose_action(actions: list[str], held_x: int,route: int) -> str:
        def payoff(action: str) -> tuple[Fraction,Fraction]:
            own=(Fraction(int(held_x>0)) if action=="pass"
                 else own_target_after_reset(
                     held_x,earned,6 if action=="ace" else 4
                 ))
            response=all_responses[action]
            opp=(response[3]/first if route==0
                 else response[route]/branch_grounds[route-1])
            return (own-lambda_weight*opp,own)
        # Use self readiness as secondary tie-break, then pass over reset.
        return max(actions,key=lambda action:(*payoff(action),
                                                int(action=="pass")))

    own_ready=joint_second=Fraction()
    action_masses={name:Fraction() for name in ("pass","judge","ace")}
    observed_sum=Fraction()
    for a in range(5):
        for j in range(5):
            for x in range(5):
                prob=observed_hand_mass(a,j,x,earned)
                if not prob:
                    continue
                observed_sum+=prob
                actions=["pass"]
                if j:
                    actions.append("judge")
                if a and ace_legal:
                    actions.append("ace")
                for route,route_weight in ((1,branch_grounds[0]),
                                           (2,branch_grounds[1])):
                    if not route_weight:
                        continue
                    action=choose_action(actions,x,
                                         route if route_observed else 0)
                    w=prob*route_weight/first
                    action_masses[action]+=w
                    own_ready+=w*(Fraction(int(x>0))
                        if action=="pass" else
                        own_target_after_reset(x,earned,
                                               6 if action=="ace" else 4))
                    joint_second+=prob*all_responses[action][route]
    assert observed_sum==1
    assert sum(action_masses.values())==1
    assert joint_second<=first
    return {
        "first_packet":first,
        "own_target_ready":own_ready,
        "beheeyem_joint_packet":joint_second,
        "pass_fraction":action_masses["pass"],
        "judge_fraction":action_masses["judge"],
        "ace_fraction":action_masses["ace"]
    }
