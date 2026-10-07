"""Regression checks for discard_family_resilience."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_family_resilience import (
    discard_family_metrics,
    uniform_protection_survival,
)


def main() -> None:
    # All three families contain exactly three discard-pair witnesses.
    star = ({"A", "B"}, {"A", "C"}, {"A", "D"})
    triangle = ({"A", "B"}, {"A", "C"}, {"B", "C"})
    matching = ({"A", "B"}, {"C", "D"}, {"E", "F"})

    s = discard_family_metrics(star)
    t = discard_family_metrics(triangle)
    m = discard_family_metrics(matching)

    assert s.witness_count == t.witness_count == m.witness_count == 3
    assert s.forced_cards == frozenset({"A"})
    assert not t.forced_cards and not m.forced_cards
    assert s.minimum_protection_cut == 1
    assert t.minimum_protection_cut == 2
    assert m.minimum_protection_cut == 3

    universe = ("A", "B", "C", "D", "E", "F")
    assert abs(uniform_protection_survival(
        star, 1, candidate_universe=universe
    ) - 5 / 6) < 1e-12
    assert uniform_protection_survival(
        triangle, 1, candidate_universe=universe
    ) == 1.0
    assert uniform_protection_survival(
        matching, 1, candidate_universe=universe
    ) == 1.0

    assert abs(uniform_protection_survival(
        star, 2, candidate_universe=universe
    ) - 10 / 15) < 1e-12
    assert abs(uniform_protection_survival(
        triangle, 2, candidate_universe=universe
    ) - 12 / 15) < 1e-12
    assert uniform_protection_survival(
        matching, 2, candidate_universe=universe
    ) == 1.0

    assert abs(uniform_protection_survival(
        star, 3, candidate_universe=universe
    ) - 9 / 20) < 1e-12
    assert abs(uniform_protection_survival(
        triangle, 3, candidate_universe=universe
    ) - 10 / 20) < 1e-12
    assert abs(uniform_protection_survival(
        matching, 3, candidate_universe=universe
    ) - 12 / 20) < 1e-12

    print("all discard-family resilience regressions passed")


if __name__ == "__main__":
    main()
