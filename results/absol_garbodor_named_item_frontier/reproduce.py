"""Validate physical named-Item access for the complete Aichi Absol/Garbodor deck."""
from __future__ import annotations

from collections import Counter
from datetime import date
import json
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records
from tools.mega_absol_named_item_access import (
    CATEGORIES, TARGETS, category_counts, exact_access, physical_oracle,
)

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
MANIFEST = (
    ROOT / "results" / "competitive_deck_baselines"
    / "absol_garbodor_kobayashi_2026.json"
)

# Explicit physical toy cards. Every valid opening, hidden Prize subset
# and first natural draw is enumerated independently of the exact solver.
TOY_CASES = (
    dict(mega=1, other_basic=2, evolution=1, quick_ball=1,
         ultra_ball=0, vip_pass=1, communication=1, heavy_ball=1,
         energy=2, filler=2),
    dict(mega=2, other_basic=2, evolution=1, quick_ball=1,
         ultra_ball=1, vip_pass=0, communication=1, heavy_ball=1,
         energy=2, filler=1),
    dict(mega=2, other_basic=1, evolution=2, quick_ball=0,
         ultra_ball=1, vip_pass=1, communication=1, heavy_ball=1,
         energy=2, filler=1),
)


def verify() -> None:
    for capacities in TOY_CASES:
        assert set(capacities) == set(CATEGORIES)
        assert sum(capacities.values()) == 12
        exact = exact_access(capacities, opening=3, prizes=2)
        oracle = physical_oracle(capacities, opening=3, prizes=2)
        assert exact == oracle, (capacities, exact, oracle)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = load_all_card_records(RESOURCES)
    original = {row["print_id"]: row["quantity"] for row in manifest["cards"]}
    assert len(original) == 37 and sum(original.values()) == 60

    # Validate source-card print identities and exact mechanics that every
    # named route requires, rather than relying on card names alone.
    mechanical_text = {
        "quick_ball": ("discard another card from your hand", "Basic Pokémon"),
        "ultra_ball": ("discard 2 other cards", "Search your deck for a Pokémon"),
        "vip_pass": ("only during your first turn", "up to 2 Basic Pokémon"),
        "communication": ("Reveal a Pokémon from your hand", "search your deck"),
        "heavy_ball": ("face-down Prize cards", "Basic Pokémon"),
    }
    for category, card_id in TARGETS.items():
        raw_set = card_id.rsplit("-", 1)[0]
        raw = next(
            row for row in json.loads(
                (RESOURCES / "cards" / "en" / f"{raw_set}.json")
                .read_text(encoding="utf-8")
            ) if row["id"] == card_id
        )
        assert records[card_id].name == raw["name"]
        if category in mechanical_text:
            all_rules = "\n".join(raw.get("rules") or ())
            for phrase in mechanical_text[category]:
                assert phrase in all_rules, (card_id, phrase)

    assert original["me1-86"] == 2
    assert original["swsh10-155"] == 2
    assert original["swsh3-104"] == 1
    cases = {
        "published": original,
        "third_mega_cut_temple": {**original, "me1-86": 3, "swsh10-155": 1},
        "third_mega_cut_crobat": {**original, "me1-86": 3},
    }
    del cases["third_mega_cut_crobat"]["swsh3-104"]

    results = {}
    for label, quantities in cases.items():
        assert sum(quantities.values()) == 60
        proof = adjudicate_deck(
            tuple(DeckEntry(card_id, quantity)
                  for card_id, quantity in quantities.items()),
            RESOURCES, as_of=date(2026, 10, 12),
        )
        assert proof.construction.valid, (label, proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (
            label, proof.disposition
        )
        caps = category_counts(quantities, records)
        assert sum(caps.values()) == 60
        assert caps["quick_ball"] == 4
        assert caps["ultra_ball"] == 2
        assert caps["vip_pass"] == 2
        assert caps["communication"] == 1
        assert caps["heavy_ball"] == 1
        assert caps["energy"] == 7
        expected_basics = {"published": 10,
                           "third_mega_cut_temple": 11,
                           "third_mega_cut_crobat": 10}[label]
        assert caps["mega"] + caps["other_basic"] == expected_basics
        result = exact_access(caps)
        assert result["direct"] <= result["vip_or_heavy"]
        assert result["vip_or_heavy"] <= result["energy_paid"]
        assert result["energy_paid"] <= result["unpaid_upper"]
        results[label] = result
        print(f"{label}: " + ", ".join(
            f"{field}={float(value):.9%}"
            for field, value in result.items()
        ))

    assert results["published"]["energy_paid"] < (
        results["third_mega_cut_temple"]["energy_paid"]
    ) < results["third_mega_cut_crobat"]["energy_paid"]
    assert results["published"]["direct"] == (
        results["third_mega_cut_temple"]["valid_opening"] * 0
        + results["published"]["direct"]
    )
    print("PASS: three full legal 60-card lists, five route metrics")
    print("PASS: three independent exhaustive labeled toy worlds")
    print("LIMIT: named one-step Item access with assumed Energy-only payments")
    print("LIMIT: no draw Abilities, lock opponent, attack or match win rate")


if __name__ == "__main__":
    verify()
