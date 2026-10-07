"""Reproduce DCI-style ranking over joint-feasible discard witnesses."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import DiscardCandidate
from discard_policy_ranking import rank_discard_selections
from joint_discard_constraints import DiscardGroupConstraint
from multicopy_zone_state import ZoneCountState


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
    scores = {
        "A": 1.0,
        "B": 0.9,
        "C": 0.1,
    }

    unconstrained = rank_discard_selections(
        state,
        candidates,
        2,
        (),
        scores,
    )
    assert unconstrained[0].selection.counts == (1, 1, 0)
    assert abs(unconstrained[0].desirability - 1.9) < 1e-12

    keep_one_of_ab = (
        DiscardGroupConstraint(frozenset({"A", "B"}), max_total=1),
    )
    constrained = rank_discard_selections(
        state,
        candidates,
        2,
        keep_one_of_ab,
        scores,
    )
    assert len(constrained) == 2
    assert constrained[0].selection.counts == (1, 0, 1)
    assert abs(constrained[0].desirability - 1.1) < 1e-12
    assert constrained[1].selection.counts == (0, 1, 1)
    assert abs(constrained[1].desirability - 1.0) < 1e-12

    print("naive_best=A+B score=1.9")
    print("naive_best_joint_legal=False")
    print("best_joint_legal=A+C score=1.1")
    print("second_joint_legal=B+C score=1.0")
    print("All discard policy ranking checks passed.")


if __name__ == "__main__":
    main()
