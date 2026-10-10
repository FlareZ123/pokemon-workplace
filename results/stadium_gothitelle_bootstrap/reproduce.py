"""Exact conditional Grand Tree -> Gothitelle -> Teleport Room feedback census."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from stadium_entry_channels import StadiumCopy, StadiumEntryState
from stadium_gothitelle_bootstrap import BootstrapState, maximize_built
from stadium_reentry_usage_bounds import StadiumReentryState
from turn_action_budget import TurnActionBudget


def initial(n: int, reserved: int, copies: int, normal: bool) -> BootstrapState:
    assert 0 <= n <= 4 and 0 <= reserved <= 4 and n + reserved <= 6
    assert copies in (1, 2)
    ready = min(4 - n, 6 - n - reserved)
    brooklet = StadiumCopy("brooklet", "Brooklet Hill")
    discard = (StadiumCopy("tree-2", "Grand Tree"),) if copies == 2 else ()
    if not normal:
        discard += (brooklet,)
    entry = StadiumEntryState(
        budget=TurnActionBudget(stadium_plays_used=int(not normal)),
        in_play=StadiumCopy("tree-1", "Grand Tree"),
        hand=(brooklet,) if normal else (),
        discard=discard,
        teleport_room_sources=frozenset(
            "original-" + str(i) for i in range(n)
        ),
    )
    return BootstrapState(
        stadium=StadiumReentryState(entry), ready=ready, other=reserved
    )


def census() -> None:
    cases = 0
    for copies in (1, 2):
        for normal in (False, True):
            for reserved in range(5):
                for n in range(5):
                    if n + reserved > 6:
                        continue
                    board = initial(n, reserved, copies, normal)
                    available_basics = board.ready
                    for policy in ("entry", "physical_copy"):
                        actual, trace = maximize_built(
                            board, policy, allow_play=normal
                        )
                        # Each activation creates one new source. One ordinary
                        # replacement costs one Teleport Room use; subsequent
                        # returns require two source uses. With no ordinary play
                        # each return requires two. Before kth activation,
                        # exactly k-1 new sources have been created.
                        source_bound = n + (2 if normal else 1)
                        if policy == "physical_copy":
                            source_bound = min(source_bound, copies)
                        expected = min(available_basics, source_bound)
                        assert actual == expected, (
                            copies, normal, reserved, n,
                            policy, actual, expected, trace
                        )
                        assert trace.count("evolve") == actual
                        cases += 1
    assert cases == 176

    # One fresh Gothitelle can itself supply the only Teleport Room action
    # in the mixed route, even when no Gothitelle existed initially.
    value, route = maximize_built(initial(0, 0, 1, True), "entry")
    assert value == 2
    assert route[0] == "evolve"
    assert "ordinary-play" not in route  # trace uses the concise "play" token
    assert "play" in route
    assert "teleport:built-1" in route

    # Legal four-copy family cap changes the apparent unconstrained optimum.
    assert [
        maximize_built(initial(n, 0, 1, True), "entry")[0]
        for n in range(5)
    ] == [2, 3, 2, 1, 0]
    assert [
        maximize_built(initial(n, 0, 1, False), "entry", allow_play=False)[0]
        for n in range(5)
    ] == [1, 2, 2, 1, 0]
    print("bootstrap cases", cases)
    print("mixed first-turn-source counts n=0..4", [2, 3, 2, 1, 0])
    print("all-Teleport source counts n=0..4", [1, 2, 2, 1, 0])


if __name__ == "__main__":
    census()
    print("stadium_gothitelle_bootstrap: PASS")
