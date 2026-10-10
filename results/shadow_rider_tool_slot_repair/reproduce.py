"""Regression for same-turn Tool-slot release, Stadium and Item restrictions."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from shadow_rider_post_trifrost_recovery import RecoveryScenario  # noqa: E402
from shadow_rider_tool_slot_repair import (  # noqa: E402
    ToolConflictScenario, find_tool_slot_recovery,
)


def card(set_id: str, ident: str) -> dict:
    rows = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json")
        .read_text(encoding="utf-8")
    )
    return next(row for row in rows if row["id"] == ident)


def test_cards() -> None:
    forest = card("swsh12", "swsh12-156")
    floatstone = card("xy8", "xy8-137")
    blower = card("sm2", "sm2-125")
    jamming = card("sv6", "sv6-153")
    valley = card("xy4", "xy4-93")
    sky = card("xy6", "xy6-89")
    assert "Pokémon Tool" in forest["subtypes"]
    assert forest["abilities"][0]["name"] == "Star Alchemy"
    assert "search your deck for a card" in forest["abilities"][0]["text"]
    assert "Pokémon Tool" in floatstone["subtypes"]
    assert "has no Retreat Cost" in floatstone["rules"][1]
    assert blower["subtypes"] == ["Item"]
    assert "Choose up to 2 in any combination of Pokémon Tool cards and Stadium cards" in blower["rules"][0]
    assert "Pokémon Tools attached to each Pokémon" in jamming["rules"][0]
    assert "have no effect" in jamming["rules"][0]
    assert "cost Colorless less" in valley["rules"][0]
    assert sky["subtypes"] == ["Stadium"]


def main() -> None:
    test_cards()
    baseline = ToolConflictScenario(field_blower_in_hand=True)
    in_hand = find_tool_slot_recovery(baseline)
    assert in_hand is not None
    assert in_hand[0] == "Field Blower: discard incumbent Tool"
    assert "Free retreat using Float Stone; promote Mimikyu" in in_hand

    under_lock = replace(
        baseline, recovery=replace(baseline.recovery, item_play_enabled=False)
    )
    assert find_tool_slot_recovery(under_lock) is None

    fetched = replace(
        baseline, field_blower_in_hand=False, field_blower_in_deck=True
    )
    from_forest = find_tool_slot_recovery(fetched)
    assert from_forest is not None
    assert from_forest[0] == "Forest Seal Stone Star Alchemy: search Field Blower"
    assert from_forest[1] == "Field Blower: discard incumbent Tool"
    assert find_tool_slot_recovery(replace(
        fetched, forest_star_alchemy_unused=False
    )) is None

    jammed = replace(baseline, jamming_tower_live=True)
    double_clear = find_tool_slot_recovery(jammed)
    assert double_clear is not None
    assert double_clear[0] == (
        "Field Blower: discard incumbent Tool and Jamming Tower"
    )
    no_blow_before_stadium = replace(
        fetched, jamming_tower_live=True
    )
    assert find_tool_slot_recovery(no_blow_before_stadium) is None
    via_stadium = replace(
        no_blow_before_stadium, replacement_stadium_in_hand="Dimension Valley"
    )
    revived_forest = find_tool_slot_recovery(via_stadium)
    assert revived_forest is not None
    assert revived_forest[0] == "Play Dimension Valley to replace Jamming Tower"
    assert revived_forest[1] == "Forest Seal Stone Star Alchemy: search Field Blower"
    assert revived_forest[2] == "Field Blower: discard incumbent Tool"

    tool_free = replace(
        via_stadium,
        incumbent_tool="None", field_blower_in_deck=False,
        recovery=replace(via_stadium.recovery, item_play_enabled=False)
    )
    item_lock_stadium = find_tool_slot_recovery(tool_free)
    assert item_lock_stadium is not None
    assert item_lock_stadium[0] == "Play Dimension Valley to replace Jamming Tower"
    assert "Free retreat using Float Stone; promote Mimikyu" in item_lock_stadium
    assert find_tool_slot_recovery(replace(
        tool_free, replacement_stadium_in_hand=None
    )) is None

    assert find_tool_slot_recovery(replace(
        via_stadium,
        recovery=replace(via_stadium.recovery, item_play_enabled=False)
    )) is None

    # A non-Tool route can still work with a blocked Active Tool slot.
    alternative = replace(
        baseline, field_blower_in_hand=False,
        recovery=replace(
            baseline.recovery,
            psychic_in_hand=2, psychic_in_discard=0,
            tulip_available=False, float_stone_available=False,
            acerola_available=False
        ),
    )
    non_tool = find_tool_slot_recovery(alternative)
    assert non_tool is not None
    assert "Guzma: opponent switch then promote Mimikyu" in non_tool

    print(json.dumps({
        "field_blower_hand_route": list(in_hand),
        "forest_searches_field_blower_route": list(from_forest),
        "simultaneous_tool_stadium_discard_route": list(double_clear),
        "replacement_stadium_then_star_alchemy_route": list(revived_forest),
        "item_locked_but_stadium_and_tool_allowed": list(item_lock_stadium),
        "alternative_night_stretcher_guzma": list(non_tool),
        "negative_item_tool_stadium_guards": True,
    }, indent=2))


if __name__ == "__main__":
    main()
