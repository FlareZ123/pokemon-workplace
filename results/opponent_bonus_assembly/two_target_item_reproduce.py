"""Independent labeled-card oracle for two paid one-output search Items."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_two_target_item import TwoTargetPaidItem


def exhaustive(model: TwoTargetPaidItem, bonus: int,
               *, ignore_payment: bool = False,
               ignore_prizes: bool = False) -> Fraction:
    labels=(
        ["basic"]*model.ordinary_basics
        + ["a","b"]
        + ["item"]*model.item_sources
        + ["safe"]*model.safe_fodder
        + ["other"]*model.capacities[-1]
    )
    good=total=0
    n=model.deck_size
    for opening in combinations(range(n),model.hand_size):
        if not any(labels[i]=="basic" for i in opening):
            continue
        outside=set(range(n))-set(opening)
        for prize in combinations(sorted(outside),model.prizes):
            prize_labels=[labels[i] for i in prize]
            remaining=outside-set(prize)
            for extra in combinations(sorted(remaining),bonus):
                hand=[labels[i] for i in (*opening,*extra)]
                missing=2-hand.count("a")-hand.count("b")
                enough_items=hand.count("item")>=missing
                enough_fodder=hand.count("safe")>=missing*model.payment_per_item
                targets_unprized=all(
                    prize_labels.count(target)==0
                    for target in ("a","b") if hand.count(target)==0
                )
                okay=enough_items and (
                    ignore_payment or enough_fodder
                ) and (ignore_prizes or targets_unprized)
                good+=int(okay)
                total+=1
    return Fraction(good,total)


def test_small() -> None:
    models=(
        TwoTargetPaidItem(11,3,2,2,2,2,1),
        TwoTargetPaidItem(12,3,2,2,2,3,2),
    )
    for model in models:
        for m in (0,1,2):
            for ignore_payment in (False,True):
                for ignore_prizes in (False,True):
                    actual=model.probability(
                        m,
                        ignore_payment=ignore_payment,
                        ignore_prizes=ignore_prizes,
                    )
                    oracle=exhaustive(
                        model,m,ignore_payment=ignore_payment,
                        ignore_prizes=ignore_prizes,
                    )
                    assert actual==oracle,(model,m,ignore_payment,ignore_prizes)


def benchmark() -> None:
    print("D | sources | bonus | ideal | payment | prizes | both")
    for d,sources in ((4,2),(8,2),(12,2),(20,2),(8,3),(12,3)):
        model=TwoTargetPaidItem(safe_fodder=d,item_sources=sources)
        for bonus in (0,4,8):
            result=model.ablation(bonus)
            physical=result["physical"]
            assert physical<=result["payment_only"]<=result["ideal"]
            assert physical<=result["prize_only"]<=result["ideal"]
            values=" | ".join(
                f"{float(result[key]):.8%}"
                for key in ("ideal","payment_only","prize_only","physical")
            )
            print(f"{d:2d} | {sources} | {bonus:2d} | {values}")
        assert model.probability(0)<=model.probability(4)<=model.probability(8)


def test_two_searcher_interaction() -> None:
    # With only one ordinary searcher and two absent singleton targets,
    # the double-search branch must be impossible, regardless of fodder.
    single=TwoTargetPaidItem(item_sources=1,safe_fodder=20)
    double=TwoTargetPaidItem(item_sources=2,safe_fodder=20)
    assert double.probability(8)>single.probability(8)


if __name__=="__main__":
    test_small()
    test_two_searcher_interaction()
    benchmark()
    print("PASS: physical two-target Item search, prizes, payments, capacity")
