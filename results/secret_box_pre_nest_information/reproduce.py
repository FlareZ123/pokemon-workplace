"""SFT: prior Nest Ball deck inspection versus Box-first K0 payment."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations,product
from math import comb
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))

from secret_box_gnh_tool_pipeline import KINDS,counts
from secret_box_pre_nest_information import optimal_pre_nest_choice
from secret_box_nest_ball_k0 import exact_nest_payment_policy


def independent_nest_first(hand_counts,unknown_counts, *,
                           unknown_basics,prizes):
    """Label all distinct copies, enumerate hidden Prizes and post-peek payments."""
    hand=tuple((k,i,"hand") for k,n in zip(KINDS,hand_counts) for i in range(n))
    pool=[]
    for k,n in zip(KINDS,unknown_counts):
        if k=="P":
            pool.extend(("Basic",i,"deck") for i in range(unknown_basics))
            pool.extend(("P",i,"deck") for i in range(n-unknown_basics))
        else:
            pool.extend((k,i,"deck") for i in range(n))
    candidates=[c for c in hand if c[0]=="I"]
    assert candidates
    spent_nest=candidates[0]
    post_nest_hand=tuple(c for c in hand if c!=spent_nest)
    needed={"A","B","S","E"}

    def search(deck,labels):
        options=[(None,) + tuple(c for c in deck if c[0] in kind)
                 for kind in labels]
        for selections in product(*options):
            selected=tuple(c for c in selections if c is not None)
            if len(set(selected))!=len(selected):
                continue
            chosen=set(selected)
            yield selected,tuple(c for c in deck if c not in chosen)

    def goal(hand):
        return needed.issubset({c[0] for c in hand})

    def continuation(prepay,deck):
        for box_picks,rest in search(
            deck,({"I"},{"A","B"},{"G"},{"S"})
        ):
            after_box=prepay+box_picks
            if goal(after_box):
                return True
            for g in (c for c in after_box if c[0]=="G"):
                after_g=tuple(c for c in after_box if c!=g)
                for picks,_ in search(rest,({"S"},)):
                    if goal(after_g+picks):
                        return True
                for cost in combinations(
                    (c for c in after_g if c[0]!="P"),2
                ):
                    spent=set(cost)
                    leftovers=tuple(c for c in after_g if c not in spent)
                    for picks,_ in search(
                        rest,({"S"},{"A","B"},{"E"})
                    ):
                        if goal(leftovers+picks):
                            return True
        return False

    win=0
    for prize in combinations(pool,prizes):
        prize_set=set(prize)
        deck=tuple(c for c in pool if c not in prize_set)
        # The already-held Nest Ball is played before Box. Its first
        # successful search reveals the deck, allowing world-specific Box
        # payments. The searched Basic is physically removed to the Bench.
        basics=[c for c in deck if c[0]=="Basic"]
        if not basics:
            continue
        searched_basic=basics[0]
        post_nest_deck=tuple(c for c in deck if c!=searched_basic)
        win+=any(
            continuation(
                tuple(c for c in post_nest_hand if c not in set(pay)),
                post_nest_deck
            )
            for pay in combinations(
                (c for c in post_nest_hand if c[0]!="P"),3
            )
        )
    return Fraction(win,comb(len(pool),prizes))


def main():
    cases=0
    for d,i,s,basics in product((2,3,4),(0,1),(1,2),(0,1,2)):
        visible=counts(D=d,I=1,A=1,G=1,S=1,P=1)
        unknown=counts(D=2,I=i,A=1,B=1,G=1,S=s,E=1,P=3)
        modeled=optimal_pre_nest_choice(
            visible,unknown,visible_basics=1,
            unseen_basics=basics,prizes=2
        )
        exact=independent_nest_first(
            visible,unknown,unknown_basics=basics,prizes=2
        )
        assert modeled.nest_first_k0==exact,(
            d,i,s,basics,modeled,exact
        )
        assert modeled.informational_upper_bound>=modeled.optimal_first_action_success
        assert modeled.nest_first_k0<=modeled.informational_upper_bound
        cases+=1
    assert cases==36
    print("Independent labeled pre-Nest-Ball Prize and payment oracle:",cases,"PASS")

    winners=[]
    checked=0
    for d,ha,hg,hs,di,da,dg,ds in product(
        (1,2,3,4),(0,1),(0,1),(0,1),
        (0,1),(1,2),(1,2),(1,2)
    ):
        visible=counts(D=d,I=1,A=ha,G=hg,S=hs,P=1)
        unknown=counts(D=4,I=di,A=da,B=1,G=dg,S=ds,E=1,P=6)
        r=optimal_pre_nest_choice(
            visible,unknown,visible_basics=1,
            unseen_basics=2,prizes=2
        )
        assert r.informational_upper_bound>=r.optimal_first_action_success
        previous=exact_nest_payment_policy(
            visible,unknown,visible_basics=1,
            unknown_basics=2,prize_count=2
        )
        assert r.informational_upper_bound==previous.clairvoyant_success
        if d>=3:
            assert r.box_first_k0==r.informational_upper_bound
        if r.gain_from_nest_first>0:
            winners.append((r.gain_from_nest_first,
                (d,ha,hg,hs,di,da,dg,ds),r))
        checked+=1
    winners.sort(key=lambda x:x[0],reverse=True)
    print("Finite canonical scan:",checked,"cases, prior-Nest improvements:",len(winners))
    for gain,params,result in winners[:5]:
        print(" params",params,"Box-first",result.box_first_k0,
              "Nest-first",result.nest_first_k0,
              "improvement",gain,
              "omniscient",result.informational_upper_bound)
    assert checked==512
    assert winners
    print("ALL TESTS PASSED")


if __name__=="__main__":
    main()
