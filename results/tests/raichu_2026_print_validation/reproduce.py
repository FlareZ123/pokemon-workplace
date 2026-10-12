"""Verify Shu Hosoda's fourth-place 2026 Aichi Raichu/Electrode 60.

Source: https://www.limitlesstcg.com/decks/list/26812
Selected English prints are representative of the published card-name counts.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

MANIFEST = ROOT / "results" / "decks" / "raichu-electrode-aichi-2026" / "manifest.json"
PUBLISHED = {
    "Voltorb": 2, "Electrode-GX": 3, "Pikachu": 1, "Alolan Raichu": 2,
    "Dedenne-GX": 2, "Crobat V": 2, "Squawkabilly ex": 1,
    "Tapu Lele-GX": 1, "Eldegoss V": 1, "Gengar & Mimikyu-GX": 1,
    "Klefki": 1, "Ditto ◇": 1, "Gladion": 1, "Carmine": 1,
    "Pokémon Ranger": 1, "Lillie's Determination": 1,
    "Quick Ball": 4, "Battle Compressor": 4, "Rescue Stretcher": 4,
    "Escape Rope": 3, "Hisuian Heavy Ball": 2, "Ultra Ball": 1,
    "Battle VIP Pass": 1, "Secret Box": 1, "Telescopic Sight": 1,
    "U-Turn Board": 1, "Forest Seal Stone": 1, "Sky Field": 3,
    "Reversal Energy": 4, "Counter Energy": 4, "Unit Energy LPM": 4,
}
CORE_EFFECTS = {
    "sm7-48": ("abilities", "Extra Energy Bomb"),
    "sm11-57": ("attacks", "Electro Rain"),
    "sm8-154": ("abilities", "Almighty Evolution"),
    "sv1-96": ("abilities", "Mischievous Lock"),
    "sm10-57": ("abilities", "Dedechange"),
    "swsh3-104": ("abilities", "Dark Asset"),
    "sv2-169": ("abilities", "Squawk and Seize"),
    "sm2-60": ("abilities", "Wonder Tag"),
    "swsh2-19": ("abilities", "Happy Match"),
    "swsh12-156": ("abilities", "Star Alchemy"),
}


def verify() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["source"] == {
        "event": "CL Aichi Open League",
        "date": "2026-05-10",
        "place": 4,
        "player": "Shu Hosoda",
        "url": "https://www.limitlesstcg.com/decks/list/26812",
    }
    rows = data["cards"]
    assert len(rows) == len(PUBLISHED) == 31
    names = {r.get("published_name", r["name"]): r["quantity"] for r in rows}
    assert names == PUBLISHED, (names.keys() ^ PUBLISHED.keys(),
                               [(k, names.get(k), v) for k, v in PUBLISHED.items()
                                if names.get(k) != v])
    assert len({r["name"] for r in rows}) == len(rows)
    assert len({r["print_id"] for r in rows}) == len(rows)
    assert all(type(r["quantity"]) is int and r["quantity"] > 0 for r in rows)
    type_counts = Counter()
    for r in rows:
        type_counts[r["category"]] += r["quantity"]
    assert type_counts == {"Pokémon": 18, "Trainer": 30, "Energy": 12}
    assert sum(type_counts.values()) == 60

    resources = ROOT / "resources"
    card_records = load_all_card_records(resources)
    basics = 0
    for r in rows:
        c = card_records[r["print_id"]]
        assert (c.name, c.supertype) == (r["name"], r["category"]), (
            r["print_id"], c.name, c.supertype)
        if c.is_basic_pokemon:
            basics += r["quantity"]
    assert basics == 13

    proof = adjudicate_deck(
        [DeckEntry(r["print_id"], r["quantity"]) for r in rows],
        resources, as_of=date(2026, 10, 12))
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason)
        for p in proof.print_proofs if p.eligibility != "eligible"]
    assert len(proof.print_proofs) == len(rows)
    assert all(p.eligibility == "eligible" for p in proof.print_proofs)

    for card_id, (field, effect) in CORE_EFFECTS.items():
        set_id = card_id.rsplit("-", 1)[0]
        source = json.loads((resources / "cards" / "en" / (set_id + ".json"))
                            .read_text(encoding="utf-8"))
        card = next(c for c in source if c["id"] == card_id)
        assert any(e["name"] == effect for e in card[field]), (card_id, effect)
    assert card_records["sm5-138"].name == "Unit Energy LightningPsychicMetal"
    assert names["Secret Box"] == 1 and names["Ditto ◇"] == 1
    print("PASS: CL Aichi 2026 fourth-place published 60 (18/30/12)")
    print("PASS: 31 source-name quantities, 13 setup-eligible Basics")
    print("PASS: exact English print-name/role and 10 critical effect witnesses")
    print("PASS: single ACE SPEC, single Prism Star, Expanded eligibility snapshot")
    print("LIMIT: exact Japanese print choices, venue-specific legality and match win rate not established")


if __name__ == "__main__":
    verify()
