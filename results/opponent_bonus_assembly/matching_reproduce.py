"""Independent physical-card checks of conditional Hall-matching assembly."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_coverage import CoverageClass, OpponentBonusCoverage
from tools.opponent_bonus_matching import BonusMatching
from tools.opponent_bonus_flexible_capacity import FlexibleTwoDemand


def brute_match(cards: list[tuple[bool, frozenset[int]]], goals: int) -> bool:
    """Explicitly assign one distinct physical card to each demand."""
    def search(goal: int, used: frozenset[int]) -> bool:
        if goal == goals:
            return True
        return any(
            goal in card[1] and index not in used
            and search(goal + 1, used | {index})
            for index,card in enumerate(cards)
        )
    return search(0,frozenset())


def brute(model: OpponentBonusCoverage, draws: int) -> tuple[Fraction, Fraction]:
    cards = [
        (card.basic,card.groups)
        for card in model.classes
        for _ in range(card.count)
    ]
    both = [0,0]
    total = 0
    n = len(cards)
    for opener in combinations(range(n),model.opening_size):
        if not any(cards[i][0] for i in opener):
            continue
        outside = set(range(n)) - set(opener)
        for prize in combinations(sorted(outside),model.prize_count):
            from_deck = outside - set(prize)
            for bonus in combinations(sorted(from_deck),draws):
                seen = [cards[i] for i in (*opener,*bonus)]
                all_present = all(any(g in c[1] for c in seen)
                                  for g in range(model.required_count))
                physical = brute_match(seen,model.required_count)
                both[0] += int(all_present)
                both[1] += int(physical)
                total += 1
    return Fraction(both[0],total),Fraction(both[1],total)


def test_small() -> None:
    models = (
        OpponentBonusCoverage(
            2,1,3,
            (
                CoverageClass(2,frozenset(),True),
                CoverageClass(1,frozenset({0})),
                CoverageClass(1,frozenset({1})),
                CoverageClass(1,frozenset({2})),
                CoverageClass(1,frozenset({0,1,2})),
                CoverageClass(4,frozenset()),
            ),
        ),
        OpponentBonusCoverage(
            3,1,3,
            (
                CoverageClass(2,frozenset(),True),
                CoverageClass(1,frozenset({0})),
                CoverageClass(1,frozenset({1})),
                CoverageClass(1,frozenset({2})),
                CoverageClass(2,frozenset({0,1,2})),
                CoverageClass(4,frozenset()),
            ),
        ),
    )
    for model in models:
        max_draws = 3 if model.deck_size == 10 else 2
        solver = BonusMatching(model)
        for m in range(max_draws+1):
            ideal,actual=brute(model,m)
            assert solver.probability(m,single_use=False)==ideal
            assert solver.probability(m,single_use=True)==actual
            assert ideal >= actual


def test_specialization() -> None:
    model=OpponentBonusCoverage(
        7,6,2,
        (
            CoverageClass(12,frozenset(),True),
            CoverageClass(2,frozenset({0})),
            CoverageClass(2,frozenset({1})),
            CoverageClass(2,frozenset({0,1})),
            CoverageClass(42,frozenset()),
        ),
    )
    matching=BonusMatching(model)
    special=FlexibleTwoDemand(60,7,6,12,2,2,2)
    for draws in (0,1,2,4,8,12):
        assert matching.probability(draws,single_use=False) == (
            model.probability(draws)
        )
        assert matching.probability(draws,single_use=True) == (
            special.one_use_coverage(draws)
        )


def test_three_demand_benchmark() -> None:
    model=OpponentBonusCoverage(
        7,6,3,
        (
            CoverageClass(12,frozenset(),True),
            CoverageClass(2,frozenset({0})),
            CoverageClass(2,frozenset({1})),
            CoverageClass(2,frozenset({2})),
            CoverageClass(2,frozenset({0,1,2})),
            CoverageClass(40,frozenset()),
        ),
    )
    solver=BonusMatching(model)
    ideal=solver.probability(0,single_use=False)
    capacity_one=solver.probability(0,single_use=True)
    assert abs(float(ideal)-0.21438834654719358)<1e-12
    assert abs(float(capacity_one)-0.02451991415591293)<1e-12
    assert ideal-capacity_one > Fraction(18,100)
    for draws in (0,1,2,4,6,12):
        assert solver.probability(draws,single_use=False) == (
            model.probability(draws)
        )
    print("Three requirements, nominal opening completion:",
          f"{float(ideal):.9%}")
    print("Three requirements, physical one-use completion:",
          f"{float(capacity_one):.9%}")
    print("Exact overstatement:",f"{float(ideal-capacity_one)*100:.9f} pp")


if __name__=="__main__":
    test_small()
    test_specialization()
    test_three_demand_benchmark()
    print("PASS: physical enumeration, two-demand reduction, and Hall theorem")
