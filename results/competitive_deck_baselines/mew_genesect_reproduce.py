"""Exact-print 2026 Aichi fifth-place Mew Genesect tournament reference.

Yamato Nakano, CL Aichi Open League 2026, May 10, fifth overall.
Source counts: https://www.limitlesstcg.com/tournaments/566/decklists
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

POKEMON: dict[str, int] = {
    "Mew V": 4,
    "Mew VMAX": 3,
    "Genesect V": 4,
    "Dedenne-GX": 1,
    "Crobat V": 1,
    "Lillie's Clefairy ex": 1,
}
TRAINERS: dict[str, int] = {
    "Guzma": 2,
    "Karen": 2,
    "Wally": 1,
    "Marnie": 1,
    "Pokémon Ranger": 1,
    "Quick Ball": 4,
    "Ultra Ball": 4,
    "Trainers' Mail": 3,
    "Battle VIP Pass": 3,
    "Special Charge": 2,
    "VS Seeker": 2,
    "Special Red Card": 2,
    "Enhanced Hammer": 1,
    "Field Blower": 1,
    "Lost Vacuum": 1,
    "Escape Rope": 1,
    "Hisuian Heavy Ball": 1,
    "Secret Box": 1,
    "Muscle Band": 2,
    "Float Stone": 2,
    "Forest Seal Stone": 1,
    "Sky Field": 2,
    "Path to the Peak": 2,
}
ENERGY: dict[str, int] = {"Double Colorless Energy": 4}

PRINT_IDS: dict[str, str] = {
    "Mew V": "swsh8-113",
    "Mew VMAX": "swsh8-114",
    "Genesect V": "swsh8-185",
    "Dedenne-GX": "sm10-57",
    "Crobat V": "swsh3-104",
    "Lillie's Clefairy ex": "sv9-56",
    "Guzma": "sm3-115",
    "Karen": "xyp-XY177",
    "Wally": "xy6-94",
    "Marnie": "swsh1-169",
    "Pokémon Ranger": "xy11-104",
    "Quick Ball": "swsh1-179",
    "Ultra Ball": "swsh9-150",
    "Trainers' Mail": "xy6-92",
    "Battle VIP Pass": "swsh8-225",
    "Special Charge": "xy11-105",
    "VS Seeker": "xy6-110",
    "Special Red Card": "me4-82",
    "Enhanced Hammer": "sv6-148",
    "Field Blower": "sm2-125",
    "Lost Vacuum": "swsh11-162",
    "Escape Rope": "swsh5-125",
    "Hisuian Heavy Ball": "swsh10-146",
    "Secret Box": "sv6-163",
    "Muscle Band": "xy1-121",
    "Float Stone": "xy8-137",
    "Forest Seal Stone": "swsh12-156",
    "Sky Field": "xy6-89",
    "Path to the Peak": "swsh6-148",
    "Double Colorless Energy": "sm1-136",
}
ABILITIES = {
    "swsh8-185": "Fusion Strike System",
    "sm10-57": "Dedechange",
    "swsh3-104": "Dark Asset",
}
ATTACKS = {"swsh8-114": "Cross Fusion Strike"}


def verify() -> None:
    root = Path(__file__).resolve().parents[2]
    resources = root / "resources"
    counts = {**POKEMON, **TRAINERS, **ENERGY}

    assert sum(POKEMON.values()) == 14
    assert sum(TRAINERS.values()) == 42
    assert sum(ENERGY.values()) == 4
    assert sum(counts.values()) == 60
    assert len(counts) == len(PRINT_IDS)

    records = load_all_card_records(resources)
    category_counts: Counter[str] = Counter()
    basic_count = 0
    for name, copies in counts.items():
        record = records[PRINT_IDS[name]]
        assert record.name == name, (name, record.name)
        category_counts[record.supertype] += copies
        if record.is_basic_pokemon:
            basic_count += copies

    assert category_counts == {
        "Pokémon": 14, "Trainer": 42, "Energy": 4
    }
    assert basic_count == 11

    entries = [DeckEntry(PRINT_IDS[name], count) for name, count in counts.items()]
    proof = adjudicate_deck(entries, resources, as_of=date(2026, 10, 12))
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason)
        for p in proof.print_proofs if p.eligibility != "eligible"
    ]

    for card_id, target in ABILITIES.items():
        set_id = card_id.rsplit("-", 1)[0]
        cards = json.loads(
            (resources / "cards" / "en" / f"{set_id}.json").read_text(
                encoding="utf-8"
            )
        )
        raw = next(c for c in cards if c["id"] == card_id)
        assert any(a["name"] == target for a in raw["abilities"])
    for card_id, target in ATTACKS.items():
        set_id = card_id.rsplit("-", 1)[0]
        cards = json.loads(
            (resources / "cards" / "en" / f"{set_id}.json").read_text(
                encoding="utf-8"
            )
        )
        raw = next(c for c in cards if c["id"] == card_id)
        assert any(a["name"] == target for a in raw["attacks"])

    print("Aichi fifth-place Mew Genesect: 14 Pokémon / 42 Trainers / 4 Energy")
    print("11 opening Basics; one Secret Box ACE SPEC")
    print(f"Exact-print snapshot disposition: {proof.disposition}")


if __name__ == "__main__":
    verify()
