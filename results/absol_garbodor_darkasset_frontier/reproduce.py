"""Reproduce constrained Dark Asset first-turn payable entry results."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records
from tools.mega_absol_crobat_darkasset import (
    POLICIES, exact_access, physical_oracle, route_flags,
)
from tools.mega_absol_stone_bridge import (
    CATEGORIES, CROBAT, category_counts,
    exact_access as stone_access,
)
from results.absol_garbodor_stone_bridge.reproduce import TOY_CASES

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
MANIFEST = (
    ROOT / "results" / "competitive_deck_baselines"
    / "absol_garbodor_kobayashi_2026.json"
)


def verify() -> None:
    for toy in TOY_CASES:
        assert tuple(toy) == CATEGORIES
        exact = exact_access(toy, opening=3, prizes=2)
        oracle = physical_oracle(toy, opening=3, prizes=2)
        assert exact == oracle, (toy, exact, oracle)
        assert exact["positive_union"] >= exact["direct_positive"]

    records = load_all_card_records(RESOURCES)
    crobat_record = next(
        x for x in json.loads(
            (RESOURCES / "cards" / "en" / "swsh3.json")
            .read_text(encoding="utf-8")
        ) if x["id"] == CROBAT
    )
    assert records[CROBAT].is_basic_pokemon
    assert any(
        ability["name"] == "Dark Asset"
        and "from your hand onto your Bench during your turn"
        in ability["text"]
        and "until you have 6 cards in your hand" in ability["text"]
        for ability in crobat_record["abilities"]
    )
    vip = next(
        x for x in json.loads(
            (RESOURCES / "cards" / "en" / "swsh8.json")
            .read_text(encoding="utf-8")
        ) if x["id"] == "swsh8-225"
    )
    assert any("put them onto your Bench" in s for s in vip["rules"])
    # VIP puts the Pokémon directly from deck onto Bench; Dark Asset's
    # hand-to-Bench trigger is therefore absent in this route.

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    original = {card["print_id"]: card["quantity"]
                for card in manifest["cards"]}
    temple = {**original, "me1-86": 3, "swsh10-155": 1}
    cut = {**original, "me1-86": 3}
    del cut[CROBAT]
    outputs = {}
    for label, deck in (
        ("published", original),
        ("third_mega_cut_temple", temple),
        ("third_mega_cut_crobat", cut),
    ):
        assert sum(deck.values()) == 60
        proof = adjudicate_deck(
            tuple(DeckEntry(card_id, quantity)
                  for card_id, quantity in deck.items()),
            RESOURCES, as_of=date(2026, 10, 12),
        )
        assert proof.disposition == "eligible_snapshot"
        assert proof.construction.valid, (label, proof.construction.issues)
        caps = category_counts(deck, records)
        scores = exact_access(caps)
        assert scores["crobat_seen"] == stone_access(caps)["crobat_held"]
        assert scores["forced_active"] + scores["direct_bench_entry"] == (
            scores["crobat_seen"]
        )
        assert scores["positive_union"] >= scores["direct_positive"]
        outputs[label] = scores
        print(label + ": " + ", ".join(
            f"{key}={float(scores[key]):.9%}" for key in POLICIES
        ))

    assert outputs["published"]["positive_union"] > 0
    assert outputs["third_mega_cut_temple"]["positive_union"] > (
        outputs["published"]["positive_union"]
    )
    assert outputs["third_mega_cut_crobat"]["positive_union"] == 0
    print("PASS: three complete snapshot-legal tournament 60-card cases")
    print("PASS: three exhaustive labeled hand/Prize/draw physical oracles")
    print("PASS: source-checked Dark Asset hand-trigger and VIP exclusion")
    print("LIMIT: one immediate source plus up to one extra Energy/Basic action")
    print("LIMIT: excludes other hand drains, card effects, locks, and wins")


if __name__ == "__main__":
    verify()
