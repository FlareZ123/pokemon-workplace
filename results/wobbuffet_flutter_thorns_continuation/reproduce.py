"""Test differential Thorns counter-actions for Wobbuffet and Flutter Mane."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_dependency_graph import AbilityLockSourceRef, resolve_ability_lock_dependencies
from board_object_kernel import ToolAttachment, make_board, make_pokemon

WOB = AbilityLockSourceRef("player", "wob")
FLUTTER = AbilityLockSourceRef("player", "flutter")
THORNS = AbilityLockSourceRef("opponent", "thorns")


def source(card_id: str) -> dict:
    setid = card_id.split("-", 1)[0]
    cards = json.loads((ROOT / "resources" / "cards" / "en" / f"{setid}.json").read_text(encoding="utf-8"))
    return next(row for row in cards if row["id"] == card_id)


def boards(
    active_kind: str, *, hood_on_thorns: bool = False
):
    rider = make_pokemon("rider", "Shadow Rider Calyrex VMAX",
                         print_id="swsh6-75", tags={"Psychic", "RuleBox", "VMAX"})
    radiant = make_pokemon("radiant", "Radiant Eternatus",
                           print_id="swsh12pt5-105", tags={"Dragon", "Basic", "RuleBox"})
    latias = make_pokemon("latias", "Latias ex", print_id="sv8-76",
                          tags={"Psychic", "Basic", "RuleBox"})
    wob = make_pokemon("wob", "Wobbuffet", print_id="xy4-36",
                       tags={"Psychic", "Basic"})
    flutter = make_pokemon("flutter", "Flutter Mane", print_id="sv5-78",
                           tags={"Psychic", "Basic", "Ancient"})
    dummy = make_pokemon("dummy", "Dummy", tags={"Basic"})
    all_ours = (rider, radiant, latias, wob, flutter, dummy)
    active_id = {"wob": "wob", "flutter": "flutter", "dummy": "dummy"}[active_kind]
    active = next(row for row in all_ours if row.object_id == active_id)
    player = make_board(
        active,
        tuple(row for row in all_ours if row.object_id != active_id)
    )
    thorns = make_pokemon(
        "thorns", "Iron Thorns ex", print_id="sv6-77",
        tags={"Basic", "Future", "RuleBox", "Lightning"},
        tool=ToolAttachment("hood", "Stealthy Hood") if hood_on_thorns else None
    )
    opponent = make_board(thorns)
    return player, opponent


def check() -> None:
    ability_texts = (
        ("xy4-36", "Bide Barricade", "except for Psychic Pokémon"),
        ("sv5-78", "Midnight Fluttering", "your opponent's Active Pokémon"),
        ("sv8pt5-43", "Midnight Fluttering", "your opponent's Active Pokémon"),
        ("svp-97", "Midnight Fluttering", "your opponent's Active Pokémon"),
        ("swsh12pt5-105", "Climactic Gate", "your turn ends"),
        ("sv6-77", "Initialization", "except for Future Pokémon"),
        ("swsh6-75", "Underworld Door", "Benched Psychic Pokémon"),
        ("sv8-76", "Skyliner", "no Retreat Cost"),
    )
    for cid, name, fragment in ability_texts:
        card = source(cid)
        assert any(row["name"] == name and fragment in row["text"]
                   for row in card.get("abilities") or ()), cid

    no_counter = resolve_ability_lock_dependencies(*boards("dummy"))
    assert no_counter.resolved and no_counter.active_sources == (THORNS,)
    assert {"rider", "radiant", "latias"}.issubset(
        no_counter.player_suppressed_object_ids
    )

    wob = resolve_ability_lock_dependencies(*boards("wob"))
    assert wob.resolved and wob.active_sources == (WOB,)
    assert wob.suppression_edges == ((WOB, THORNS),)
    assert "thorns" in wob.opponent_suppressed_object_ids
    assert "radiant" in wob.player_suppressed_object_ids
    assert "rider" not in wob.player_suppressed_object_ids
    assert "latias" not in wob.player_suppressed_object_ids

    flutter = resolve_ability_lock_dependencies(*boards("flutter"))
    assert flutter.resolved and flutter.active_sources == (FLUTTER,)
    assert flutter.suppression_edges == ((FLUTTER, THORNS),)
    assert "radiant" not in flutter.player_suppressed_object_ids
    assert "rider" not in flutter.player_suppressed_object_ids
    assert "latias" not in flutter.player_suppressed_object_ids
    assert "thorns" in flutter.opponent_suppressed_object_ids

    for active in ("wob", "flutter"):
        hooded = resolve_ability_lock_dependencies(
            *boards(active, hood_on_thorns=True)
        )
        assert hooded.resolved
        assert set(hooded.active_sources) == {
            THORNS, WOB if active == "wob" else FLUTTER
        }
        assert hooded.suppression_edges == ()
        assert {"rider", "radiant", "latias"}.issubset(
            hooded.player_suppressed_object_ids
        )
        tower = resolve_ability_lock_dependencies(
            *boards(active, hood_on_thorns=True),
            stadium_name="Jamming Tower"
        )
        assert tower.resolved
        assert tower.active_sources == (
            WOB if active == "wob" else FLUTTER,
        )
    print(json.dumps({
        "wobbuffet_releases_underworld_door": True,
        "wobbuffet_still_suppresses_radiant_climactic_gate": True,
        "flutter_releases_underworld_door_and_climactic_gate": True,
        "both_counters_stopped_by_opposing_thorns_hood": True,
        "jamming_tower_restores_both_counter_sources": True,
        "validation": "PASS",
        "match_wins_calculated": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    check()
