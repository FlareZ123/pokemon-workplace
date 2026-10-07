"""Reproduce dependency-aware composition of continuous Ability locks."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_dependency_graph import (
    AbilityLockSourceRef,
    resolve_ability_lock_dependencies,
)
from board_object_kernel import ToolAttachment, make_board, make_pokemon


def main() -> None:
    # Acyclic hierarchy: Garbotoxin suppresses Wobbuffet, while Bide Barricade
    # cannot suppress Psychic Garbodor.
    wob = make_pokemon(
        "wob",
        "Wobbuffet",
        print_id="xy4-36",
        tags={"Basic", "Psychic"},
    )
    zone = make_pokemon(
        "zone",
        "Magnezone",
        print_id="bw8-46",
        tags={"Stage2", "Metal"},
    )
    player = make_board(wob, (zone,))

    opp_active = make_pokemon("opp-active", "Opponent", print_id="opp")
    garb = make_pokemon(
        "garb",
        "Garbodor",
        print_id="xy9-57",
        tags={"Stage1", "Psychic"},
        tool=ToolAttachment("garb-tool", "Float Stone"),
    )
    opponent = make_board(opp_active, (garb,))

    hierarchy = resolve_ability_lock_dependencies(player, opponent)
    assert hierarchy.resolved
    assert hierarchy.unresolved_cycles == ()
    assert hierarchy.active_sources == (
        AbilityLockSourceRef("opponent", "garb"),
    )
    assert hierarchy.suppression_edges == (
        (
            AbilityLockSourceRef("opponent", "garb"),
            AbilityLockSourceRef("player", "wob"),
        ),
    )
    assert hierarchy.player_suppressed_object_ids is not None
    assert {"wob", "zone"}.issubset(hierarchy.player_suppressed_object_ids)

    # Circular dependency: opposing Active Neutralizing Gas and Lazy each
    # suppress the other's source. The engine refuses to choose a branch.
    weezing = make_pokemon(
        "weezing",
        "Galarian Weezing",
        print_id="swsh2-113",
        tags={"Stage1", "Darkness"},
    )
    zone2 = make_pokemon(
        "zone",
        "Magnezone",
        print_id="bw8-46",
        tags={"Stage2", "Metal"},
    )
    gas_player = make_board(weezing, (zone2,))

    slaking = make_pokemon(
        "slaking",
        "Slaking",
        print_id="sm7-115",
        tags={"Stage2", "Colorless"},
    )
    lazy_opponent = make_board(slaking)

    cycle = resolve_ability_lock_dependencies(gas_player, lazy_opponent)
    assert not cycle.resolved
    assert cycle.active_sources is None
    assert cycle.player_suppressed_object_ids is None
    assert cycle.opponent_suppressed_object_ids is None
    expected_cycle = tuple(
        sorted(
            (
                AbilityLockSourceRef("player", "weezing"),
                AbilityLockSourceRef("opponent", "slaking"),
            )
        )
    )
    assert cycle.unresolved_cycles == (expected_cycle,)
    assert set(cycle.suppression_edges) == {
        (
            AbilityLockSourceRef("player", "weezing"),
            AbilityLockSourceRef("opponent", "slaking"),
        ),
        (
            AbilityLockSourceRef("opponent", "slaking"),
            AbilityLockSourceRef("player", "weezing"),
        ),
    }

    # Opponent-effect protection can break the dependency cycle. A live
    # Stealthy Hood on Weezing blocks Lazy, leaving Neutralizing Gas as the
    # sole active suppressor.
    hooded_weezing = make_pokemon(
        "weezing",
        "Galarian Weezing",
        print_id="swsh2-113",
        tags={"Stage1", "Darkness"},
        tool=ToolAttachment("hood", "Stealthy Hood"),
    )
    hooded_player = make_board(hooded_weezing, (zone2,))
    hood_break = resolve_ability_lock_dependencies(
        hooded_player,
        lazy_opponent,
    )
    assert hood_break.resolved
    assert hood_break.active_sources == (
        AbilityLockSourceRef("player", "weezing"),
    )
    assert hood_break.opponent_suppressed_object_ids is not None
    assert "slaking" in hood_break.opponent_suppressed_object_ids

    # Jamming Tower removes Hood protection, recreating the cycle. The
    # dependency graph changes without any source or target leaving play.
    tower_cycle = resolve_ability_lock_dependencies(
        hooded_player,
        lazy_opponent,
        stadium_name="Jamming Tower",
    )
    assert not tower_cycle.resolved
    assert tower_cycle.unresolved_cycles == (expected_cycle,)

    print("ability_lock_dependency_graph regression: PASS")


if __name__ == "__main__":
    main()
