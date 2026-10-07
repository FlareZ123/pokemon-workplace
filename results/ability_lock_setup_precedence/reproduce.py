"""Reproduce official setup precedence for mutually suppressing Abilities."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_dependency_graph import (
    AbilityLockSourceRef,
    resolve_ability_lock_dependencies,
)
from ability_lock_setup_precedence import resolve_setup_ability_lock_precedence
from board_object_kernel import make_board, make_pokemon


def main() -> None:
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
    player = make_board(empoleon)
    opponent = make_board(wobbuffet)

    snapshot_only = resolve_ability_lock_dependencies(player, opponent)
    assert not snapshot_only.resolved
    assert set(snapshot_only.suppression_edges) == {
        (
            AbilityLockSourceRef("player", "empoleon"),
            AbilityLockSourceRef("opponent", "wobbuffet"),
        ),
        (
            AbilityLockSourceRef("opponent", "wobbuffet"),
            AbilityLockSourceRef("player", "empoleon"),
        ),
    }

    player_first = resolve_setup_ability_lock_precedence(
        player,
        opponent,
        first_player_owner="player",
    )
    assert player_first.resolved
    assert player_first.active_sources == (
        AbilityLockSourceRef("player", "empoleon"),
    )
    assert player_first.player_suppressed_object_ids == frozenset()
    assert player_first.opponent_suppressed_object_ids == frozenset({"wobbuffet"})

    opponent_first = resolve_setup_ability_lock_precedence(
        player,
        opponent,
        first_player_owner="opponent",
    )
    assert opponent_first.resolved
    assert opponent_first.active_sources == (
        AbilityLockSourceRef("opponent", "wobbuffet"),
    )
    assert opponent_first.player_suppressed_object_ids == frozenset({"empoleon"})
    assert opponent_first.opponent_suppressed_object_ids == frozenset()

    assert player_first.active_sources != opponent_first.active_sources

    print("ability_lock_setup_precedence regression: PASS")


if __name__ == "__main__":
    main()
