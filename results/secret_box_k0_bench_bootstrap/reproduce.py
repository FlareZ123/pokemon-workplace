"""SFT: distinct eligible Basic holders as a prerequisite for two Tools."""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from fractions import Fraction
from math import comb
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

from secret_box_gnh_tool_pipeline import counts
from secret_box_k0_opening_mix import average_box_payment_policy
from secret_box_k0_bench_bootstrap import (
    counted_visible_hands, holder_qualified_k0, baseline_holder_bridge,
)


def literal_distribution(deck, basic_count, opening_hand_size):
    labels = []
    for k, n in zip(("D","I","A","B","G","S","E"), deck[:-1]):
        labels += [(k,j) for j in range(n)]
    labels += [("Basic",j) for j in range(basic_count)]
    labels += [("P",j) for j in range(deck[-1]-basic_count)]
    out = Counter()
    total = 0
    for opener in combinations(range(len(labels)),opening_hand_size-1):
        if not any(labels[j][0]=="Basic" for j in opener):
            continue
        set_open = set(opener)
        for draw in range(len(labels)):
            if draw in set_open:
                continue
            shown = Counter(labels[j][0] for j in opener+(draw,))
            n_basic = shown.pop("Basic",0)
            shown["P"]+=n_basic
            out[(counts(**shown),n_basic)]+=1
            total+=1
    return dict(out),total


def analytical_holder_mass(N, basics, other_hand=6, required=2):
    accepted = comb(N,other_hand)-comb(N-basics,other_hand)
    denom = accepted*(N-other_hand)
    favorable = sum(
        comb(basics,s)*comb(N-basics,other_hand-s)
        * ((basics-s) if s+1>=required else 0)
        + comb(basics,s)*comb(N-basics,other_hand-s)
        * ((N-basics)-(other_hand-s) if s>=required else 0)
        for s in range(1,other_hand+1)
    )
    return Fraction(favorable,denom)


def main():
    toy=counts(D=4,I=1,A=1,B=1,G=1,S=1,E=1,P=3)
    typed, den=counted_visible_hands(toy,basics=2,opening_hand_size=5)
    literal, literal_den=literal_distribution(toy,2,5)
    assert (den,len(typed))==(3465,170), (den,len(typed))
    assert (typed,den)==(literal,literal_den)
    print("Independent labeled Basic and opener/draw census: PASS",
          "states",len(typed),"weighted orders",den)

    baseline=counts(D=20,I=1,A=2,B=1,G=2,S=2,E=1,P=30)
    ordinary=average_box_payment_policy(baseline,basic_starters=12)
    one=holder_qualified_k0(baseline,basics=12,min_holders=1)
    two=baseline_holder_bridge()
    three=holder_qualified_k0(baseline,basics=12,min_holders=3)
    assert (one.k0_joint_success,one.k1_joint_success) == (
        ordinary.k0_success,ordinary.clairvoyant_success
    )
    assert one.sufficient_holders_mass==1
    assert two.sufficient_holders_mass==analytical_holder_mass(59,12,required=2)
    assert three.sufficient_holders_mass==analytical_holder_mass(59,12,required=3)
    assert 0 < three.k0_joint_success < two.k0_joint_success < one.k0_joint_success
    assert 0 <= two.joint_information_gap <= one.joint_information_gap
    print("Unconstrained K0",float(one.k0_joint_success),"K1",float(one.k1_joint_success))
    print("Two holders mass",two.sufficient_holders_mass,float(two.sufficient_holders_mass))
    print("Two holders K0",two.k0_joint_success,float(two.k0_joint_success))
    print("Two holders K1",two.k1_joint_success,float(two.k1_joint_success))
    print("Two holders K1-K0",two.joint_information_gap,float(two.joint_information_gap))
    print("Three holders mass",three.sufficient_holders_mass,float(three.sufficient_holders_mass))
    print("Three holders K0",three.k0_joint_success,float(three.k0_joint_success))
    print("Three holders K1-K0",three.joint_information_gap,float(three.joint_information_gap))
    print("ALL TESTS PASSED")


if __name__=="__main__":
    main()
