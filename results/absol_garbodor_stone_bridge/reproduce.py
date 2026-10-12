"""Reproduce the Aichi Mega Absol/Crobat/Forest Seal Stone frontier."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records
from tools.mega_absol_stone_bridge import (
    BAG, CATEGORIES, CROBAT, POLICIES, STONE,
    category_counts, exact_access, physical_oracle,
)

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
MANIFEST = (
    ROOT / "results" / "competitive_deck_baselines"
    / "absol_garbodor_kobayashi_2026.json"
)

# Three independent exhaustive physical-card deal oracles.
TOY_CASES = (
    dict(mega=1, other_basic=1, crobat=1, evolution=1,
         quick_ball=1, ultra_ball=0, vip_pass=1, communication=1,
         heavy_ball=1, energy=2, stone=1, bag=1, filler=0),
    dict(mega=2, other_basic=1, crobat=1, evolution=0,
         quick_ball=1, ultra_ball=1, vip_pass=0, communication=1,
         heavy_ball=1, energy=1, stone=1, bag=1, filler=1),
    dict(mega=1, other_basic=2, crobat=0, evolution=1,
         quick_ball=1, ultra_ball=1, vip_pass=1, communication=0,
         heavy_ball=1, energy=2, stone=1, bag=1, filler=0),
)


def check_card_text(records: dict) -> None:
    expected = {
        CROBAT: ("Dark Asset", "When you play this Pokémon from your hand"),
        STONE: ("Star Alchemy", "search your deck for a card"),
        BAG: ("Search your deck for up to 2 Pokémon Tool cards",),
    }
    for card_id, phrases in expected.items():
        set_id = card_id.rsplit("-", 1)[0]
        raw = next(
            row for row in json.loads(
                (RESOURCES / "cards" / "en" / f"{set_id}.json")
                .read_text(encoding="utf-8")
            ) if row["id"] == card_id
        )
        assert records[card_id].name == raw["name"]
        full_text = "\n".join(
            (raw.get("rules") or ())
            + [a.get("name", "") + " " + a.get("text", "")
               for a in raw.get("abilities") or ()]
        )
        for phrase in phrases:
            assert phrase in full_text, (card_id, phrase)
        if card_id == STONE:
            assert any("Pokémon V" in text for text in raw["rules"])


def verify() -> None:
    for toy in TOY_CASES:
        assert tuple(toy) == CATEGORIES
        assert sum(toy.values()) == 12
        exact = exact_access(toy, opening=3, prizes=2)
        oracle = physical_oracle(toy, opening=3, prizes=2)
        assert exact == oracle, (toy, exact, oracle)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = load_all_card_records(RESOURCES)
    check_card_text(records)
    published = {card["print_id"]: card["quantity"]
                 for card in manifest["cards"]}
    assert len(published) == 37 and sum(published.values()) == 60
    assert published["me1-86"] == 2
    assert published[CROBAT] == 1
    assert published[STONE] == 1
    assert published[BAG] == 1
    assert published["swsh10-155"] == 2

    temple = {**published, "me1-86": 3, "swsh10-155": 1}
    crobat = {**published, "me1-86": 3}
    del crobat[CROBAT]
    cases = {"published": published, "third_mega_cut_temple": temple,
             "third_mega_cut_crobat": crobat}
    results = {}
    for name, quantities in cases.items():
        assert sum(quantities.values()) == 60
        proof = adjudicate_deck(
            tuple(DeckEntry(card_id, count)
                  for card_id, count in quantities.items()),
            RESOURCES, as_of=date(2026, 10, 12),
        )
        assert proof.construction.valid, (name, proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (
            name, proof.disposition
        )
        counts = category_counts(quantities, records)
        assert counts["mega"] == (2 if name == "published" else 3)
        assert counts["crobat"] == (0 if name.endswith("crobat") else 1)
        assert counts["stone"] == counts["bag"] == 1
        output = exact_access(counts)
        assert output["named_or_stone"] >= output["named_paid"]
        assert output["ability_locked"] == output["named_paid"]
        assert output["both_locked"] <= output["item_locked"]
        assert output["item_locked"] <= output["named_or_stone"]
        assert output["stone_any"] == (
            output["stone_held_crobat"] + output["stone_prize_crobat"]
        )
        results[name] = output
        print(name + ": " + ", ".join(
            f"{key}={float(output[key]):.9%}" for key in POLICIES
        ))

    baseline = results["published"]
    keep = results["third_mega_cut_temple"]
    cut = results["third_mega_cut_crobat"]
    assert keep["named_paid"] < cut["named_paid"]
    assert keep["named_or_stone"] > cut["named_or_stone"]
    assert baseline["named_or_stone"] < keep["named_or_stone"]
    assert cut["stone_any"] == cut["crobat_held"] == 0
    assert cut["item_locked"] == cut["both_locked"]
    assert keep["item_locked"] < cut["item_locked"]
    assert keep["ability_locked"] < cut["ability_locked"]
    for state in ("ability_locked", "item_locked", "both_locked"):
        open_advantage = keep["named_or_stone"] - cut["named_or_stone"]
        blocked_advantage = keep[state] - cut[state]
        threshold = open_advantage / (open_advantage - blocked_advantage)
        assert 0 < threshold < 1
        print(f"break_even_{state}_mixture={float(threshold):.9%}")
    print("PASS: three full independently validated tournament-legal 60s")
    print("PASS: three independent exhaustive labeled physical-card oracles")
    print("PASS: ranking inversion after jointly accessible VSTAR Tool route")
    print("LIMIT: no Crobat draw, Ability lock, sequential turns, or match wins")


if __name__ == "__main__":
    verify()
