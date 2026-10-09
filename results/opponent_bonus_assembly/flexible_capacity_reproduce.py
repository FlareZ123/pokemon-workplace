"""Exact physical-enumeration proof for one-use flexible assembly cards."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_flexible_capacity import FlexibleTwoDemand


def brute(model: FlexibleTwoDemand, draws: int) -> tuple[Fraction, Fraction, Fraction]:
    cards = (
        ["basic"]*model.basic_starters
        + ["a"]*model.a_only
        + ["b"]*model.b_only
        + ["flex"]*model.flexible
        + ["other"]*(
            model.deck_size - model.basic_starters - model.a_only
            - model.b_only - model.flexible
        )
    )
    total = together = single = error = 0
    for opening in combinations(range(model.deck_size), model.opening_size):
        if not any(cards[i] == "basic" for i in opening):
            continue
        remain = set(range(model.deck_size)) - set(opening)
        for prize in combinations(sorted(remain), model.prizes):
            deck = remain - set(prize)
            for bonus in combinations(sorted(deck), draws):
                observed = [cards[i] for i in (*opening, *bonus)]
                a = observed.count("a")
                b = observed.count("b")
                f = observed.count("flex")
                joint = bool((a+f) and (b+f))
                separate = bool((a and b) or (f and (a or b)) or f >= 2)
                total += 1
                together += int(joint)
                single += int(separate)
                error += int(joint and not separate)
    return Fraction(together,total), Fraction(single,total), Fraction(error,total)


def test_enumeration() -> None:
    models = (
        FlexibleTwoDemand(9,2,1,2,1,1,1),
        FlexibleTwoDemand(10,2,2,2,1,1,2),
        FlexibleTwoDemand(9,2,1,2,0,0,3),
    )
    for model in models:
        for draws in range(4):
            ideal, actual, gap = brute(model,draws)
            assert model.simultaneous_coverage(draws) == ideal
            assert model.one_use_coverage(draws) == actual
            assert model.one_use_gap(draws) == gap


def test_sixty_card_counterexample() -> None:
    models = [FlexibleTwoDemand(60,7,6,12,4-f,4-f,f) for f in range(5)]
    expected = (
        (0.12964829164733382,0.12964829164733382),
        (0.18249957367420355,0.1234388),
        (0.2415603552302913,0.1098723),
    )
    for f, (ideal, actual) in enumerate(expected):
        model = models[f]
        assert abs(float(model.simultaneous_coverage(0))-ideal)<1e-12
        assert abs(float(model.one_use_coverage(0))-actual)<1e-6
    for model in models:
        for draws in range(13):
            joint = model.simultaneous_coverage(draws)
            one = model.one_use_coverage(draws)
            gap = model.one_use_gap(draws)
            assert 0 <= one <= joint <= 1
            assert joint-one == gap
    at_two = models[2]
    print("Two flexible cards, opening ideal joint coverage:",
          f"{float(at_two.simultaneous_coverage(0)):.9%}")
    print("Two flexible cards, opening one-use coverage:",
          f"{float(at_two.one_use_coverage(0)):.9%}")
    print("False-completion overstatement:",
          f"{float(at_two.one_use_gap(0))*100:.9f} pp")


def test_zero_flexible() -> None:
    model = FlexibleTwoDemand(60,7,6,12,4,4,0)
    for draws in range(13):
        assert model.one_use_coverage(draws) == model.simultaneous_coverage(draws)
        assert model.one_use_gap(draws) == 0


if __name__ == "__main__":
    test_enumeration()
    test_sixty_card_counterexample()
    test_zero_flexible()
    print("PASS: physical one-use capacity, exact failure atom, 60-card cases")
