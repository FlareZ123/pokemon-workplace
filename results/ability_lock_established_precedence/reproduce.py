"""Reproduce the official Garbotoxin / Cursed Land precedence ruling."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_dependency_graph import (
    AbilityLockSourceRef,
    resolve_ability_lock_dependencies,
)
from ability_lock_established_precedence import (
    resolve_verified_established_precedence,
)
from board_object_kernel import ToolAttachment, make_board, make_pokemon
from single_source_ability_lock_geometry import (
    single_source_suppressed_object_ids,
)


def main() -> None:
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

    garb_ref = AbilityLockSourceRef("opponent", "garbodor")
    ting_ref = AbilityLockSourceRef("player", "ting-lu")

    before_damage = resolve_ability_lock_dependencies(player, opponent)
    assert before_damage.resolved
    assert before_damage.active_sources == (garb_ref,)
    assert before_damage.suppression_edges == ((garb_ref, ting_ref),)

    damaged_garbodor = replace(garbodor, damage_counters=1)
    damaged_opponent = make_board(opponent_active, (damaged_garbodor,))

    snapshot_after_damage = resolve_ability_lock_dependencies(
        player,
        damaged_opponent,
    )
    assert not snapshot_after_damage.resolved
    assert set(snapshot_after_damage.suppression_edges) == {
        (garb_ref, ting_ref),
        (ting_ref, garb_ref),
    }

    after_damage = resolve_verified_established_precedence(
        before_damage,
        player,
        damaged_opponent,
    )
    assert after_damage.resolved
    assert after_damage.active_sources == (garb_ref,)
    assert after_damage.player_suppressed_object_ids is not None
    assert "ting-lu" in after_damage.player_suppressed_object_ids
    assert after_damage.opponent_suppressed_object_ids is not None
    assert "garbodor" not in after_damage.opponent_suppressed_object_ids

    # Cursed Land itself is damage-gated and explicitly exempts Pokemon ex.
    regular = make_pokemon(
        "regular",
        "Damaged regular Pokemon",
        print_id="synthetic-regular",
        tags={"Basic"},
        damage_counters=1,
    )
    pokemon_ex = make_pokemon(
        "pokemon-ex",
        "Damaged Pokemon ex",
        print_id="synthetic-ex",
        tags={"Basic", "ex", "RuleBox"},
        damage_counters=1,
    )
    target_board = make_board(regular, (pokemon_ex,))
    cursed_targets = single_source_suppressed_object_ids(
        target_board,
        player,
        source_owner="opponent",
        source_object_id="ting-lu",
    )
    assert cursed_targets == frozenset({"regular"})

    print("ability_lock_established_precedence regression: PASS")


if __name__ == "__main__":
    main()
