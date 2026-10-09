"""Physical Prize-location oracle for a paid singleton search source."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_search_target_prize import SingletonSearchPrize


def brute(model: SingletonSearchPrize, bonus: int) -> tuple[Fraction,Fraction]:
    labels=(
        ["basic"]*model.basics
        + ["a","b","search"]
        + ["safe"]*model.safe_discards
        + ["other"]*model.capacities[-1]
    )
    valid=naive=actual=0
    for hand in combinations(range(model.deck_size),model.opening_size):
        if not any(labels[i]=="basic" for i in hand):
            continue
        outside=set(range(model.deck_size))-set(hand)
        for prize in combinations(sorted(outside),model.prizes):
            available=outside-set(prize)
            for bonus_cards in combinations(sorted(available),bonus):
                seen=[labels[i] for i in (*hand,*bonus_cards)]
                direct=seen.count("a") and seen.count("b")
                source=(
                    seen.count("a")+seen.count("b")==1
                    and "search" in seen
                    and seen.count("safe")>=model.discard_payment
                )
                missing="b" if "a" in seen else "a"
                possible=bool(direct or source)
                success=bool(direct or (source and all(
                    labels[i]!=missing for i in prize
                )))
                valid+=1
                naive+=int(possible)
                actual+=int(success)
    return Fraction(naive,valid),Fraction(actual,valid)


def test_small() -> None:
    cases=(
        SingletonSearchPrize(11,3,2,2,2,2),
        SingletonSearchPrize(12,3,2,2,3,2),
    )
    for model in cases:
        for m in (0,1,2):
            optimistic,physical=brute(model,m)
            assert model.probability(m,assume_target_in_deck=True)==optimistic
            assert model.probability(m)==physical
            assert optimistic-physical==model.prize_overstatement(m)


def test_benchmark() -> None:
    print("Safe discards | bonus | naive success | Prize-aware success | gap(pp)")
    for d in (4,8,12,20):
        model=SingletonSearchPrize(safe_discards=d)
        for m in (0,4,8):
            naive=model.probability(m,assume_target_in_deck=True)
            true=model.probability(m)
            gap=model.prize_overstatement(m)
            assert naive-true==gap
            assert 0<=true<=naive<=1
            print(
                f"{d:2d} | {m:2d} | {float(naive):.9%} | "
                f"{float(true):.9%} | {100*float(gap):.9f}"
            )
        assert model.probability(0)<=model.probability(4)<=model.probability(8)


if __name__=="__main__":
    test_small()
    test_benchmark()
    print("PASS: independent Prize placement, conditional search availability")
