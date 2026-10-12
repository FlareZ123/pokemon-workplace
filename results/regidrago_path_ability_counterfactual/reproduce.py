"""Print-grounded one-slot Path to the Peak Regidrago counterfactual."""

from collections import Counter
from copy import deepcopy
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
source = json.loads((ROOT / "results" / "regidrago_aichi_top10_playable" /
                     "yoshioka_regidrago_2026.json").read_text(encoding="utf-8"))
candidate = json.loads((HERE / "regidrago_path_swap_60.json").read_text(encoding="utf-8"))
champion = json.loads((ROOT / "results" / "regidrago_shadow_rider_temporal_counterplay" /
                       "shadow_rider_aichi_2026.json").read_text(encoding="utf-8"))
printed = {
    card["id"]: card
    for path in sorted((ROOT / "resources" / "cards" / "en").glob("*.json"))
    for card in json.loads(path.read_text(encoding="utf-8"))
}

def named_counts(deck: dict) -> Counter[str]:
    return Counter({
        item["name"]: item["count"]
        for entries in deck["groups"].values()
        for item in entries
    })

before = named_counts(source)
after = named_counts(candidate)
assert sum(before.values()) == sum(after.values()) == 60
assert after["Parallel City"] == 0
assert before["Parallel City"] == 1
assert after["Path to the Peak"] == 1
assert before["Path to the Peak"] == 0
assert after == before - Counter({"Parallel City": 1}) + Counter({"Path to the Peak": 1})

assert {group: sum(item["count"] for item in entries)
        for group, entries in candidate["groups"].items()} == {
            "Pokémon": 20, "Trainer": 30, "Energy": 10
        }
for group, entries in candidate["groups"].items():
    for item in entries:
        card = printed[item["print_id"]]
        display_name = ("Battle Compressor Team Flare Gear"
                        if item["name"] == "Battle Compressor" else item["name"])
        assert card["name"] == display_name
        assert card["supertype"] == group
        assert card["legalities"]["expanded"] == "Legal", item["print_id"]
        if group != "Energy" or "Basic" not in card.get("subtypes", []):
            assert item["count"] <= 4
assert sum(item["count"] for item in candidate["groups"]["Trainer"]
           if "ACE SPEC" in printed[item["print_id"]].get("subtypes", [])) == 1

path = printed["swsh6-148"]
assert path["name"] == "Path to the Peak"
assert "Stadium" in path["subtypes"]
assert any("Pokémon with a Rule Box in play" in line and
           "have no Abilities" in line
           for line in path["rules"])
wobb = printed["xy4-36"]
assert "except for Psychic Pokémon" in wobb["abilities"][0]["text"]
assert "If this Pokémon is your Active Pokémon" in wobb["abilities"][0]["text"]
latias = printed["sv8-76"]
assert latias["types"] == ["Psychic"] and latias.get("rules")
assert "Your Basic Pokémon in play have no Retreat Cost." == latias["abilities"][0]["text"]
marshadow = printed["sm10-81"]
assert not marshadow.get("rules")
assert "discard any Stadium card in play" in marshadow["abilities"][0]["text"]


def suppression(deck: dict, wobbuffet_active: bool,
                path_active: bool) -> tuple[int, int, list[str]]:
    suppressed = 0
    exempt = 0
    suppressed_names = []
    for item in deck["groups"]["Pokémon"]:
        card = printed[item["print_id"]]
        if not card.get("abilities"):
            continue
        psychic_exception_fails = wobbuffet_active and "Psychic" not in card["types"]
        rulebox_lock = path_active and bool(card.get("rules"))
        denied = psychic_exception_fails or rulebox_lock
        if denied:
            suppressed += item["count"]
            suppressed_names.append(card["name"])
        else:
            exempt += item["count"]
    return suppressed, exempt, suppressed_names

assert suppression(candidate, False, False)[:2] == (0, 11)
assert suppression(champion, False, False)[:2] == (0, 11)

checks = {
    ("only_Wobbuffet", True, False): ((7, 4), (1, 10)),
    ("only_Path", False, True): ((8, 3), (10, 1)),
    ("both_locks", True, True): ((9, 2), (10, 1)),
    ("no_locks", False, False): ((0, 11), (0, 11)),
}
for (label, active, stadium), (own_expected, opp_expected) in checks.items():
    own = suppression(candidate, active, stadium)
    opponent = suppression(champion, active, stadium)
    assert own[:2] == own_expected, (label, own)
    assert opponent[:2] == opp_expected, (label, opponent)
    print(label, "own blocked/exempt:", own[:2],
          "opponent blocked/exempt:", opponent[:2])

# Psychic Wobbuffet is exempt from its own lock; Path disables the *Rule Box*
# Latias Skyliner route, so a two-cost Wobbuffet cannot use that Free Retreat
# while Path remains in play, despite still being Basic.
assert not printed["xy4-36"].get("rules")
assert len(printed["xy4-36"]["retreatCost"]) == 2
assert "Basic" in printed["xy4-36"]["subtypes"]
assert bool(printed["sv8-76"].get("rules"))
assert "Sky Field" in named_counts(champion)
assert "Dimension Valley" in named_counts(champion)
assert "Field Blower" in named_counts(champion)
assert "Marshadow" in named_counts(champion)["Marshadow"] and "Marshadow" in named_counts(candidate)

print("PASS: exactly one published-slot replacement, snapshot eligibility,")
print("      typed Rule Box and Psychic suppression, and removal counterplay sources.")
