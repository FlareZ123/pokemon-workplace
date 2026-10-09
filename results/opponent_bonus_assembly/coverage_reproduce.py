"""Exhaustive physical-card validation of multi-role opponent bonus draws."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.opponent_bonus_coverage import CoverageClass, OpponentBonusCoverage
from tools.opponent_bonus_assembly import OpponentBonusAssembly


def physical_enumeration(model: OpponentBonusCoverage, draws: int) -> Fraction:
    cards = [
        (c.basic, c.groups)
        for c in model.classes
        for _ in range(c.count)
    ]
    good = total = 0
    n = len(cards)
    for opening in combinations(range(n), model.opening_size):
        if not any(cards[i][0] for i in opening):
            continue
        outside = set(range(n)) - set(opening)
        for prizes in combinations(sorted(outside), model.prize_count):
            deck = outside - set(prizes)
            for bonus in combinations(sorted(deck), draws):
                seen = set(opening) | set(bonus)
                good += int(all(any(
                    group in cards[index][1] for index in seen
                ) for group in range(model.required_count)))
                total += 1
    return Fraction(good, total)


def test_enumeration() -> None:
    scenarios = (
        OpponentBonusCoverage(
            2, 1, 2,
            (
                CoverageClass(2, frozenset(), True),
                CoverageClass(1, frozenset({0})),
                CoverageClass(1, frozenset({1})),
                CoverageClass(1, frozenset({0, 1})),
                CoverageClass(4, frozenset()),
            ),
        ),
        OpponentBonusCoverage(
            2, 1, 2,
            (
                CoverageClass(1, frozenset(), True),
                CoverageClass(1, frozenset({0, 1}), True),
                CoverageClass(1, frozenset({0})),
                CoverageClass(1, frozenset({1})),
                CoverageClass(5, frozenset()),
            ),
        ),
    )
    for model in scenarios:
        for m in range(4):
            assert model.probability(m) == physical_enumeration(model, m)


def test_composition() -> None:
    # A physical four-copy Basic target, twelve total Basics, four-copy
    # independent non-Basic target, and forty-four filler cards.
    special = OpponentBonusAssembly(60, 7, 6, 12, (4, 4), (4, 0))
    general = OpponentBonusCoverage(
        7, 6, 2,
        (
            CoverageClass(4, frozenset({0}), True),
            CoverageClass(8, frozenset(), True),
            CoverageClass(4, frozenset({1})),
            CoverageClass(44, frozenset()),
        ),
    )
    for m in range(13):
        assert special.assembly_probability(m) == general.probability(m)


def test_dual_roles() -> None:
    # Four effective copies per group, replacing exclusive A/B copies
    # with multi-role cards while preserving all other card identities.
    def scenario(dual: int) -> OpponentBonusCoverage:
        return OpponentBonusCoverage(
            7, 6, 2,
            (
                CoverageClass(12, frozenset(), True),
                CoverageClass(4 - dual, frozenset({0})),
                CoverageClass(4 - dual, frozenset({1})),
                CoverageClass(dual, frozenset({0, 1})),
                CoverageClass(40 + dual, frozenset()),
            ),
        )

    first = []
    peaks = []
    for dual in range(3):
        model = scenario(dual)
        assert model.deck_size == 60
        for group in range(2):
            assert sum(c.count for c in model.classes if group in c.groups) == 4
        probs = [model.probability(m) for m in range(13)]
        gains = [b-a for a,b in zip(probs,probs[1:])]
        first.append(float(probs[0]))
        peaks.append(gains.index(max(gains)))
    assert peaks == [4,3,0]
    for a,b in zip(first,first[1:]):
        assert a < b
    assert abs(first[0] - 0.12964829164733382) < 1e-12
    assert abs(first[1] - 0.18249957) < 1e-7
    assert abs(first[2] - 0.24156036) < 1e-7
    print("Opening joint assembly (0,1,2 dual cards):", first)
    print("Peak marginal bonus draw indices:", peaks)


def test_single_target_theorem() -> None:
    for count in (1,2,3,4):
        model = OpponentBonusCoverage(
            7, 6, 1,
            (
                CoverageClass(12, frozenset(), True),
                CoverageClass(count, frozenset({0})),
                CoverageClass(48-count, frozenset()),
            ),
        )
        p = [model.probability(i) for i in range(13)]
        increments = [b-a for a,b in zip(p,p[1:])]
        assert all(a >= b for a,b in zip(increments,increments[1:]))
        if count == 1:
            assert len(set(increments)) == 1


if __name__ == "__main__":
    test_enumeration()
    test_composition()
    test_dual_roles()
    test_single_target_theorem()
    print("PASS: dual-role coverage, exact physical enumeration, single-target theorem")
