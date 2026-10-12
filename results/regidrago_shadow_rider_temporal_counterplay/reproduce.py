"""Reproduce a published champion reference using bundled English card data.

Run as a single Python file from any working directory on Windows or elsewhere.
Snapshot eligibility is not an assertion of all future regional tournament rules.
"""

from collections import Counter
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
RESULT = Path(__file__).resolve().parent
DECK = json.loads((RESULT / "shadow_rider_aichi_2026.json").read_text(encoding="utf-8"))

printed = {
    card["id"]: card
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json"))
    for card in json.loads(path.read_text(encoding="utf-8"))
}

expected = {"Pokémon": 18, "Trainer": 31, "Energy": 11}
totals = Counter()
subtypes = Counter()
for group, entries in DECK["groups"].items():
    for entry in entries:
        count, display, card_id = entry["count"], entry["name"], entry["print_id"]
        card = printed[card_id]
        catalog_name = ("Battle Compressor Team Flare Gear"
                        if display == "Battle Compressor" else display)
        assert card["name"] == catalog_name, (display, card_id, card["name"])
        assert card["supertype"] == group, (display, group)
        assert card.get("legalities", {}).get("expanded") == "Legal", card_id
        assert count > 0, display
        totals[group] += count
        subtypes.update({kind: count for kind in card.get("subtypes", [])})
        if group != "Energy" or "Basic" not in card.get("subtypes", []):
            assert count <= 4, (display, count)
        print(f"{group:7} {count:2} x {display:32} {card_id:18} Expanded: Legal")

assert totals == expected, (totals, expected)
assert sum(totals.values()) == 60
assert subtypes["ACE SPEC"] == 1
assert subtypes["Radiant"] == 1

critical = {
    "Mimikyu": ("sm2-58", "attacks", "Copycat"),
    "Dialga-GX": ("sm5-100", "attacks", "Timeless-GX"),
    "Girafarig": ("sm8-94", "attacks", "Get Lost"),
    "Marshadow": ("sm10-81", "abilities", "Resetting Hole"),
    "Latias ex": ("sv8-76", "abilities", "Skyliner"),
    "Shadow Rider Calyrex VMAX": ("swsh6-75", "abilities", "Underworld Door"),
}
pokemon = {entry["name"]: entry["print_id"] for entry in DECK["groups"]["Pokémon"]}
for name, (card_id, field, effect_name) in critical.items():
    assert pokemon[name] == card_id, (name, pokemon[name], card_id)
    assert effect_name in [a["name"] for a in printed[card_id].get(field, [])]

print(f"PASS: {sum(totals.values())} cards; Pokémon {totals['Pokémon']}, "
      f"Trainer {totals['Trainer']}, Energy {totals['Energy']}; "
      "one ACE SPEC, one Radiant, and six critical print/effect identities.")
