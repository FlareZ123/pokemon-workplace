"""Reproduce a published 2026 Aichi Regidrago 60-card Expanded reference."""

from collections import Counter
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
RESULT = Path(__file__).resolve().parent
DATA = json.loads((RESULT / "yoshioka_regidrago_2026.json").read_text(encoding="utf-8"))
printed = {
    card["id"]: card
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json"))
    for card in json.loads(path.read_text(encoding="utf-8"))
}
expected = {"Pokémon": 20, "Trainer": 30, "Energy": 10}
totals = Counter()
subtypes = Counter()
for group, entries in DATA["groups"].items():
    for entry in entries:
        count, name, print_id = entry["count"], entry["name"], entry["print_id"]
        card = printed[print_id]
        source_name = ("Battle Compressor Team Flare Gear"
                       if name == "Battle Compressor" else name)
        assert card["name"] == source_name, (name, print_id, card["name"])
        assert card["supertype"] == group, (name, group)
        assert card.get("legalities", {}).get("expanded") == "Legal", print_id
        assert count > 0, name
        if group != "Energy" or "Basic" not in card.get("subtypes", []):
            assert count <= 4, (name, count)
        totals[group] += count
        subtypes.update({kind: count for kind in card.get("subtypes", [])})
        print(f"{group:7} {count:2} x {name:32} {print_id:18} Expanded: Legal")
assert totals == expected, (totals, expected)
assert sum(totals.values()) == 60
assert subtypes["ACE SPEC"] == 1, subtypes
assert subtypes["Radiant"] == 0, subtypes

pokemon = {c["name"]: c["print_id"] for c in DATA["groups"]["Pokémon"]}
trainer = {c["name"]: c["count"] for c in DATA["groups"]["Trainer"]}
energy = {c["name"]: c["count"] for c in DATA["groups"]["Energy"]}
assert pokemon["Regidrago VSTAR"] == "swsh12-136"
assert pokemon["Budew"] == "me2pt5-16"
assert pokemon["Wobbuffet"] == "xy4-36"
assert printed[pokemon["Budew"]]["attacks"][0]["name"] == "Itchy Pollen"
assert printed[pokemon["Budew"]]["attacks"][0]["cost"] == []
assert trainer["Guzma"] == 2
assert trainer["Prime Catcher"] == 1
assert energy["Double Dragon Energy"] == 4
assert trainer["Crispin"] == trainer["Raihan"] == 1

published = json.loads((ROOT / "results" / "regidrago_budew_promotion_baselines" /
                        "aichi9_counts.json").read_text(encoding="utf-8"))
entry = next(x for x in published["decklists"] if x["place"] == 10)
assert entry["budew"] == 2
assert entry["guzma"] == trainer["Guzma"] == 2
assert entry["prime_catcher"] == 1
assert entry["kyurem_sv6pt5_47"] == 1
assert entry["double_dragon_energy"] == energy["Double Dragon Energy"] == 4

wobb = printed[pokemon["Wobbuffet"]]
assert wobb["types"] == ["Psychic"]
ability = next(a["text"] for a in wobb["abilities"]
               if a["name"] == "Bide Barricade")
assert "Active Pokémon" in ability
assert "except for Psychic Pokémon" in ability
assert "in each player's hand" in ability
assert "in each player's discard pile" in ability

def retained_ability(pokemon_id: str) -> bool:
    return "Psychic" in printed[pokemon_id]["types"]

assert retained_ability("swsh6-75")  # opposing Shadow Rider VMAX Underworld Door
assert retained_ability("sv8-76")  # own Latias Skyliner
assert retained_ability("sm2-60")  # opposing Tapu Lele-GX Wonder Tag
assert not retained_ability("swsh12-136")  # own Regidrago Legacy Star
assert not retained_ability("sm10-57")  # own Dedenne-GX Dedechange
assert not retained_ability("sv2-169")  # own Squawkabilly ex Squawk and Seize
assert "Your Basic Pokémon" in printed["sv8-76"]["abilities"][0]["text"]

print("PASS: 60 verified Expanded-legal English prints, 20/30/10.")
print("PASS: 10th-place published counts and Psychic type-selective Active Wobbuffet lock.")
