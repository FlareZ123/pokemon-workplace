"""SFT: 60-card Regidrago Dragapult/VIP counterfactual legality and exact delta."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def verify() -> None:
    source = json.loads((ROOT / "results" / "competitive_deck_baselines"
                         / "regidrago_haruku_2026.json").read_text(encoding="utf-8"))
    variant = json.loads((HERE / "candidate.json").read_text(encoding="utf-8"))
    original = {r["print_id"]: r["quantity"] for r in source["cards"]}
    changed = {r["print_id"]: r["quantity"] for r in variant["cards"]}
    assert set(original) == set(changed)
    differences = {key: changed[key]-original[key] for key in original
                   if changed[key] != original[key]}
    assert differences == {"sv6-130": 1, "swsh8-225": -1}, differences
    assert all(q > 0 for q in changed.values())
    assert sum(changed.values()) == 60
    counts = Counter()
    for row in variant["cards"]:
        counts[row["category"]] += row["quantity"]
    assert counts == {"Pokémon": 21, "Trainer": 29, "Energy": 10}

    proof = adjudicate_deck(
        tuple(DeckEntry(r["print_id"], r["quantity"]) for r in variant["cards"]),
        ROOT / "resources",
        as_of=date(2026, 10, 12),
    )
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot", [
        (p.card_id, p.eligibility, p.reason) for p in proof.print_proofs
        if p.eligibility != "eligible"
    ]
    print("PASS: exactly +1 Dragapult ex / -1 Battle VIP Pass from source")
    print("PASS: 60 cards, 21/29/10, one unchanged ACE SPEC")
    print("PASS: conservative 2026-10-12 Expanded English eligibility")


if __name__ == "__main__":
    verify()
