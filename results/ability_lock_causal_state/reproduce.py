"""Reproduce causal continuity across verified Ability-lock precedence events."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_causal_state import (
    advance_lock_state,
    initialize_setup_lock_state,
    initialize_snapshot_lock_state,
)
from ability_lock_dependency_graph import AbilityLockSourceRef
from board_object_kernel import ToolAttachment, make_board, make_pokemon


def main() -> None:
    # Setup precedence persists when ordinary targets change while the source
    # dependency graph stays the same.
    empoleon = make_pokemon(
        "empoleon",
        "Empoleon V",
        print_id="swsh5-40",
        tags={"Basic", "Water", "RuleBox"},
    )
    wobbuffet = make_pokemon(
        "wobbuffet",
        "Wobbuffet",
        print_id="xy4-36",
        tags={"Basic", "Psychic"},
    )
    setup_player = make_board(empoleon)
    setup_opponent = make_board(wobbuffet)

    setup = initialize_setup_lock_state(
        setup_player,
        setup_opponent,
        first_player_owner="player",
    )
    assert setup.resolved
    assert setup.basis == "setup_first_player"
    assert setup.resolution.active_sources == (
        AbilityLockSourceRef("player", "empoleon"),
    )

    magnezone = make_pokemon(
        "zone",
        "Magnezone",
        print_id="bw8-46",
        tags={"Stage2", "Metal"},
    )
    expanded_player = make_board(empoleon, (magnezone,))
    setup_continues = advance_lock_state(
        setup,
        expanded_player,
        setup_opponent,
    )
    assert setup_continues.resolved
    assert setup_continues.basis == "setup_first_player"
    assert setup_continues.resolution.player_suppressed_object_ids == frozenset()

    # Snapshot resolution becomes a verified history-dependent cycle after the
    # Garbodor damage condition turns Cursed Land's reverse edge on.
    ting_lu = make_pokemon(
        "ting-lu",
        "Ting-Lu ex",
        print_id="sv2-127",
        tags={"Basic", "Fighting", "ex", "RuleBox"},
    )
    player = make_board(ting_lu)
    opponent_active = make_pokemon(
        "opponent-active",
        "Opponent Active",
        print_id="synthetic-opponent-active",
        tags={"Basic"},
    )
    garbodor = make_pokemon(
        "garbodor",
        "Garbodor",
        print_id="xy9-57",
        tags={"Stage1", "Psychic"},
        tool=ToolAttachment("garbodor-tool", "Float Stone"),
    )
    opponent = make_board(opponent_active, (garbodor,))

    initial = initialize_snapshot_lock_state(player, opponent)
    assert initial.resolved
    assert initial.basis == "snapshot"
    assert initial.resolution.active_sources == (
        AbilityLockSourceRef("opponent", "garbodor"),
    )

    damaged_garbodor = replace(garbodor, damage_counters=1)
    damaged_opponent = make_board(opponent_active, (damaged_garbodor,))
    damaged = advance_lock_state(initial, player, damaged_opponent)
    assert damaged.resolved
    assert damaged.basis == "verified_established"
    assert damaged.resolution.active_sources == (
        AbilityLockSourceRef("opponent", "garbodor"),
    )

    # A new ordinary target changes the final overlay without changing the
    # reciprocal source graph, so the verified winner persists.
    extra_target = make_pokemon(
        "extra",
        "Extra target",
        print_id="synthetic-extra",
        tags={"Basic"},
    )
    expanded_player = make_board(ting_lu, (extra_target,))
    persisted = advance_lock_state(damaged, expanded_player, damaged_opponent)
    assert persisted.resolved
    assert persisted.basis == "verified_established"
    assert persisted.resolution.player_suppressed_object_ids is not None
    assert {"ting-lu", "extra"}.issubset(
        persisted.resolution.player_suppressed_object_ids
    )

    # Removing the damage condition makes the graph acyclic again and returns
    # state ownership to pure snapshot resolution.
    cleared = advance_lock_state(persisted, expanded_player, opponent)
    assert cleared.resolved
    assert cleared.basis == "snapshot"
    assert cleared.resolution.active_sources == (
        AbilityLockSourceRef("opponent", "garbodor"),
    )

    print("ability_lock_causal_state regression: PASS")


if __name__ == "__main__":
    main()
