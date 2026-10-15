"""Conditional multi-source Ability-lock regression for Muk and Iron Thorns ex."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_dependency_graph import AbilityLockSourceRef, resolve_ability_lock_dependencies
from board_object_kernel import ToolAttachment, make_board, make_pokemon
from build_expanded_legality_baseline import classify_effective_legality

MUK = AbilityLockSourceRef("player", "muk")
THORNS = AbilityLockSourceRef("opponent", "thorns")
THORNS_PRINTS = ("sv6-77", "sv6-196", "sv8pt5-32")


def card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    cards = json.loads((ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8"))
    return next(row for row in cards if row["id"] == card_id)


def verify_text() -> None:
    muk = card("sm1-58")
    assert classify_effective_legality(muk)[0] == "Legal"
    assert "Stage 1" in muk["subtypes"]
    assert muk["abilities"][0]["name"] == "Power of Alchemy"
    assert "in each player's hand" in muk["abilities"][0]["text"]
    assert "in each player's discard pile" in muk["abilities"][0]["text"]
    for cid in THORNS_PRINTS:
        thorns = card(cid)
        assert classify_effective_legality(thorns)[0] == "Legal"
        assert {"Basic", "Future", "ex"} <= set(thorns["subtypes"])
        text = next(a["text"] for a in thorns["abilities"] if a["name"] == "Initialization")
        assert "in the Active Spot" in text
        assert "Pokémon with a Rule Box" in text
        assert "except for Future Pokémon" in text
    for cid, name in (("swsh6-75", "Underworld Door"),
                      ("swsh8-185", "Fusion Strike System"),
                      ("sv3-164", "Quick Search")):
        row = card(cid)
        assert classify_effective_legality(row)[0] == "Legal"
        assert any(a["name"] == name for a in row["abilities"])


def boards(muk: bool, *, thorns_tool: str | None = None,
           genesect_tool: str | None = None, thorns_active: bool = True):
    ours = [
        make_pokemon("rider", "Shadow Rider Calyrex VMAX",
                     print_id="swsh6-75", tags={"VMAX", "RuleBox", "Psychic"}),
        make_pokemon("own-genesect", "Genesect V",
                     print_id="swsh8-185", tags={"Basic", "RuleBox"}),
    ]
    if muk:
        ours.append(make_pokemon("muk", "Alolan Muk",
                                 print_id="sm1-58", tags={"Stage1", "Darkness"}))
    player = make_board(make_pokemon("own-active", "Our Active", tags={"Basic"}), ours)

    thorns = make_pokemon(
        "thorns", "Iron Thorns ex", print_id="sv6-77",
        tags={"Basic", "RuleBox", "Future"},
        tool=ToolAttachment("thorns-tool", thorns_tool) if thorns_tool else None,
    )
    genesect = make_pokemon(
        "enemy-genesect", "Genesect V", print_id="swsh8-185",
        tags={"Basic", "RuleBox"},
        tool=ToolAttachment("genesect-tool", genesect_tool) if genesect_tool else None,
    )
    pidgeot = make_pokemon("pidgeot", "Pidgeot ex", print_id="sv3-164",
                           tags={"Stage2", "RuleBox"})
    opponent = (
        make_board(thorns, (genesect, pidgeot)) if thorns_active
        else make_board(make_pokemon("enemy-active", "Opponent", tags={"Basic"}),
                        (thorns, genesect, pidgeot))
    )
    return player, opponent


def main() -> None:
    verify_text()

    before = resolve_ability_lock_dependencies(*boards(False))
    assert before.resolved and before.active_sources == (THORNS,)
    assert before.player_suppressed_object_ids == frozenset({"rider", "own-genesect"})
    assert before.opponent_suppressed_object_ids == frozenset({"enemy-genesect", "pidgeot"})

    after = resolve_ability_lock_dependencies(*boards(True))
    assert after.resolved and after.active_sources == (MUK,)
    assert after.suppression_edges == ((MUK, THORNS),)
    assert after.player_suppressed_object_ids == frozenset({"own-active", "own-genesect"})
    assert after.opponent_suppressed_object_ids == frozenset({"thorns", "enemy-genesect"})
    assert "rider" not in after.player_suppressed_object_ids
    assert "pidgeot" not in after.opponent_suppressed_object_ids

    hood = resolve_ability_lock_dependencies(*boards(True, thorns_tool="Stealthy Hood"))
    assert hood.resolved and set(hood.active_sources) == {MUK, THORNS}
    assert hood.suppression_edges == ()
    assert "rider" in hood.player_suppressed_object_ids
    assert "pidgeot" in hood.opponent_suppressed_object_ids
    assert "thorns" not in hood.opponent_suppressed_object_ids

    tower = resolve_ability_lock_dependencies(
        *boards(True, thorns_tool="Stealthy Hood"),
        stadium_name="Jamming Tower",
    )
    assert tower.resolved and tower.active_sources == (MUK,)
    assert tower.suppression_edges == ((MUK, THORNS),)
    assert "rider" not in tower.player_suppressed_object_ids

    protected = resolve_ability_lock_dependencies(
        *boards(True, genesect_tool="Stealthy Hood")
    )
    assert protected.resolved and protected.active_sources == (MUK,)
    assert "enemy-genesect" not in protected.opponent_suppressed_object_ids
    assert "own-genesect" in protected.player_suppressed_object_ids

    benched = resolve_ability_lock_dependencies(*boards(True, thorns_active=False))
    assert benched.resolved and benched.active_sources == (MUK,)
    assert benched.suppression_edges == ()

    print(json.dumps({
        "exact_thorns_prints_checked": THORNS_PRINTS,
        "before_muk_live": ["Initialization"],
        "after_muk_live": ["Power of Alchemy"],
        "restored_evolution_abilities": ["Underworld Door", "Quick Search"],
        "basic_ability_suppressed": "Fusion Strike System",
        "hood_on_thorns_keeps_initialization_active": True,
        "jamming_tower_restores_muk_precedence": True,
        "hood_on_opposing_genesect_protects_that_ability": True,
        "thorns_benched_initialization_inactive": True,
        "estimated_match_wins": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
