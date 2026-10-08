"""Independent physical labeled Prize oracle for Nest Ball -> two Tool holders."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations,product
from math import comb
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))

from secret_box_gnh_tool_pipeline import KINDS,counts
from secret_box_k0_payment import evaluate_hidden_prize_payment
from secret_box_k0_bench_bootstrap import baseline_holder_bridge
from secret_box_k0_opening_mix import average_box_payment_policy
from secret_box_nest_ball_k0 import (
    exact_nest_payment_policy,nest_ball_opening_mixture,
)


def brute(hidden_hand, unknown, *, visible_basics, unknown_basics, prize_count):
    hand=tuple((k,i,"hand") for k,n in zip(KINDS,hidden_hand) for i in range(n))
    draw=[]
    for k,n in zip(KINDS,unknown):
        if k=="P":
            draw += [("Basic",j,"deck") for j in range(unknown_basics)]
            draw += [("P",j,"deck") for j in range(n-unknown_basics)]
        else:
            draw += [(k,j,"deck") for j in range(n)]

    payments=tuple(combinations((c for c in hand if c[0]!="P"),3))
    target={"A","B","S","E"}

    def reached(h,holders):
        return holders>=2 and target.issubset({c[0] for c in h})

    def search(pool,requirements):
        options=[(None,)+tuple(c for c in pool if c[0] in accepted)
                 for accepted in requirements]
        for selected in product(*options):
            chosen=tuple(c for c in selected if c is not None)
            if len(set(chosen))!=len(chosen):
                continue
            used=set(chosen)
            yield chosen,tuple(c for c in pool if c not in used)

    def continuation(held,deck):
        for picks,after_box in search(
            deck,({"I"},{"A","B"},{"G"},{"S"})
        ):
            received=held+picks
            preps=[(received,after_box,visible_basics)]
            if visible_basics<2:
                for item in (c for c in received if c[0]=="I"):
                    for basic in (c for c in after_box if c[0]=="Basic"):
                        reduced=tuple(c for c in received if c!=item)
                        reduced_deck=tuple(c for c in after_box if c!=basic)
                        preps.append((reduced,reduced_deck,visible_basics+1))
            for prep,post_nest,holders in preps:
                if reached(prep,holders):
                    return True
                for g in (c for c in prep if c[0]=="G"):
                    spent_g=tuple(c for c in prep if c!=g)
                    for newer,_ in search(post_nest,({"S"},)):
                        if reached(spent_g+newer,holders):
                            return True
                    for cost in combinations(
                        (c for c in spent_g if c[0]!="P"),2
                    ):
                        spent=set(cost)
                        remaining=tuple(c for c in spent_g if c not in spent)
                        for newer,_ in search(
                            post_nest,({"S"},{"A","B"},{"E"})
                        ):
                            if reached(remaining+newer,holders):
                                return True
        return False

    win_counts=[0]*len(payments)
    know=0
    for prize in combinations(draw,prize_count):
        pr_set=set(prize)
        deck=tuple(c for c in draw if c not in pr_set)
        flags=[]
        for j,cost in enumerate(payments):
            cost_set=set(cost)
            paid=tuple(c for c in hand if c not in cost_set)
            success=continuation(paid,deck)
            flags.append(success)
            win_counts[j]+=success
        know+=any(flags)
    den=comb(len(draw),prize_count)
    return (Fraction(know,den),
            Fraction(max(win_counts,default=0),den))


def main():
    hand=counts(D=2,A=1,G=1,S=1,P=1)
    checked=0
    for items,stadiums,extra_basics,extra_g in product(
        (0,1),(1,2),(0,1,2),(0,1)
    ):
        unknown=counts(
            D=2,I=items,A=1,B=1,G=extra_g,S=stadiums,E=1,P=3
        )
        for h_basics in (1,2):
            fast=exact_nest_payment_policy(
                hand,unknown,visible_basics=h_basics,
                unknown_basics=extra_basics,prize_count=2,
            )
            literal=brute(
                hand,unknown,visible_basics=h_basics,
                unknown_basics=extra_basics,prize_count=2,
            )
            assert (fast.clairvoyant_success,fast.k0_success)==literal,(
                items,stadiums,extra_basics,extra_g,h_basics,fast,literal
            )
            if h_basics>=2:
                ordinary=evaluate_hidden_prize_payment(
                    hand,unknown,prize_count=2
                )
                assert (fast.k0_success,fast.clairvoyant_success)==(
                    ordinary.k0_success,ordinary.clairvoyant_success
                )
            checked+=1
    assert checked==48
    print("Independent physically labeled hidden Basic/Prize oracle:",checked,"PASS")

    toy=counts(D=20,I=1,A=2,B=1,G=2,S=2,E=1,P=30)
    result=nest_ball_opening_mixture(toy,total_basic_starters=12)
    restricted=baseline_holder_bridge()
    hand_only=average_box_payment_policy(toy,basic_starters=12)
    assert restricted.k0_joint_success <= result.k0_success <= hand_only.k0_success
    assert restricted.k1_joint_success <= result.k1_success <= hand_only.clairvoyant_success
    assert result.incremental_k0_vs_two_visible > 0
    assert result.incremental_k1_vs_two_visible > 0
    assert result.information_gap >= 0
    assert result.visible_states == 782, result.visible_states
    print("Baseline strict two-holder K0:",restricted.k0_joint_success,
          float(restricted.k0_joint_success))
    print("With Box-searched Nest Ball K0:",result.k0_success,float(result.k0_success))
    print("With Box-searched Nest Ball K1:",result.k1_success,float(result.k1_success))
    print("Nest Ball incremental K0:",result.incremental_k0_vs_two_visible,
          float(result.incremental_k0_vs_two_visible))
    print("Information gap:",result.information_gap,float(result.information_gap))
    print("One visible holder state probability:",result.one_holder_probability,
          float(result.one_holder_probability))
    print("Visible typed state count:",result.visible_states)
    print("ALL TESTS PASSED")


if __name__=="__main__":
    main()
