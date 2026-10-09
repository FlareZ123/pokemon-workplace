"""Independent Prize-set enumeration for ranked singleton choice value."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_search_choice_value import RankedSingletonSearch, from_numbers


def exhaustive(unseen: int, prizes: int,
               values: tuple[Fraction,...]) -> tuple[Fraction,Fraction,Fraction]:
    fixed=adaptive=none=Fraction()
    target_ids=tuple(range(len(values)))
    total=0
    for prized in combinations(range(unseen),prizes):
        prize_set=set(prized)
        choices=[value for i,value in enumerate(values) if i not in prize_set]
        fixed+=values[0] if 0 not in prize_set else Fraction()
        adaptive+=max(choices,default=Fraction())
        none+=int(not choices)
        total+=1
    return fixed/total,adaptive/total,none/total


def test_enumeration() -> None:
    for m in (6,7,8):
        for p in range(m+1):
            for values in (
                (Fraction(1),),
                (Fraction(1),Fraction(3,5)),
                (Fraction(1),Fraction(3,5),Fraction(1,10)),
            ):
                model=RankedSingletonSearch(m,p,values)
                fixed,adaptive,none=exhaustive(m,p,values)
                assert model.fixed_choice_value()==fixed
                assert model.adaptive_choice_value()==adaptive
                assert model.probability_no_targets_available()==none
                assert model.information_gain()>=0
                assert sum(
                    model.available_target_count_probability(k)
                    for k in range(len(values)+1)
                )==1


def test_benchmark() -> None:
    two=from_numbers(53,6,(1,0.6))
    three=from_numbers(53,6,(1,0.6,0.3))
    assert three.information_gain()>=two.information_gain()
    assert two.fixed_choice_value()==Fraction(47,53)
    assert two.information_gain()==(
        Fraction(3,5)*Fraction(6,53)*Fraction(47,52)
    )
    print("Two target fixed:",f"{float(two.fixed_choice_value()):.9f}")
    print("Two target adaptive:",f"{float(two.adaptive_choice_value()):.9f}")
    print("Two target inspection benefit:",f"{float(two.information_gain()):.9f}")
    print("Three target inspection benefit:",f"{float(three.information_gain()):.9f}")
    print("Three targets all Prized:",f"{float(three.probability_no_targets_available()):.9%}")


if __name__=="__main__":
    test_enumeration()
    test_benchmark()
    print("PASS: exact Prize subsets, conditional search output decisions")
