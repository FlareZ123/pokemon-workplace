"""Validate the complete 2026 Aichi 10th-place Regidrago list by exact print.

Independent published source: https://limitlesstcg.com/decks/list/26816
The player may have used region-specific or alternate artwork printings.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
import json
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
MANIFEST = BASE / "regidrago_haruku_2026.json"

# Critical attack payloads and bench-support identities must match exact prints.
CORE = {
    "swsh12-136": ("attacks", "Apex Dragon"),
    "sv8pt5-4": ("attacks", "Itchy Pollen"),
    "sv6-130": ("attacks", "Phantom Dive"),
    "sm5-100": ("attacks", "Timeless-GX"),
    "sv5-120": ("attacks", "Retribution Strike"),
    "sv6pt5-47": ("attacks", "Trifrost"),
    "swsh11-136": ("attacks", "Rolling Iron"),
    "sm10-57": ("abilities", "Dedechange"),
    "sv2-169": ("abilities", "Squawk and Seize"),
    "sm2-60": ("abilities", "Wonder Tag"),
    "sv8-76": ("abilities", "Skyliner"),
    "sm10-81": ("abilities", "Resetting Hole"),
    "xy4-36": ("abilities", "Bide Barricade"),
}

REFERENCE_SPOT_CHECK = {
    "Regidrago V": 4,
    "Regidrago VSTAR": 3,
    "Budew": 2,
    "Koraidon ex": 1,
    "Kyurem": 1,
    "Dialga-GX": 1,
    "Guzma": 2,
    "Quick Ball": 3,
    "Mysterious Treasure": 3,
    "Battle VIP Pass": 3,
    "VS Seeker": 3,
    "Prime Catcher": 1,
    "Grass Energy": 4,
    "Fire Energy": 2,
    "Double Dragon Energy": 4,
}


def verify() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = manifest["source"]
    assert source["event"] == "CL Aichi Open League"
    assert source["date"] == "2026-05-10"
    assert source["place"] == 10
    assert source["player"] == "Haruku Yoshioka"
    assert source["url"] == "https://limitlesstcg.com/decks/list/26816"

    rows = manifest["cards"]
    assert len(rows) == 36
    assert len({r["name"] for r in rows}) == len(rows)
    assert len({r["print_id"] for r in rows}) == len(rows)
    assert all(isinstance(r["quantity"], int) and r["quantity"] > 0 for r in rows)

    by_type: Counter[str] = Counter()
    names: Counter[str] = Counter()
    for r in rows:
        by_type[r["category"]] += r["quantity"]
        names[r["name"]] += r["quantity"]
    assert by_type == {"Pokémon": 20, "Trainer": 30, "Energy": 10}
    assert sum(by_type.values()) == 60
    for name, expected in REFERENCE_SPOT_CHECK.items():
        assert names[name] == expected, (name, names[name], expected)

    # Cross-check exact published counts already independently transcribed in
    # the project's nine-Aichi-Regidrago reference study.
    comparison = json.loads((
        ROOT / "results" / "regidrago_budew_promotion_baselines"
        / "aichi9_counts.json"
    ).read_text(encoding="utf-8"))
    matches = [r for r in comparison["decklists"] if r["place"] == 10]
    assert len(matches) == 1
    published = matches[0]
    assert published["url"] == source["url"]
    for field, name in {
        "budew": "Budew",
        "quick_ball": "Quick Ball",
        "guzma": "Guzma",
        "prime_catcher": "Prime Catcher",
        "latias_ex": "Latias ex",
        "hisuian_heavy_ball": "Hisuian Heavy Ball",
        "kyurem_sv6pt5_47": "Kyurem",
        "crispin": "Crispin",
        "raihan": "Raihan",
        "basic_grass": "Grass Energy",
        "basic_fire": "Fire Energy",
        "double_dragon_energy": "Double Dragon Energy",
    }.items():
        assert names[name] == published[field], (field, names[name], published[field])

    resources = ROOT / "resources"
    records = load_all_card_records(resources)
    basics = 0
    for r in rows:
        record = records[r["print_id"]]
        assert record.name == r["name"], (r["print_id"], record.name, r["name"])
        assert record.supertype == r["category"], (r["name"], record.supertype)
        if record.is_basic_pokemon:
            basics += r["quantity"]
    assert basics == 15

    ace_spec = [r for r in rows if r["name"] == "Prime Catcher"]
    assert len(ace_spec) == 1 and ace_spec[0]["quantity"] == 1

    proof = adjudicate_deck(
        tuple(DeckEntry(r["print_id"], r["quantity"]) for r in rows),
        resources,
        as_of=date(2026, 10, 12),
    )
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason) for p in proof.print_proofs
        if p.eligibility != "eligible"
    ]
    assert len(proof.print_proofs) == len(rows)
    assert all(p.eligibility == "eligible" for p in proof.print_proofs)

    for print_id, (field, effect_name) in CORE.items():
        set_id = print_id.rsplit("-", 1)[0]
        raw_cards = json.loads(
            (resources / "cards" / "en" / f"{set_id}.json").read_text(
                encoding="utf-8"
            )
        )
        card = next(c for c in raw_cards if c["id"] == print_id)
        assert any(e.get("name") == effect_name for e in card[field]), (
            print_id, effect_name
        )

    print("PASS: Regidrago 10th CL Aichi 2026, 60 cards (20/30/10)")
    print("PASS: 36 source card names and exact selected print IDs")
    print("PASS: 15 Basic Pokémon, exactly one ACE SPEC")
    print("PASS: 12 independent nine-list source count crosschecks")
    print("PASS: 13 core attack/Ability print-specific witnesses")
    print("PASS: conservative October 12 Expanded snapshot eligibility")
    print("LIMIT: no head-to-head match win rate or regional paper legality proof")


if __name__ == "__main__":
    verify()
