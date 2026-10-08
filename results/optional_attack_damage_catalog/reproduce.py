"""Reproduce exact optional attack-damage text family counts and witnesses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from optional_attack_damage_catalog import build_catalog, optional_attack_profile


def main() -> None:
    catalog = build_catalog(ROOT / "resources")
    assert catalog["print_rows"] == 71, catalog["print_rows"]
    assert catalog["unique_effect_signatures"] == 39
    assert catalog["unique_card_names"] == 37
    assert catalog["variable_bonus_prints"] == 10
    assert catalog["variable_bonus_signatures"] == 3

    rows = catalog["rows"]
    cetitan = [r for r in rows if r["card_name"] == "Cetitan ex"]
    assert {r["card_id"] for r in cetitan} == {"sv10-65", "sv10-210"}
    assert all(
        r["base_damage"] == r["bonus_per_unit"] == 140
        and not r["variable_bonus"]
        and r["cost_family"] == "stadium_discard"
        for r in cetitan
    )
    roaring = [r for r in rows if r["card_name"] == "Roaring Moon ex"]
    assert len(roaring) == 6
    assert all(r["base_damage"] == 100 and r["bonus_per_unit"] == 120 for r in roaring)

    variable = {r["attack_name"] for r in rows if r["variable_bonus"]}
    assert variable == {"Max Lance", "Max Beating", "Magma Eruption"}

    # This is a conservative text family, excluding an opponent-controlled
    # damage modifier and any attack lacking the exact initial optional form.
    assert optional_attack_profile({
        "name": "Whisk Away",
        "damage": "30+",
        "text": (
            "Your opponent reveals his or her hand. Choose a Pokémon you find "
            "there and put it on the bottom your opponent's deck. If you do, "
            "this attack does 30 more damage."
        ),
    }) is None

    summary = {key: value for key, value in catalog.items() if key != "rows"}
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("optional attack-damage catalog: PASS")


if __name__ == "__main__":
    main()
