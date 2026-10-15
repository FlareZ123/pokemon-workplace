"""Verify eight-Supporter access under an Aichi Crobat-to-Lumineon swap."""
from __future__ import annotations

from collections import Counter
from datetime import date
import json
from pathlib import Path

from tools.absol_support_tutor_frontier import (
    CATEGORIES, OUTCOMES, CROBAT, LUMINEON, TAPU_LELE, MEGA,
    SUPPORTERS, ITEMS, category_counts, exact_access, physical_oracle,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

ROOT = Path(__file__).resolve().parents[3]
RESOURCES = ROOT / "resources"
BASELINE = ROOT / "results/competitive_deck_baselines/absol_garbodor_kobayashi_2026.json"
VARIANT = ROOT / "results/decks/mega-absol-lumineon-support-tutor/deck.json"

TOYS = (
    dict(mega=1, other_basic=1, tutor=1, evolution=0, quick_ball=1,
         ultra_ball=0, communication=1, heavy_ball=1, energy=1,
         supporter=1, filler=3),
    dict(mega=1, other_basic=1, tutor=2, evolution=0, quick_ball=1,
         ultra_ball=1, communication=1, heavy_ball=1, energy=2,
         supporter=1, filler=1),
    dict(mega=1, other_basic=0, tutor=2, evolution=1, quick_ball=1,
         ultra_ball=1, communication=0, heavy_ball=1, energy=2,
         supporter=1, filler=2),
)


def source_card(card_id: str) -> dict:
    set_id = card_id.rsplit("-", 1)[0]
    return next(
        card for card in json.loads(
            (RESOURCES / "cards" / "en" / f"{set_id}.json").read_text(encoding="utf-8")
        ) if card["id"] == card_id
    )


def check_sources() -> None:
    for card_id, name in ((TAPU_LELE, "Wonder Tag"), (LUMINEON, "Luminous Sign")):
        raw = source_card(card_id)
        assert raw["supertype"] == "Pokémon"
        assert "Basic" in raw["subtypes"]
        assert any(
            ability["name"] == name
            and "from your hand onto your Bench" in ability["text"]
            and "search your deck for a Supporter card" in ability["text"]
            for ability in raw["abilities"]
        )
    assert source_card(CROBAT)["abilities"][0]["name"] == "Dark Asset"
    assert source_card(MEGA)["name"] == "Mega Absol ex"
    assert all("Supporter" in source_card(id)["subtypes"] for id in SUPPORTERS)
    assert any("Pokémon V" in rule for rule in source_card("swsh12-156")["rules"])
    for id, word in ITEMS.items():
        raw = source_card(id)
        assert raw["supertype"] == "Trainer", (id,word)


def verify() -> None:
    for toy in TOYS:
        assert tuple(toy) == CATEGORIES
        exact = exact_access(toy, opening=3, prizes=2)
        physical = physical_oracle(toy, opening=3, prizes=2)
        assert exact == physical, (toy, exact, physical)
    check_sources()
    original = json.loads(BASELINE.read_text(encoding="utf-8"))["cards"]
    changed = json.loads(VARIANT.read_text(encoding="utf-8"))["cards"]
    published = {row["print_id"]: row["quantity"] for row in original}
    replacement = {row["print_id"]: row["quantity"] for row in changed}
    assert len(original) == len(changed) == 37
    assert len(published) == len(replacement) == 37
    assert sum(published.values()) == sum(replacement.values()) == 60
    expected = Counter(published)
    del expected[CROBAT]
    expected[LUMINEON] = 1
    assert replacement == expected, "Only the single Crobat-for-Lumineon slot may change"

    records = load_all_card_records(RESOURCES)
    outputs = {}
    for name, quantities in (("published_crobat",published),("lumineon_swap",replacement)):
        for row in (original if name == "published_crobat" else changed):
            record = records[row["print_id"]]
            assert (record.name,record.supertype) == (row["name"],row["category"])
            assert record.effective_status == "Legal"
        proof = adjudicate_deck(
            tuple(DeckEntry(card_id, qty) for card_id,qty in quantities.items()),
            RESOURCES, as_of=date(2026,10,15),
        )
        assert proof.construction.valid, (name,proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (name,proof.disposition)
        caps = category_counts(quantities,records)
        assert caps["tutor"] == (1 if name == "published_crobat" else 2)
        assert caps["other_basic"] == (7 if name == "published_crobat" else 6)
        assert caps["supporter"] == 8 and caps["energy"] == 7
        out = exact_access(caps)
        assert out["supporter_held"] <= out["held_or_search_supporter"]
        assert out["new_supporter_when_none_held"] == (
            out["held_or_search_supporter"] - out["supporter_held"]
        )
        outputs[name] = out
        print(name+": "+", ".join(f"{k}={float(out[k]):.9%}" for k in OUTCOMES))
    prior = outputs["published_crobat"]
    new = outputs["lumineon_swap"]
    assert new["supporter_held"] == prior["supporter_held"]
    assert new["ability_entry"] > prior["ability_entry"]
    assert new["held_or_search_supporter"] > prior["held_or_search_supporter"]
    # The apparent second tutor's raw access gain is mostly redundancy.
    assert (new["held_or_search_supporter"]-prior["held_or_search_supporter"]) < (
        new["ability_entry"]-prior["ability_entry"]
    )
    assert 0 < float(
        new["held_or_search_supporter"]-prior["held_or_search_supporter"]
    ) < 0.05
    print("PASS: three independently labeled physical toy oracles")
    print("PASS: full source-verified 60-card baseline and exact one-card swap")
    print("PASS: October 15 paper Expanded print and construction checks")
    print("PASS: union marginal distinguishes raw tutor access from held eight Supporters")
    print("LIMIT: excludes Dark Asset draws, Star Alchemy, multiple chained Items and matches")


if __name__ == "__main__":
    verify()
