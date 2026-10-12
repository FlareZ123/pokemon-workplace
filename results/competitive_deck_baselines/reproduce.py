"""Check a fully specified paper Expanded reference list against bundled evidence."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

from tools.aichi_vileplume_als import DECK_COUNTS
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

# Published Aichi runner-up count transcription is imported from the source
# research model. These are chosen exact English prints for a playable reference.
PRINT_IDS: dict[str, str] = {
    "Pidgey": "sm9-121", "Pidgeotto": "sm9-123", "Pidgeot ex": "sv3-164",
    "Oddish": "xy7-1", "Gloom": "xy7-2", "Vileplume": "xy7-3",
    "Vileplume-GX": "sm12-4", "Lillipup": "bw7-120",
    "Herdier": "bw7-121", "Stoutland": "bw7-122",
    "Bunnelby": "xy5-121", "Fan Rotom": "sv7-118",
    "Relicanth": "sv5-84", "Mr. Mime": "bw9-47",
    "Girafarig": "sm8-94", "Budew": "sv8pt5-4", "Jirachi": "sm9-99",
    "Guzma & Hala": "sm12-193", "Guzma": "sm3-115",
    "Cassius": "xy1-115", "Karen": "xyp-XY177",
    "Plumeria": "sm3-120", "Gladion": "sm4-95",
    "Faba": "sm8-173", "Lusamine": "sm4-96",
    "Bellelba & Brycen-Man": "sm12-186", "Peonia": "swsh6-149",
    "Team Yell's Cheer": "swsh9-149", "Tag Call": "sm12-206",
    "Stealthy Hood": "sm10-186",
    "Technical Machine: Evolution": "sv4-178",
    "Counter Gain": "sm8-170", "Artazon": "sv2-171",
    "Grand Tree": "sv7-136", "Capture Energy": "swsh2-171",
    "Jet Energy": "sv2-190", "Memory Energy": "sm8-194",
    "Grass Energy": "bw1-105",
}


def verify() -> None:
    root = Path(__file__).resolve().parents[2]
    resources = root / "resources"
    assert sum(DECK_COUNTS.values()) == 60
    assert set(DECK_COUNTS) == set(PRINT_IDS)
    records = load_all_card_records(resources)
    by_type: Counter[str] = Counter()
    basic_count = 0
    for name, count in DECK_COUNTS.items():
        card = records[PRINT_IDS[name]]
        assert card.name == name, (name, card.name)
        by_type[card.supertype] += count
        if card.is_basic_pokemon:
            basic_count += count

    assert by_type == {"Pokémon": 26, "Trainer": 28, "Energy": 6}, by_type
    assert basic_count == 14
    assert DECK_COUNTS["Grand Tree"] == 1
    assert records[PRINT_IDS["Grand Tree"]].rules

    entries = [DeckEntry(PRINT_IDS[name], count) for name, count in DECK_COUNTS.items()]
    proof = adjudicate_deck(entries, resources, as_of=date(2026, 10, 12))
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason) for p in proof.print_proofs
        if p.eligibility != "eligible"
    ]
    assert all(p.eligibility == "eligible" for p in proof.print_proofs)

    important = {
        "xy5-121": ("ancientTrait", "Ω Barrage"),
        "sm9-123": ("abilities", "Air Mail"),
        "xy7-3": ("abilities", "Irritating Pollen"),
        "bw7-122": ("abilities", "Sentinel"),
        "sv7-118": ("abilities", "Fan Call"),
        "sm9-99": ("abilities", "Stellar Wish"),
    }
    for card_id, (field, expected) in important.items():
        set_id = card_id.rsplit("-", 1)[0]
        raw = json.loads((resources / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8"))
        print_data = next(card for card in raw if card["id"] == card_id)
        value = print_data[field]
        if isinstance(value, list):
            assert any(v["name"] == expected for v in value), (card_id, expected)
        else:
            assert value["name"] == expected, (card_id, expected)

    print("Aichi Vileplume reference: 60 cards / 26 Pokémon / 28 Trainers / 6 Energy")
    print("Basic Pokémon: 14; ACE SPEC: Grand Tree ×1")
    print("All 38 selected prints pass bundled current Expanded deck legality proof")
    print(f"Disposition: {proof.disposition}; regional scope: {proof.regional_legality_scope}")


if __name__ == "__main__":
    verify()
