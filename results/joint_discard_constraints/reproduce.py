"""Reproduce the joint-discardability counterexample."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from joint_discard_constraints import (
    DiscardGroupConstraint,
    enumerate_group_constrained_discard_selections,
)
from multicopy_zone_state import ZoneCountState


def marginal(states, card):
    return sum(probability for probability, available in states if card in available)


def payability(states, cost):
    return sum(
        probability
        for probability, available in states
        if len(available) >= cost
    )


def main() -> None:
    state = ZoneCountState.from_mapping(
        {
            ("A", "hand"): 1,
            ("B", "hand"): 1,
            ("C", "hand"): 1,
        }
    )
    candidates = (
        DiscardCandidate("A"),
        DiscardCandidate("B"),
        DiscardCandidate("C"),
    )
    keep_one_of_ab = (
        DiscardGroupConstraint(frozenset({"A", "B"}), max_total=1),
    )

    raw_one = enumerate_discard_selections(state, candidates, 1)
    constrained_one = enumerate_group_constrained_discard_selections(
        state,
        candidates,
        1,
        keep_one_of_ab,
    )
    assert len(raw_one) == 3
    assert constrained_one == raw_one

    raw_two = enumerate_discard_selections(state, candidates, 2)
    constrained_two = enumerate_group_constrained_discard_selections(
        state,
        candidates,
        2,
        keep_one_of_ab,
    )
    assert len(raw_two) == 3
    assert len(constrained_two) == 2
    assert (1, 1, 0) in [selection.counts for selection in raw_two]
    assert (1, 1, 0) not in [
        selection.counts for selection in constrained_two
    ]

    raw_three = enumerate_discard_selections(state, candidates, 3)
    constrained_three = enumerate_group_constrained_discard_selections(
        state,
        candidates,
        3,
        keep_one_of_ab,
    )
    assert len(raw_three) == 1
    assert not constrained_three

    # Same marginal discardability, different joint payability.
    anti_correlated = (
        (Fraction(1, 2), frozenset({"A"})),
        (Fraction(1, 2), frozenset({"B"})),
    )
    positively_correlated = (
        (Fraction(1, 2), frozenset()),
        (Fraction(1, 2), frozenset({"A", "B"})),
    )
    for card in ("A", "B"):
        assert marginal(anti_correlated, card) == Fraction(1, 2)
        assert marginal(positively_correlated, card) == Fraction(1, 2)

    assert payability(anti_correlated, 2) == 0
    assert payability(positively_correlated, 2) == Fraction(1, 2)

    print("single-card witnesses=3 in both models")
    print("two-card raw witnesses=3")
    print("two-card constrained witnesses=2")
    print("three-card raw witnesses=1")
    print("three-card constrained witnesses=0")
    print("marginal_DCI_A=1/2")
    print("marginal_DCI_B=1/2")
    print("cost2_payability_anticorrelated=0")
    print("cost2_payability_correlated=1/2")
    print("All joint discardability checks passed.")


if __name__ == "__main__":
    main()
