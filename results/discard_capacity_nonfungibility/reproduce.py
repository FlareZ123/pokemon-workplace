"""Reproduce non-fungible discard capacity under joint constraints."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import (
    DiscardCandidate,
    apply_discard_selection,
)
from joint_discard_constraints import (
    DiscardGroupConstraint,
    enumerate_group_constrained_discard_selections,
    maximum_group_constrained_discard_cost,
)
from multicopy_zone_state import ZoneCountState


def selection_with_counts(selections, counts):
    matches = [selection for selection in selections if selection.counts == counts]
    if len(matches) != 1:
        raise AssertionError((counts, selections))
    return matches[0]


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
    constraints = (
        DiscardGroupConstraint(frozenset({"A", "B"}), max_total=1),
    )

    initial_capacity = maximum_group_constrained_discard_cost(
        state,
        candidates,
        constraints,
    )
    assert initial_capacity == 2

    one_card = enumerate_group_constrained_discard_selections(
        state,
        candidates,
        1,
        constraints,
    )
    assert len(one_card) == 3

    discard_a = selection_with_counts(one_card, (1, 0, 0))
    discard_c = selection_with_counts(one_card, (0, 0, 1))

    after_a = apply_discard_selection(
        state,
        candidates,
        discard_a,
    ).after
    after_c = apply_discard_selection(
        state,
        candidates,
        discard_c,
    ).after

    capacity_after_a = maximum_group_constrained_discard_cost(
        after_a,
        candidates,
        constraints,
    )
    capacity_after_c = maximum_group_constrained_discard_cost(
        after_c,
        candidates,
        constraints,
    )
    assert capacity_after_a == 2
    assert capacity_after_c == 1

    downstream_after_a = enumerate_group_constrained_discard_selections(
        after_a,
        candidates,
        2,
        constraints,
    )
    downstream_after_c = enumerate_group_constrained_discard_selections(
        after_c,
        candidates,
        2,
        constraints,
    )
    assert len(downstream_after_a) == 1
    assert not downstream_after_c

    print("initial_capacity=2")
    print("first_cost=1")
    print("capacity_after_discard_A=2")
    print("capacity_after_discard_C=1")
    print("downstream_cost2_after_A=True")
    print("downstream_cost2_after_C=False")
    print("All discard-capacity non-fungibility checks passed.")


if __name__ == "__main__":
    main()
