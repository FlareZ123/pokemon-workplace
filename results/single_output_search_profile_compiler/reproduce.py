from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from single_output_search_profile_compiler import (
    compile_single_output_revealed_search_profiles,
)


profiles = compile_single_output_revealed_search_profiles(ROOT / "resources")
counts = Counter(profile.name for profile in profiles)

assert len(profiles) == 28
assert set(counts) == {
    "Energy Search",
    "Evolution Incense",
    "Master Ball",
    "Poké Kid",
    "Quick Ball",
    "Skyla",
    "Team Rocket's Petrel",
    "Ultra Ball",
}
assert counts == Counter({
    "Ultra Ball": 13,
    "Energy Search": 4,
    "Quick Ball": 3,
    "Team Rocket's Petrel": 3,
    "Poké Kid": 2,
    "Evolution Incense": 1,
    "Master Ball": 1,
    "Skyla": 1,
})

quick_ball = tuple(
    profile
    for profile in profiles
    if profile.name == "Quick Ball"
)
assert {profile.card_id for profile in quick_ball} == {
    "swsh1-179",
    "swsh1-216",
    "swsh8-237",
}
for profile in quick_ball:
    assert profile.action_class == "Item"
    assert len(profile.base_outputs) == 1
    assert profile.base_outputs[0].label == "Basic Pokémon"
    assert profile.base_outputs[0].max_units == 1
    assert profile.required_discard_other_cards == 1
    assert profile.play_condition is not None
    assert "discard another card" in profile.play_condition

ultra_ball = tuple(
    profile
    for profile in profiles
    if profile.name == "Ultra Ball"
)
assert len(ultra_ball) == 13
for profile in ultra_ball:
    assert profile.action_class == "Item"
    assert profile.base_outputs[0].label == "Pokémon"
    assert profile.required_discard_other_cards == 2

energy_search = tuple(
    profile
    for profile in profiles
    if profile.name == "Energy Search"
)
assert len(energy_search) == 4
for profile in energy_search:
    assert profile.action_class == "Item"
    assert profile.required_discard_other_cards == 0
    assert profile.base_outputs[0].label.casefold() == "basic energy card"

petrel = tuple(
    profile
    for profile in profiles
    if profile.name == "Team Rocket's Petrel"
)
assert len(petrel) == 3
for profile in petrel:
    assert profile.action_class == "Supporter"
    assert profile.base_outputs[0].label == "Trainer card"

excluded_names = {
    "Arven",
    "Boxed Order",
    "Earthen Vessel",
    "Fighting Gong",
    "Poké Ball",
}
assert not excluded_names & set(counts)

print("single-output revealed-search compiler regressions passed")
print("28 legal print profiles across 8 unique names")
print("Quick Ball: 3 prints, Basic Pokemon, exact one-card discard cost")
print("Ultra Ball: 13 prints, Pokemon, exact two-card discard cost")
print("coin, disjunctive, multi-output, and multi-unit families remain excluded")
