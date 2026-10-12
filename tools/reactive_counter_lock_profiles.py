"""Printed-source-grounded static Ability/Tool lock scopes for a Scrafty stack.

Caller attests that each lock is active at the post-damage reaction window.
This does not compile timing or source establishment.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from reactive_counter_stack_frontier import Stack, source_validate
from build_expanded_legality_baseline import classify_effective_legality

LOCK_PRINTS = {
    "garbotoxin": ("bw11-68", "Garbodor", "Garbotoxin",
                  "each Pokémon in play, in each player's hand, and in each player's discard pile has no Abilities (except for Garbotoxin)"),
    "wobbuffet": ("xy4-36", "Wobbuffet", "Bide Barricade",
                  "has no Abilities (except for Psychic Pokémon)"),
    "rulebox": ("swsh6-148", "Path to the Peak", "",
                "Pokémon with a Rule Box in play (both yours and your opponent's) have no Abilities."),
    "tools": ("sv6-153", "Jamming Tower", "",
              "Pokémon Tools attached to each Pokémon (both yours and your opponent's) have no effect."),
}

@dataclass(frozen=True)
class LockProfile:
    garbotoxin: bool = False
    wobbuffet: bool = False
    path_to_peak: bool = False
    jamming_tower: bool = False

    def counters(self, stack: Stack) -> int:
        active_enabled = not (self.garbotoxin or self.wobbuffet or self.path_to_peak)
        aura_enabled = not (self.garbotoxin or self.wobbuffet)
        tool = {"none": 0, "punk": 4, "deluxe": 12}[stack.tool]
        return (5 * int(active_enabled) + stack.spiritomb * int(aura_enabled)
                + 2 * stack.spiky + (0 if self.jamming_tower else tool))

def verify_prints(resources: Path) -> None:
    source_validate(resources)
    sets = {x["id"]: x for x in json.loads((resources / "sets" / "en.json").read_text(encoding="utf-8"))}
    for role, (print_id, name, ability, phrase) in LOCK_PRINTS.items():
        set_id = print_id.split("-", 1)[0]
        assert sets[set_id]["legalities"].get("expanded") == "Legal", role
        assert sets[set_id]["releaseDate"] <= "2026/10/12", role
        cards = json.loads((resources / "cards" / "en" / (set_id + ".json")).read_text(encoding="utf-8"))
        card = next(c for c in cards if c["id"] == print_id)
        assert card["name"] == name and classify_effective_legality(card)[0] == "Legal", role
        texts = ([a["text"] for a in card.get("abilities") or () if a["name"] == ability]
                 if ability else card.get("rules") or ())
        assert any(phrase in t for t in texts), role
        if role == "garbotoxin":
            assert any("Pokémon Tool card attached to it" in t for t in texts)
        if role == "wobbuffet":
            assert any("your Active Pokémon" in t for t in texts)

def verify_reference_ace_spec(resources: Path, manifest: dict) -> None:
    cards = manifest["cards"]
    assert sum(c["quantity"] for c in cards) == 60
    assert any(c["print_id"] == "bw11-68" and c["quantity"] == 2 for c in cards)
    assert sum(c["quantity"] for c in cards if c["name"] == "Float Stone") == 4
    assert all(c["name"] != "Deluxe Bomb" for c in cards)
    sets = {s["id"]: s for s in json.loads((resources / "sets" / "en.json").read_text(encoding="utf-8"))}
    aces = []
    for line in cards:
        print_id = line["print_id"]
        set_id = print_id.split("-", 1)[0]
        assert sets[set_id]["legalities"].get("expanded") == "Legal"
        source = json.loads((resources / "cards" / "en" / (set_id + ".json")).read_text(encoding="utf-8"))
        card = next(c for c in source if c["id"] == print_id)
        assert card["name"] == line["name"], print_id
        if "ACE SPEC" in card.get("subtypes", []):
            aces.append((print_id, line["quantity"]))
    assert aces == [("sv6-163", 1)], aces

def study() -> dict:
    full, lean = Stack(4, 4, "deluxe"), Stack(0, 0, "deluxe")
    cases = {
        "unlocked": LockProfile(),
        "path_to_peak": LockProfile(path_to_peak=True),
        "wobbuffet": LockProfile(wobbuffet=True),
        "own_garbotoxin": LockProfile(garbotoxin=True),
        "jamming_tower": LockProfile(jamming_tower=True),
        "path_and_jamming": LockProfile(path_to_peak=True, jamming_tower=True),
        "garbotoxin_and_jamming": LockProfile(garbotoxin=True, jamming_tower=True),
        "garbotoxin_and_path": LockProfile(garbotoxin=True, path_to_peak=True),
    }
    return {
        "sources": {k: v[0] for k, v in LOCK_PRINTS.items()},
        "counter_table": {name: {"full": mode.counters(full), "mega_deluxe_only": mode.counters(lean)}
                          for name, mode in cases.items()},
        "min_spiky_for_170_with_four_spiritomb": {
            name: next((n for n in range(5) if mode.counters(Stack(4, n, "deluxe")) >= 17), None)
            for name, mode in cases.items()},
    }
