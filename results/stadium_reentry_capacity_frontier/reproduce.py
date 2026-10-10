"""Reproduce resource-contention reversal in Stadium effect-use availability."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from stadium_entry_channels import StadiumCopy, StadiumEntryState
from stadium_reentry_capacity_frontier import (
    CapacityFrontierState,
    maximize_target_evolutions,
)
from stadium_reentry_usage_bounds import StadiumReentryState
from turn_action_budget import TurnActionBudget


def initial(sources: int, copies: int, reserved: int) -> CapacityFrontierState:
    assert 0 <= sources <= 4
    assert copies in (1, 2)
    assert 0 <= reserved <= 2
    targets = max(0, 6 - sources - reserved)
    discard = (
        (StadiumCopy("tree-2", "Grand Tree"),)
        if copies == 2 else ()
    )
    stadium = StadiumReentryState(StadiumEntryState(
        budget=TurnActionBudget(),
        hand=(StadiumCopy("brooklet", "Brooklet Hill"),),
        discard=discard,
        in_play=StadiumCopy("tree-1", "Grand Tree"),
        teleport_room_sources=frozenset(
            "goth-" + str(i) for i in range(sources)
        ),
    ))
    return CapacityFrontierState(
        stadium=stadium,
        ready=frozenset("basic-" + str(i) for i in range(targets)),
        reserved_non_targets=reserved,
    )


def test_capacity_census() -> None:
    rows = []
    for copies in (1, 2):
        for reserved in (0, 1, 2):
            for sources in range(5):
                board = initial(sources, copies, reserved)
                slots = len(board.ready)
                entry_bound = 1 + (sources + 1) // 2
                for policy in ("entry", "physical_copy"):
                    count, trace = maximize_target_evolutions(board, policy)
                    source_limit = (
                        entry_bound if policy == "entry"
                        else min(copies, entry_bound)
                    )
                    expected = min(source_limit, slots)
                    assert count == expected, (
                        copies, reserved, sources, policy, count, expected
                    )
                    selected_targets = [
                        move.split(":", 1)[1]
                        for move in trace if move.startswith("evolve:")
                    ]
                    assert len(selected_targets) == count
                    assert len(set(selected_targets)) == count
                    rows.append((copies, reserved, sources, policy, count))

    assert len(rows) == 60

    # A fourth Gothitelle occupies the board slot that would otherwise
    # be the third eligible Basic; the added source makes the best *actual*
    # count worse even under the optimistic per-entry semantics.
    a, trace_a = maximize_target_evolutions(initial(3, 1, 0), "entry")
    b, trace_b = maximize_target_evolutions(initial(4, 1, 0), "entry")
    assert (a, b) == (3, 2)
    assert trace_a and trace_b

    # An additional reserved attacker creates a further collapse.
    c, _ = maximize_target_evolutions(initial(4, 1, 1), "entry")
    d, _ = maximize_target_evolutions(initial(4, 1, 2), "entry")
    assert (c, d) == (1, 0)

    # All physical Stadium copies remain in the source inventory and normal
    # Stadium quota is never multiplied by an effect-based placement.
    assert initial(4, 1, 0).stadium.entry.budget.stadium_plays_used == 0
    print("cases", len(rows))
    print("entry copy1 reserved0 sources0..4:",
          [x[4] for x in rows
           if x[0] == 1 and x[1] == 0 and x[3] == "entry"])
    print("entry copy1 reserved1 sources0..4:",
          [x[4] for x in rows
           if x[0] == 1 and x[1] == 1 and x[3] == "entry"])


if __name__ == "__main__":
    test_capacity_census()
    print("stadium_reentry_capacity_frontier: PASS")
