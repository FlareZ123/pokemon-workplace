"""Exhaustive Prize-subset validation of ranked multi-copy search targets."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_search_family_value import RankedFamilySearch
from tools.opponent_bonus_search_choice_value import RankedSingletonSearch


def exhaustive(model: RankedFamilySearch) -> tuple[Fraction,Fraction]:
    targets=[]
    for group,copies in enumerate(model.family_copies):
        targets.extend([group]*copies)
    filler=model.unseen_cards-len(targets)
    labels=targets+[-1]*filler
    fixed=adaptive=Fraction()
    total=0
    for prize in combinations(range(model.unseen_cards),model.prizes):
        gone=set(prize)
        available={
            labels[i]
            for i in range(model.unseen_cards)
            if i not in gone
        }
        fixed+=model.family_values[0] if 0 in available else 0
        adaptive+=max(
            (value for group,value in enumerate(model.family_values)
             if group in available),
            default=Fraction(),
        )
        total+=1
    return fixed/total,adaptive/total


def test_small() -> None:
    for n in (6,7,8):
        for p in range(n+1):
            for families in (
                ((1,Fraction(1)),),
                ((1,Fraction(1)),(1,Fraction(3,5))),
                ((2,Fraction(1)),(1,Fraction(3,5))),
                ((2,Fraction(1)),(2,Fraction(3,5))),
                ((1,Fraction(1)),(1,Fraction(3,5)),(1,Fraction(1,3))),
            ):
                counts=tuple(count for count,value in families)
                values=tuple(value for count,value in families)
                if sum(counts)>n:
                    continue
                model=RankedFamilySearch(n,p,counts,values)
                fixed,adaptive=exhaustive(model)
                assert model.fixed_choice_value()==fixed
                assert model.adaptive_choice_value()==adaptive
                assert model.information_gain()>=0


def test_singleton_reduction() -> None:
    for p in (0,1,3,6):
        singleton=RankedSingletonSearch(
            53,p,(Fraction(1),Fraction(3,5),Fraction(3,10))
        )
        families=RankedFamilySearch(
            53,p,(1,1,1),(Fraction(1),Fraction(3,5),Fraction(3,10))
        )
        assert singleton.fixed_choice_value()==families.fixed_choice_value()
        assert singleton.adaptive_choice_value()==families.adaptive_choice_value()


def test_option_divergence() -> None:
    best_plus_backup=RankedFamilySearch.from_values(
        53,6,((1,1.0),(1,0.6))
    )
    duplicate_best=RankedFamilySearch.from_values(
        53,6,((2,1.0),)
    )
    two_best_plus_backup=RankedFamilySearch.from_values(
        53,6,((2,1.0),(1,0.6))
    )
    assert duplicate_best.adaptive_choice_value()>best_plus_backup.adaptive_choice_value()
    assert two_best_plus_backup.information_gain()<best_plus_backup.information_gain()
    assert duplicate_best.adaptive_choice_value()-best_plus_backup.adaptive_choice_value()==(
        Fraction(2,5)*Fraction(6,53)*Fraction(47,52)
    )
    print("A singleton + B singleton value:",f"{float(best_plus_backup.adaptive_choice_value()):.9f}")
    print("Two copies of A value:",f"{float(duplicate_best.adaptive_choice_value()):.9f}")
    print("Two copies A + B option gain:",f"{float(two_best_plus_backup.information_gain()):.9f}")
    print("Slot swap duplicate A vs B:",f"{float(duplicate_best.adaptive_choice_value()-best_plus_backup.adaptive_choice_value()):.9f}")


if __name__=="__main__":
    test_small()
    test_singleton_reduction()
    test_option_divergence()
    print("PASS: exact multi-copy target Prize configurations and option valuation")
