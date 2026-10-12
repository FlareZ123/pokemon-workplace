"""Verify Aichi English print deck and its exact Beach/DCE frontier."""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from math import isclose
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records
from tools.iron_thorns_beach_frontier import BeachCounts, beach_fallback, exact

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def verify() -> None:
    candidate = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
    original = json.loads(
        (HERE.parent / "iron_thorns_aichi_english" / "manifest.json")
        .read_text(encoding="utf-8")
    )
    assert candidate["source"] == original["source"]
    rows = candidate["cards"]
    counts = Counter({row["name"]: row["quantity"] for row in rows})
    base = Counter({row["name"]: row["quantity"] for row in original["cards"]})
    assert len(rows) == len(base) == 32
    assert counts - base == {"Tropical Beach": 1}
    assert base - counts == {"Double Colorless Energy": 1}
    assert sum(counts.values()) == 60
    assert counts["Iron Thorns ex"] == 4
    assert counts["Tropical Beach"] == 2
    assert counts["Double Colorless Energy"] == 1
    assert counts["Megaton Blower"] == 1

    records = load_all_card_records(ROOT / "resources")
    by_type = Counter()
    starters = 0
    for row in rows:
        card = records[row["print_id"]]
        assert card.name == row["name"], (row["print_id"], card.name)
        assert card.supertype == row["category"]
        by_type[row["category"]] += row["quantity"]
        if card.is_basic_pokemon:
            starters += row["quantity"]
    assert by_type == {"Pokémon": 4, "Trainer": 48, "Energy": 8}, by_type
    assert starters == 4

    proof = adjudicate_deck(
        tuple(DeckEntry(row["print_id"], row["quantity"]) for row in rows),
        ROOT / "resources",
        as_of=date(2026, 10, 12),
    )
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason)
        for p in proof.print_proofs if p.eligibility != "eligible"
    ]

    speed = exact(BeachCounts(dce=2, beach=1, safe=12))
    recovery = exact(BeachCounts(dce=1, beach=2, safe=12))
    assert isclose(float(speed["strict_attack"]), 0.20953810533875675, abs_tol=1e-12)
    assert isclose(float(recovery["strict_attack"]), 0.16293835803004747, abs_tol=1e-12)
    assert isclose(float(beach_fallback(speed, "strict")), 0.2704635061627364, abs_tol=1e-12)
    assert isclose(float(beach_fallback(recovery, "strict")), 0.3965775391048470, abs_tol=1e-12)
    assert recovery["strict_attack"] < speed["strict_attack"]
    assert beach_fallback(recovery, "strict") > beach_fallback(speed, "strict")

    print("PASS: 60 cards / 4 Pokémon / 48 Trainers / 8 Energy, 4 Basic starters")
    print("PASS: English Expanded snapshot:", proof.disposition)
    print("PASS: exactly one DCE -> Tropical Beach matched-size substitution")
    print("Speed 2-DCE strict opening access:", f"{float(speed['strict_attack']):.9%}")
    print("Beach 2-copy strict opening access:", f"{float(recovery['strict_attack']):.9%}")
    print("Speed fallback:", f"{float(beach_fallback(speed, 'strict')):.9%}")
    print("Beach fallback:", f"{float(beach_fallback(recovery, 'strict')):.9%}")
    print("LIMIT: first-turn access and Beach opportunity, no actual win rate")


if __name__ == "__main__":
    verify()
