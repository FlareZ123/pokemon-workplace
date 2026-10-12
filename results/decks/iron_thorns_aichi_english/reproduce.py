"""Legality and exact named-resource sensitivity for English Iron Thorns."""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from math import isclose
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records
from tools.iron_thorns_gnh_side_payload import Counts, exact

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = Path(__file__).with_name("manifest.json")


def verify() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = manifest["cards"]
    assert manifest["source"]["place"] == 6
    assert manifest["source"]["date"] == "2026-05-10"
    assert len(rows) == 32
    assert len({r["name"] for r in rows}) == len(rows)
    counts = Counter({r["name"]: r["quantity"] for r in rows})
    by_type = Counter()
    cards = load_all_card_records(ROOT / "resources")
    basics = 0
    for row in rows:
        qty = row["quantity"]
        assert isinstance(qty, int) and not isinstance(qty, bool) and 1 <= qty <= 4
        card = cards[row["print_id"]]
        assert card.name == row["name"], (row["name"], card.name)
        assert card.supertype == row["category"]
        by_type[row["category"]] += qty
        basics += qty if card.is_basic_pokemon else 0

    assert by_type == {"Pokémon": 4, "Trainer": 47, "Energy": 9}, by_type
    assert sum(by_type.values()) == 60 and basics == 4
    assert counts["Iron Thorns ex"] == 4
    assert counts["Megaton Blower"] == 1
    assert counts["Trainers' Mail"] == 4
    assert counts["Handheld Fan"] == 2
    assert counts["Double Colorless Energy"] == 2
    assert counts["Guzma & Hala"] == 2 and counts["Tag Call"] == 2
    assert counts["Thunder Mountain ◇"] == 1
    assert len(manifest["substitutions"]) == 3

    proof = adjudicate_deck(
        tuple(DeckEntry(r["print_id"], r["quantity"]) for r in rows),
        ROOT / "resources",
        as_of=date(2026, 10, 12),
    )
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason)
        for p in proof.print_proofs if p.eligibility != "eligible"
    ]
    assert all(p.eligibility == "eligible" for p in proof.print_proofs)

    baseline = exact(Counts(dce=1))
    candidate = exact(Counts(dce=2))
    def reach(x: object) -> float:
        return float(x.direct + x.mediated_discard + x.mediated_no_discard)
    original, adapted = reach(baseline), reach(candidate)
    assert isclose(original, 0.33781505711, abs_tol=1e-10)
    assert isclose(adapted, 0.38080679951, abs_tol=1e-10)
    assert adapted > original
    print("PASS: 60 cards / 4 Pokémon / 47 Trainers / 9 Energy, 4 Basic starters")
    print("PASS: conservative English Expanded snapshot:", proof.disposition)
    print(f"Named resource access, 1/2 DCE: {original:.9%} / {adapted:.9%}")
    print(f"Increase: {(adapted-original)*100:.9f} percentage points")
    print("LIMIT: modeled resource access; no attack or game win-rate measurements")


if __name__ == "__main__":
    verify()
