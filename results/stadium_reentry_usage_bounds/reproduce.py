"""Reproduce conditional Stadium usage bounds across physical re-entry paths."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_expanded_legality_baseline import classify_effective_legality
from stadium_entry_channels import StadiumCopy, StadiumEntryState
from stadium_reentry_usage_bounds import (
    StadiumReentryState,
    activate,
    can_activate,
    max_activations,
    teleport_successors,
)
from turn_action_budget import TurnActionBudget


def check_cards() -> None:
    for set_id, card_id, name in (
        ("xy3", "xy3-41", "Gothitelle"),
        ("sv7", "sv7-136", "Grand Tree"),
        ("sm2", "sm2-120", "Brooklet Hill"),
    ):
        cards = json.loads(
            (ROOT / "resources" / "cards" / "en" / (set_id + ".json"))
            .read_text(encoding="utf-8")
        )
        card = next(x for x in cards if x["id"] == card_id)
        assert card["name"] == name
        assert classify_effective_legality(card)[0] == "Legal"
        if name == "Gothitelle":
            assert "put a Stadium card with a different name" in str(card["abilities"])
        if name == "Grand Tree":
            assert any("Once during each player's turn" in s for s in card["rules"])


def make_state(n_sources: int, tree_copies: int) -> StadiumReentryState:
    assert 0 <= n_sources <= 4
    assert tree_copies in (1, 2)
    discard = (StadiumCopy("brooklet-1", "Brooklet Hill"),)
    if tree_copies == 2:
        discard += (StadiumCopy("tree-2", "Grand Tree"),)
    entry = StadiumEntryState(
        budget=TurnActionBudget(stadium_plays_used=1),
        in_play=StadiumCopy("tree-1", "Grand Tree"),
        discard=discard,
        teleport_room_sources=frozenset(
            "goth-" + str(i) for i in range(n_sources)
        ),
    )
    return StadiumReentryState(entry)


def run_census() -> None:
    for copies in (1, 2):
        for n in range(5):
            state = make_state(n, copies)
            max_by_policy = {}
            for policy in ("entry", "physical_copy", "name"):
                count, trace = max_activations(state, policy)
                max_by_policy[policy] = count
                assert len([x for x in trace if x.startswith("use:")]) == count
            assert max_by_policy["entry"] == 1 + n // 2
            assert max_by_policy["physical_copy"] == min(
                copies, 1 + n // 2
            )
            assert max_by_policy["name"] == 1
            print(
                "copies", copies,
                "gothitelle", n,
                "max_uses", max_by_policy,
            )


def run_identity_witnesses() -> None:
    first = make_state(2, 1)
    first = activate(first, "entry")
    assert first is not None

    brooklet = next(
        x for x in teleport_successors(first, "goth-0")
        if x.entry.in_play is not None and x.entry.in_play.name == "Brooklet Hill"
    )
    returned = next(
        x for x in teleport_successors(brooklet, "goth-1")
        if x.entry.in_play is not None and x.entry.in_play.copy_id == "tree-1"
    )
    assert returned.epoch == 2
    assert returned.entry.budget.stadium_plays_used == 1
    assert returned.entry.teleport_room_used == frozenset({"goth-0", "goth-1"})
    assert not can_activate(returned, "physical_copy")
    assert not can_activate(returned, "name")
    assert can_activate(returned, "entry")
    twice = activate(returned, "entry")
    assert twice is not None and len(twice.uses) == 2
    assert len({x.copy_id for x in twice.uses}) == 1
    assert len({x.epoch for x in twice.uses}) == 2

    # In contrast, the documented different-copy situation has no ambiguity
    # between the entry and physical-copy policies.
    first = make_state(2, 2)
    first = activate(first, "entry")
    assert first is not None
    brooklet = next(
        x for x in teleport_successors(first, "goth-0")
        if x.entry.in_play is not None and x.entry.in_play.name == "Brooklet Hill"
    )
    second = next(
        x for x in teleport_successors(brooklet, "goth-1")
        if x.entry.in_play is not None and x.entry.in_play.copy_id == "tree-2"
    )
    assert can_activate(second, "entry")
    assert can_activate(second, "physical_copy")
    assert not can_activate(second, "name")
    physical = activate(second, "physical_copy")
    assert physical is not None
    assert [use.copy_id for use in physical.uses] == ["tree-1", "tree-2"]

    # The adapter cannot perform a third teleport with either already-used source.
    assert teleport_successors(second, "goth-0") == ()
    assert teleport_successors(second, "goth-1") == ()
    initial_ids = {"tree-1", "tree-2", "brooklet-1"}
    final_ids = {x.copy_id for x in physical.entry.discard}
    assert physical.entry.in_play is not None
    final_ids.add(physical.entry.in_play.copy_id)
    assert initial_ids == final_ids


if __name__ == "__main__":
    check_cards()
    run_identity_witnesses()
    run_census()
    print("stadium_reentry_usage_bounds: PASS")
