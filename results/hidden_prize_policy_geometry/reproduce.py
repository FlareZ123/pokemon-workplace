"""SFT: event-cover geometry from an exact Secret Box hidden-Prize witness."""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))

from hidden_prize_policy_geometry import evaluate_binary_policy_events
from secret_box_gnh_tool_pipeline import counts,D,I,A,B,G,S,E,P,_pay
from secret_box_k0_payment import (
    evaluate_hidden_prize_payment,continuation_after_box_payment,
)


def synthetic_examples():
    test=evaluate_binary_policy_events(
        (2,3,5),
        {
            "pay-a":(True,False,True),
            "pay-b":(False,True,True),
            "dominated":(False,False,True),
        }
    )
    assert test.uninformed_success==Fraction(4,5)
    assert test.clairvoyant_success==1
    assert test.best_actions==("pay-b",)
    assert test.nondominated_actions==("pay-a","pay-b")
    assert test.minimum_union_cover==2
    assert test.action_count==3
    assert test.world_count==3

    all_dead=evaluate_binary_policy_events(
        (1,1,1),{"a":(False,False,False)}
    )
    assert all_dead.uninformed_success==all_dead.clairvoyant_success==0
    assert all_dead.minimum_union_cover==0
    print("Synthetic nondominance and cover fixtures: PASS")


def secret_box_witness():
    hand=counts(D=2,A=1,G=1,S=1,P=2)
    unknown=counts(D=18,I=1,A=1,B=1,G=1,S=1,E=1,P=28)
    assert 1+sum(hand)+sum(unknown)==60

    payments=tuple(sorted(set(_pay(hand,3))))
    assert len(payments)==7
    keys=(I,A,B,G,S,E)
    events={paid:[] for paid in payments}
    weights=[]
    for prized in product((0,1),repeat=6):
        remaining_filler_prizes=6-sum(prized)
        weight=comb(46,remaining_filler_prizes)
        deck=[0]*8
        for target,count in zip(keys,prized):
            deck[target]=1-count
        deck=tuple(deck)
        weights.append(weight)
        for paid in payments:
            events[paid].append(continuation_after_box_payment(paid,deck))
    assert len(weights)==64 and sum(weights)==comb(52,6)

    geometry=evaluate_binary_policy_events(weights,events)
    existing=evaluate_hidden_prize_payment(hand,unknown,prize_count=6)
    assert geometry.uninformed_success==existing.k0_success
    assert geometry.clairvoyant_success==existing.clairvoyant_success
    assert geometry.uninformed_success==Fraction(1925583,2908360)
    assert geometry.clairvoyant_success==Fraction(32637,44744)
    assert geometry.information_gap==Fraction(97911,1454180)
    assert set(geometry.best_actions)==set(existing.best_paid_hands)
    assert geometry.minimum_union_cover>1
    print("Exact 60-card payment world census:",geometry.world_count,"PASS")
    print("Payment alternatives:",geometry.action_count)
    print("Distinct nondominated success events:",len(geometry.nondominated_actions))
    print("Minimum action-family cover:",geometry.minimum_union_cover)
    print("K0:",geometry.uninformed_success,float(geometry.uninformed_success))
    print("K1:",geometry.clairvoyant_success,float(geometry.clairvoyant_success))
    print("Information gap:",geometry.information_gap,float(geometry.information_gap))


if __name__=="__main__":
    synthetic_examples()
    secret_box_witness()
    print("ALL TESTS PASSED")
