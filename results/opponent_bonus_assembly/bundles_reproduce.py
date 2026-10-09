"""Independent physical-card enumeration of exclusive and bundle outputs."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_output_bundles import (
    OutputBundleClass, BonusOutputBundles,
)
from tools.opponent_bonus_flexible_capacity import FlexibleTwoDemand


def card_can_complete(
    observed: list[OutputBundleClass], required: int
) -> bool:
    """Independent recursive action-choice enumeration per physical copy."""
    full=(1<<required)-1
    def visit(index: int, covered: int) -> bool:
        if covered==full:
            return True
        if index==len(observed):
            return False
        if visit(index+1,covered):
            return True
        return any(
            visit(index+1,covered|sum(1<<role for role in choice))
            for choice in observed[index].output_choices
        )
    return visit(0,0)


def enumerate_physical(model: BonusOutputBundles, bonus: int) -> Fraction:
    physical=[OutputBundleClass(1,c.basic,c.output_choices)
              for c in model.classes for _ in range(c.count)]
    n=len(physical)
    correct=total=0
    for hand in combinations(range(n),model.opening_size):
        if not any(physical[i].basic for i in hand):
            continue
        outside=set(range(n))-set(hand)
        for prize in combinations(sorted(outside),model.prize_count):
            deck=outside-set(prize)
            for draws in combinations(sorted(deck),bonus):
                observed=[physical[i] for i in (*hand,*draws)]
                correct+=int(card_can_complete(observed,model.requirements))
                total+=1
    return Fraction(correct,total)


def test_small() -> None:
    scenarios=(
        BonusOutputBundles(
            2,1,2,
            (
                OutputBundleClass(2,True,()),
                OutputBundleClass(1,False,(frozenset({0}),)),
                OutputBundleClass(1,False,(frozenset({1}),)),
                OutputBundleClass(1,False,(frozenset({0}),frozenset({1}))),
                OutputBundleClass(1,False,(frozenset({0,1}),)),
                OutputBundleClass(3,False,()),
            ),
        ),
        BonusOutputBundles(
            3,1,3,
            (
                OutputBundleClass(2,True,()),
                OutputBundleClass(1,False,(frozenset({0}),)),
                OutputBundleClass(1,False,(frozenset({1,2}),frozenset({0,1}))),
                OutputBundleClass(1,True,(frozenset({2}),)),
                OutputBundleClass(4,False,()),
            ),
        ),
    )
    for model in scenarios:
        for bonus in range(3):
            assert model.probability(bonus)==enumerate_physical(model,bonus)


def test_reduction() -> None:
    model=BonusOutputBundles(
        7,6,2,
        (
            OutputBundleClass(12,True,()),
            OutputBundleClass(2,False,(frozenset({0}),)),
            OutputBundleClass(2,False,(frozenset({1}),)),
            OutputBundleClass(2,False,(frozenset({0}),frozenset({1}))),
            OutputBundleClass(42,False,()),
        ),
    )
    two_demand=FlexibleTwoDemand(60,7,6,12,2,2,2)
    for m in (0,1,2,4,8,12):
        assert model.probability(m)==two_demand.one_use_coverage(m)


def test_bundled_effect() -> None:
    common=(
        OutputBundleClass(12,True,()),
        OutputBundleClass(2,False,(frozenset({0}),)),
        OutputBundleClass(2,False,(frozenset({1}),)),
    )
    flexible=OutputBundleClass(2,False,(frozenset({0}),frozenset({1})))
    final=OutputBundleClass(41,False,())
    bundle=BonusOutputBundles(
        7,6,2,
        common+(flexible,OutputBundleClass(1,False,(frozenset({0,1}),)),final),
    )
    single=BonusOutputBundles(
        7,6,2,
        common+(
            OutputBundleClass(3,False,(frozenset({0}),frozenset({1}))),
            final,
        ),
    )
    assert bundle.deck_size==single.deck_size==60
    assert bundle.probability(0)>single.probability(0)
    assert bundle.probability(4)>single.probability(4)
    print("One bundled resource opening completion:",
          f"{float(bundle.probability(0)):.9%}")
    print("One extra single-output flex resource opening completion:",
          f"{float(single.probability(0)):.9%}")


if __name__=="__main__":
    test_small()
    test_reduction()
    test_bundled_effect()
    print("PASS: exact action-bundle choices, physical enumeration, and matching reduction")
