"""Independent exhaustive paid-bundle validation and disposable-pool frontier."""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_bundle_payment import PaidBundleTwoDemand
from tools.opponent_bonus_output_bundles import (
    OutputBundleClass,BonusOutputBundles,
)


def enumerate_physical(model: PaidBundleTwoDemand, bonus: int,
                       ignore_payment: bool = False) -> Fraction:
    categories = (
        ["basic"]*model.ordinary_basics
        + ["a"]*model.exclusive_a
        + ["b"]*model.exclusive_b
        + ["flex"]*model.single_output_flexible
        + ["bundle"]*model.bundled_cards
        + ["safe"]*model.safe_discards
        + ["other"]*model.class_capacities[-1]
    )
    good=total=0
    for opener in combinations(range(model.deck_size),model.opening_size):
        if not any(categories[i]=="basic" for i in opener):
            continue
        outside=set(range(model.deck_size))-set(opener)
        for prizes in combinations(sorted(outside),model.prize_count):
            deck=outside-set(prizes)
            for extra in combinations(sorted(deck),bonus):
                observed=[categories[i] for i in (*opener,*extra)]
                a=observed.count("a")
                b=observed.count("b")
                f=observed.count("flex")
                payable=bool(observed.count("bundle") and (
                    ignore_payment or observed.count("safe")>=model.bundle_payment
                ))
                success=bool((a and b) or (f and (a or b)) or f>=2 or payable)
                good+=int(success)
                total+=1
    return Fraction(good,total)


def test_small() -> None:
    models=(
        PaidBundleTwoDemand(10,2,1,2,1,1,1,1,2,2),
        PaidBundleTwoDemand(11,3,2,2,0,0,1,1,3,2),
    )
    for model in models:
        for m in (0,1,2):
            assert model.probability(m)==enumerate_physical(model,m)
            assert model.probability(m,ignore_payment=True)==(
                enumerate_physical(model,m,ignore_payment=True)
            )
            assert model.probability(m,allow_bundle=False) <= model.probability(m)
            assert model.probability(m) <= model.probability(m,ignore_payment=True)


def test_bundle_equivalence() -> None:
    model=PaidBundleTwoDemand(safe_discards=12)
    capacities=model.class_capacities
    abstract=BonusOutputBundles(
        model.opening_size,model.prize_count,2,
        (
            OutputBundleClass(capacities[0],True,()),
            OutputBundleClass(capacities[1],False,(frozenset({0}),)),
            OutputBundleClass(capacities[2],False,(frozenset({1}),)),
            OutputBundleClass(capacities[3],False,(
                frozenset({0}),frozenset({1})
            )),
            OutputBundleClass(capacities[4],False,(frozenset({0,1}),)),
            OutputBundleClass(capacities[5],False,()),
            OutputBundleClass(capacities[6],False,()),
        ),
    )
    for m in (0,1,3,7):
        assert model.probability(m,ignore_payment=True)==abstract.probability(m)


def benchmark() -> None:
    print("Safe discards | paid bundle opening | third flexible opening | difference (pp)")
    crossover=[]
    for d in (3,4,6,8,12,16,20,24,28):
        model=PaidBundleTwoDemand(safe_discards=d)
        third=replace(model,bundled_cards=0,single_output_flexible=3)
        actual=model.probability(0)
        control=third.probability(0)
        assert control==third.probability(0,allow_bundle=False)
        assert model.probability(0,ignore_payment=True)>actual
        delta=actual-control
        print(f"{d:3d} | {float(actual):.9%} | {float(control):.9%} | {100*float(delta):+.9f}")
        crossover.append((d,delta))
    assert crossover[0][1]<0
    assert crossover[-1][1]>0


if __name__=="__main__":
    test_small()
    test_bundle_equivalence()
    benchmark()
    print("PASS: cost-gated bundled source, exhaustive oracle, crossover")
