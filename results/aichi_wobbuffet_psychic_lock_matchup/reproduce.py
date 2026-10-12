"""Matchup-specific full-deck Wobbuffet Ability-suppression inventory."""

from collections import Counter
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
printed = {
    card["id"]: card
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json"))
    for card in json.loads(path.read_text(encoding="utf-8"))
}
decks = {
    "regidrago": json.loads((ROOT / "results" / "regidrago_aichi_top10_playable" /
                            "yoshioka_regidrago_2026.json").read_text(encoding="utf-8")),
    "shadow_rider": json.loads((ROOT / "results" / "regidrago_shadow_rider_temporal_counterplay" /
                               "shadow_rider_aichi_2026.json").read_text(encoding="utf-8")),
}
wobb = printed["xy4-36"]
barricade = next(a["text"] for a in wobb["abilities"] if a["name"] == "Bide Barricade")
assert wobb["types"] == ["Psychic"]
assert "If this Pokémon is your Active Pokémon" in barricade
assert "in each player's hand" in barricade
assert "in each player's discard pile" in barricade
assert "except for Psychic Pokémon" in barricade

summaries = {}
for name, deck in decks.items():
    assert sum(e["count"] for group in deck["groups"].values() for e in group) == 60
    summary = Counter()
    suppressed = []
    exempt = []
    for entry in deck["groups"]["Pokémon"]:
        source = printed[entry["print_id"]]
        assert source["name"] == entry["name"], (source["id"], entry["name"])
        if not source.get("abilities"):
            continue
        n = entry["count"]
        summary["ability_bearing"] += n
        if "Psychic" in source["types"]:
            summary["exempt"] += n
            exempt.append((source["name"], n))
        else:
            summary["suppressed"] += n
            suppressed.append((source["name"], n))
    summaries[name] = summary
    print(name, ":", dict(summary))
    print("  suppressed:", suppressed)
    print("  exempt:", exempt)

assert summaries["regidrago"] == {
    "ability_bearing": 11, "suppressed": 7, "exempt": 4,
}
assert summaries["shadow_rider"] == {
    "ability_bearing": 11, "suppressed": 1, "exempt": 10,
}
named = [
    ("swsh6-75", "Psychic", "Underworld Door", True),
    ("swsh12-136", "Dragon", "Legacy Star", False),
    ("swsh11-136", "Dragon", "Moisture Star", False),
    ("sv8-76", "Psychic", "Skyliner", True),
    ("sm10-57", "Lightning", "Dedechange", False),
    ("sv2-169", "Colorless", "Squawk and Seize", False),
    ("swsh12pt5-105", "Dragon", "Climactic Gate", False),
]
for id_, ptype, ability, survives in named:
    card = printed[id_]
    assert ptype in card["types"], (id_, card["types"])
    assert ability in [a["name"] for a in card.get("abilities", [])], id_
    assert ("Psychic" in card["types"]) == survives

assert "Your Basic Pokémon" in printed["sv8-76"]["abilities"][0]["text"]
assert printed["xy4-36"]["stage"] == "Basic"
assert printed["swsh12-136"]["stage"] == "VSTAR"
print("PASS: per-print, copy-weighted Bide Barricade suppression counts and type gates.")
