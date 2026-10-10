"""Enumerate physical opening/Prize/draw worlds for turn-order Item access."""

from __future__ import annotations
import itertools
import sys
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from grand_tree_arven_union_access import ArvenUnionAccess


def brute(m: ArvenUnionAccess, *, going_second: bool) -> Fraction:
    names=(
        ("B",)*m.basics+("G",)*m.gladion+("A",)*m.arven
        +("T","S1","S2","Comm")
        +("F",)*(m.total-m.basics-m.gladion-m.arven-4)
    )
    assert len(names)==m.total
    cards=tuple(range(m.total))
    valid=0
    success=Fraction()
    for hand in itertools.combinations(cards,m.opening):
        hset=set(hand)
        if not any(names[i]=="B" for i in hand):
            continue
        valid+=1
        hnames={names[i] for i in hand}
        if not {"B","G","T"}<=hnames or "S1" in hnames or "S2" in hnames:
            continue
        deck_before_prizes=tuple(i for i in cards if i not in hset)
        prizes_sum=Fraction()
        prize_ways=0
        for prize in itertools.combinations(deck_before_prizes,m.prizes):
            prize_ways+=1
            pset=set(prize)
            if sum(names[i]=="S1" for i in prize)!=1 or any(
                names[i]=="S2" for i in prize
            ):
                continue
            deck=tuple(i for i in deck_before_prizes if i not in pset)
            first_sum=Fraction()
            for first in deck:
                if names[first]=="S2":
                    continue
                after_first=tuple(i for i in deck if i!=first)
                has_comm="Comm" in hnames or names[first]=="Comm"
                has_arven="A" in hnames or names[first]=="A"
                if (
                    not has_comm and going_second and has_arven
                    and any(names[i]=="Comm" for i in after_first)
                ):
                    # Arven played T1, removing Communication from deck.
                    after=tuple(i for i in after_first if names[i]!="Comm")
                    wins=sum(names[i]!="S2" for i in after)
                else:
                    after=after_first
                    wins=sum(
                        names[i]!="S2" and (
                            has_comm or names[i]=="Comm"
                        ) for i in after
                    )
                first_sum+=Fraction(wins,len(after)*len(deck))
            prizes_sum+=first_sum
        success+=prizes_sum/prize_ways
    return success/valid


def main() -> None:
    cases=(
        ArvenUnionAccess(10,2,1,0,4,2),
        ArvenUnionAccess(10,2,1,1,4,2),
        ArvenUnionAccess(10,2,2,1,4,2),
        ArvenUnionAccess(11,2,1,2,5,2),
        ArvenUnionAccess(11,2,2,2,5,2),
        ArvenUnionAccess(11,3,1,2,5,2),
        ArvenUnionAccess(11,3,2,1,5,2),
        ArvenUnionAccess(11,3,2,2,5,2),
    )
    for case in cases:
        for second in (False,True):
            exact=case.probability(going_second=second)
            independent=brute(case,going_second=second)
            assert exact==independent,(case,second,exact,independent)
            assert 0<=exact<=1
    for a in range(5):
        case=ArvenUnionAccess(arven=a)
        first=case.probability(going_second=False)
        second=case.probability(going_second=True)
        assert second>=first
        print(
            "Arven",a,
            "P(first)%",f"{float(first)*100:.9f}",
            "P(second)%",f"{float(second)*100:.9f}",
            "gain pp",f"{float(second-first)*100:.9f}",
        )
    assert ArvenUnionAccess(arven=0).going_second_advantage()==0
    print("independent worlds",len(cases)*2)
    print("grand_tree_arven_union_access: PASS")


if __name__=="__main__":
    main()
