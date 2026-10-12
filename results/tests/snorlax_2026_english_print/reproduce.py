"""Third-place 2026 Aichi Snorlax Stall, one-card international adaptation.

Source: https://limitlesstcg.com/tournaments/566/decklists
Original Japanese card Player's Ceremony has no English print. Substitute a
second Tropical Beach while preserving the other 59 source card copies.
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

BASE = ROOT / "results" / "decks" / "snorlax-stall-aichi-2026-english"
MANIFEST = BASE / "manifest.json"
ORIGINAL_NAMES = {
    "Snorlax": 3, "Galarian Stunfisk": 2, "Regirock": 1,
    "Mimikyu": 1, "Girafarig": 1, "Bunnelby": 1,
    "Articuno-GX": 1, "Rotom V": 1,
    "Plumeria": 4, "Arven": 4, "Team Flare Grunt": 2,
    "Teammates": 2, "Lusamine": 2,
    "Team Rocket's Handiwork": 1, "Gladion": 1, "Guzma": 1,
    "Faba": 1, "Penny": 1, "Eri": 1, "Lillie's Determination": 1,
    "Nest Ball": 3, "VS Seeker": 3, "Enhanced Hammer": 2,
    "Trainers' Mail": 2, "Counter Catcher": 2,
    "Scoop Up Cyclone": 1, "Quick Ball": 1,
    "Hisuian Heavy Ball": 1, "Night Stretcher": 1,
    "Float Stone": 1, "Stealthy Hood": 1, "Tool Jammer": 1,
    "Forest Seal Stone": 1,
    "Tropical Beach": 1, "Player's Ceremony": 1, "Temple of Sinnoh": 1,
    "Capture Energy": 3, "Water Energy": 2,
}
CORE = {
    "bw8-101": ("abilities", "Block"),
    "swsh1-132": ("abilities", "Snap Trap"),
    "sv2-97": ("abilities", "Safeguard"),
    "sm8-94": ("attacks", "Get Lost"),
    "xy5-121": ("attacks", "Rototiller"),
    "sm7-31": ("attacks", "Cold Crush-GX"),
    "swsh11-58": ("abilities", "Instant Charge"),
    "swsh12-156": ("abilities", "Star Alchemy"),
}


def verify() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    src = data["source"]
    assert (src["place"], src["player"], src["date"]) == (
        3, "Haruto Miki", "2026-05-10")
    assert src["url"] == "https://limitlesstcg.com/tournaments/566/decklists"
    rows = data["cards"]
    counts = Counter({r["name"]: r["quantity"] for r in rows})
    original = Counter(ORIGINAL_NAMES)
    assert sum(original.values()) == 60 and original["Player's Ceremony"] == 1
    expected = original.copy()
    expected["Player's Ceremony"] -= 1
    expected["Tropical Beach"] += 1
    del expected["Player's Ceremony"]
    assert counts == expected
    assert len(rows) == len(counts) == len(ORIGINAL_NAMES) - 1
    assert len({r["print_id"] for r in rows}) == len(rows)
    assert all(type(r["quantity"]) is int and r["quantity"] > 0 for r in rows)
    by_type = Counter()
    for r in rows:
        by_type[r["category"]] += r["quantity"]
    assert by_type == {"Pokémon": 11, "Trainer": 44, "Energy": 5}
    assert sum(by_type.values()) == 60

    resources = ROOT / "resources"
    records = load_all_card_records(resources)
    basics = 0
    for row in rows:
        record = records[row["print_id"]]
        assert (record.name, record.supertype) == (
            row["name"], row["category"]), (row["print_id"], record.name)
        assert record.effective_status == "Legal", row
        if record.is_basic_pokemon:
            basics += row["quantity"]
    assert basics == 11

    proof = adjudicate_deck(
        [DeckEntry(row["print_id"], row["quantity"]) for row in rows],
        resources, as_of=date(2026, 10, 12))
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason)
        for p in proof.print_proofs if p.eligibility != "eligible"]
    assert all(p.eligibility == "eligible" for p in proof.print_proofs)

    for card_id, (kind, effect) in CORE.items():
        source = json.loads((resources / "cards/en"
                             / (card_id.rsplit("-", 1)[0] + ".json"))
                            .read_text(encoding="utf-8"))
        row = next(c for c in source if c["id"] == card_id)
        assert any(e["name"] == effect for e in row[kind]), (card_id, effect)
    beach = json.loads((resources / "cards/en/bwp.json").read_text(encoding="utf-8"))
    beach_print = next(c for c in beach if c["id"] == "bwp-BW28")
    assert any("draw cards until" in rule.lower() for rule in beach_print["rules"])
    assert counts["Tropical Beach"] == 2
    assert counts["Scoop Up Cyclone"] == 1

    print("PASS: Source-derived CL Aichi 2026 third-place Snorlax Stall 60")
    print("PASS: Only 1 Player's Ceremony -> 2nd Tropical Beach substitution")
    print("PASS: 11 Pokémon / 44 Trainer / 5 Energy, 11 opening Basics")
    print("PASS: 8 core gameplay print effects and 2 print-matched Tropical Beaches")
    print("PASS: conservative English paper Expanded snapshot eligibility")
    print("LIMIT: 2026 Japanese tournament third place belongs to SOURCE deck;")
    print("       modified English variant has no tournament result or matchup win rate")


if __name__ == "__main__":
    verify()
