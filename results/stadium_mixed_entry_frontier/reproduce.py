"""Reproduce normal Stadium play plus Teleport Room reuse-sensitive frontier."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from stadium_entry_channels import StadiumCopy, StadiumEntryState
from stadium_reentry_usage_bounds import (
    StadiumReentryState,
    activate,
    can_activate,
    max_activations,
    ordinary_play_successors,
    teleport_successors,
)
from turn_action_budget import TurnActionBudget


def initial(n_sources: int, tree_copies: int) -> StadiumReentryState:
    assert 0 <= n_sources <= 4 and tree_copies in (1, 2)
    discard = (
        (StadiumCopy("tree-2", "Grand Tree"),)
        if tree_copies == 2
        else ()
    )
    return StadiumReentryState(StadiumEntryState(
        budget=TurnActionBudget(),
        hand=(StadiumCopy("brooklet-1", "Brooklet Hill"),),
        discard=discard,
        in_play=StadiumCopy("tree-1", "Grand Tree"),
        teleport_room_sources=frozenset(
            "goth-" + str(i) for i in range(n_sources)
        ),
    ))


def test_witness() -> None:
    original = initial(1, 1)
    used = activate(original, "entry")
    assert used is not None
    plays = ordinary_play_successors(used)
    assert len(plays) == 1
    after_play = plays[0]
    assert after_play.entry.in_play is not None
    assert after_play.entry.in_play.name == "Brooklet Hill"
    assert after_play.entry.budget.stadium_plays_used == 1
    assert ordinary_play_successors(after_play) == ()

    replacements = teleport_successors(after_play, "goth-0")
    assert len(replacements) == 1
    returned = replacements[0]
    assert returned.entry.in_play is not None
    assert returned.entry.in_play.copy_id == "tree-1"
    assert returned.entry.budget.stadium_plays_used == 1
    assert returned.entry.teleport_room_used == frozenset({"goth-0"})
    assert returned.epoch == 2
    assert can_activate(returned, "entry")
    assert not can_activate(returned, "physical_copy")
    assert not can_activate(returned, "name")
    assert activate(returned, "entry") is not None
    assert teleport_successors(returned, "goth-0") == ()

    original_two = initial(1, 2)
    used_two = activate(original_two, "entry")
    assert used_two is not None
    after_play_two, = ordinary_play_successors(used_two)
    options = teleport_successors(after_play_two, "goth-0")
    assert {x.entry.in_play.copy_id for x in options if x.entry.in_play} == {
        "tree-1", "tree-2"
    }
    distinct_copy = next(
        x for x in options if x.entry.in_play is not None
        and x.entry.in_play.copy_id == "tree-2"
    )
    assert can_activate(distinct_copy, "physical_copy")
    after_use = activate(distinct_copy, "physical_copy")
    assert after_use is not None
    assert [x.copy_id for x in after_use.uses] == ["tree-1", "tree-2"]
    assert (
        {x.copy_id for x in after_use.entry.discard}
        | {after_use.entry.in_play.copy_id}
    ) == {"tree-1", "tree-2", "brooklet-1"}


def test_census() -> None:
    for copies in (1, 2):
        for sources in range(5):
            base = initial(sources, copies)
            maxima = {}
            for policy in ("entry", "physical_copy", "name"):
                maximum, trace = max_activations(
                    base, policy, include_normal_play=True
                )
                maxima[policy] = maximum
                assert sum(x.startswith("use:") for x in trace) == maximum

            expected_entry = 1 + (sources + 1) // 2
            assert maxima == {
                "entry": expected_entry,
                "physical_copy": min(copies, expected_entry),
                "name": 1,
            }, (copies, sources, maxima)

            # The Brooklet card begins in hand, so without normal Stadium
            # play no different-named Stadium can first enter play.
            for policy in ("entry", "physical_copy", "name"):
                without_play, _ = max_activations(
                    base, policy, include_normal_play=False
                )
                assert without_play == 1
            print("tree_copies", copies, "sources", sources, maxima)


if __name__ == "__main__":
    test_witness()
    test_census()
    print("stadium_mixed_entry_frontier: PASS")
