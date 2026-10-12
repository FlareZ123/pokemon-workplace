"""Check the full 2026 Aichi champion Shadow Rider list with exact English prints.

Card-name counts: https://www.limitlesstcg.com/tournaments/566/decklists
Winner: Yasunori Kato, May 10, 2026. English Battle Compressor has the
complete printed name 'Battle Compressor Team Flare Gear'.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

POKEMON: dict[str, int] = {
    "Shadow Rider Calyrex V": 3,
    "Shadow Rider Calyrex VMAX": 4,
    "Lillie's Clefairy ex": 2,
    "Tapu Lele-GX": 2,
    "Trevenant & Dusknoir-GX": 1,
    "Latias ex": 1,
    "Dialga-GX": 1,
    "Mimikyu": 1,
    "Girafarig": 1,
    "Marshadow": 1,
    "Radiant Eternatus": 1,
}
TRAINERS: dict[str, int] = {
    "Lillie's Determination": 2,
    "Carmine": 1,
    "Iono": 1,
    "Teammates": 1,
    "Raihan": 1,
    "Acerola": 1,
    "Guzma": 1,
    "Tulip": 1,
    "Mysterious Treasure": 4,
    "Fog Crystal": 4,
    "VS Seeker": 3,
    "Quick Ball": 1,
    "Hisuian Heavy Ball": 1,
    "Battle Compressor Team Flare Gear": 1,
    "Field Blower": 1,
    "Night Stretcher": 1,
    "Unfair Stamp": 1,
    "Float Stone": 1,
    "Forest Seal Stone": 1,
    "Sky Field": 2,
    "Dimension Valley": 1,
}
ENERGY: dict[str, int] = {"Psychic Energy": 11}

PRINT_IDS: dict[str, str] = {
    "Shadow Rider Calyrex V": "swsh6-74",
    "Shadow Rider Calyrex VMAX": "swsh6-75",
    "Lillie's Clefairy ex": "sv9-56",
    "Tapu Lele-GX": "sm2-60",
    "Trevenant & Dusknoir-GX": "smp-SM217",
    "Latias ex": "sv8-76",
    "Dialga-GX": "sm5-100",
    "Mimikyu": "sm2-58",
    "Girafarig": "sm8-94",
    "Marshadow": "sm10-81",
    "Radiant Eternatus": "swsh12pt5-105",
    "Lillie's Determination": "me1-119",
    "Carmine": "sv6-145",
    "Iono": "sv2-185",
    "Teammates": "xy5-141",
    "Raihan": "swsh7-152",
    "Acerola": "sm3-112",
    "Guzma": "sm3-115",
    "Tulip": "sv4-181",
    "Mysterious Treasure": "sm6-113",
    "Fog Crystal": "swsh6-140",
    "VS Seeker": "xy6-110",
    "Quick Ball": "swsh1-179",
    "Hisuian Heavy Ball": "swsh10-146",
    "Battle Compressor Team Flare Gear": "xy4-92",
    "Field Blower": "sm2-125",
    "Night Stretcher": "sv6pt5-61",
    "Unfair Stamp": "sv6-165",
    "Float Stone": "xy8-137",
    "Forest Seal Stone": "swsh12-156",
    "Sky Field": "xy6-89",
    "Dimension Valley": "xy4-93",
    "Psychic Energy": "bw1-109",
}

CORE_MECHANICS = {
    "swsh6-75": ("abilities", "Underworld Door"),
    "sm2-60": ("abilities", "Wonder Tag"),
    "sm2-58": ("attacks", "Copycat"),
    "sm5-100": ("attacks", "Timeless-GX"),
    "swsh12pt5-105": ("abilities", "Climactic Gate"),
}


def verify() -> None:
    root = Path(__file__).resolve().parents[2]
    resources = root / "resources"
    counts = {**POKEMON, **TRAINERS, **ENERGY}
    assert set(counts) == set(PRINT_IDS)
    assert len(counts) == 33
    assert sum(POKEMON.values()) == 18
    assert sum(TRAINERS.values()) == 31
    assert sum(ENERGY.values()) == 11
    assert sum(counts.values()) == 60

    records = load_all_card_records(resources)
    by_type: Counter[str] = Counter()
    basic_count = 0
    for name, quantity in counts.items():
        record = records[PRINT_IDS[name]]
        assert record.name == name, (name, record.name)
        by_type[record.supertype] += quantity
        if record.is_basic_pokemon:
            basic_count += quantity
    assert by_type == {"Pokémon": 18, "Trainer": 31, "Energy": 11}
    assert basic_count == 14

    entries = [DeckEntry(PRINT_IDS[name], quantity) for name, quantity in counts.items()]
    proof = adjudicate_deck(entries, resources, as_of=date(2026, 10, 12))
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason) for p in proof.print_proofs
        if p.eligibility != "eligible"
    ]
    assert all(p.eligibility == "eligible" for p in proof.print_proofs)

    for card_id, (field, expected_name) in CORE_MECHANICS.items():
        set_id = card_id.rsplit("-", 1)[0]
        raw = json.loads(
            (resources / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8")
        )
        card = next(c for c in raw if c["id"] == card_id)
        assert any(v["name"] == expected_name for v in card[field]), (
            card_id,
            expected_name,
        )

    print("Aichi winning Shadow Rider: 60 cards / 18 Pokémon / 31 Trainers / 11 Energy")
    print("Basic Pokémon: 14; ACE SPEC: Unfair Stamp ×1; Radiant: Eternatus ×1")
    print(f"33 exact prints eligible in bundled Expanded: {proof.disposition}")


if __name__ == "__main__":
    verify()
