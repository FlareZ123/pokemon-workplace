"""Basic-only filler relabeling changes accepted-opening denominator."""

from __future__ import annotations

import sys
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"results"/"grand_tree_arven_union_access"))

from grand_tree_arven_union_access import ArvenUnionAccess
from reproduce import brute


def basic_valid_probability(case: ArvenUnionAccess) -> Fraction:
    return Fraction(
        comb(case.total,case.opening)
        - comb(case.total-case.basics-case.extra_basics,case.opening),
        comb(case.total,case.opening),
    )


def physical_regressions() -> None:
    checks=0
    for model_base in (
        (11,2,1,1,5,2),
        (11,2,2,1,5,2),
        (11,3,1,2,5,2),
        (12,2,1,2,5,3),
    ):
        first=ArvenUnionAccess(*model_base,extra_basics=0)
        baseline={
            order: first.probability(going_second=order)
                   * basic_valid_probability(first)
            for order in (False,True)
        }
        available=first.total-first.basics-first.gladion-first.arven-4
        for extras in range(min(3,available)+1):
            case=ArvenUnionAccess(*model_base,extra_basics=extras)
            for second in (False,True):
                actual=case.probability(going_second=second)
                independent=brute(case,going_second=second)
                assert actual==independent,(case,second,actual,independent)
                invariant=actual*basic_valid_probability(case)
                assert invariant==baseline[second]
                checks+=1
    assert checks>=24
    print("physical exact comparisons",checks)


def sixty_card_frontier() -> None:
    data=[]
    for extra in (0,2,4,8,12,16):
        case=ArvenUnionAccess(extra_basics=extra)
        valid=basic_valid_probability(case)
        p_first=case.probability(going_second=False)
        p_second=case.probability(going_second=True)
        data.append((extra,valid,p_first,p_second))
        print(
            "other_basic",extra,
            "P(valid opener)",f"{float(valid)*100:.9f}%",
            "P(first certificate|valid)",f"{float(p_first)*100:.9f}%",
            "P(second certificate|valid)",f"{float(p_second)*100:.9f}%",
        )
    assert [row[1] for row in data]==sorted(row[1] for row in data)
    assert [row[3] for row in data]==sorted(
        (row[3] for row in data),reverse=True
    )
    assert all(
        row[1]*row[2]==data[0][1]*data[0][2]
        for row in data
    )
    assert all(
        row[1]*row[3]==data[0][1]*data[0][3]
        for row in data
    )
    assert data[0][3]>2*data[-1][3]


if __name__=="__main__":
    physical_regressions()
    sixty_card_frontier()
    print("grand_tree_basic_mulligan_denominator: PASS")
