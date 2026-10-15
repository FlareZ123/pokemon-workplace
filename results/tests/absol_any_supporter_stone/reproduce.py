"""Validate all-eight-Supporter / Star Alchemy overlap at exact paper prints."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from tools.absol_any_supporter_stone import (
    CATEGORIES, OUTCOMES, STONE, BAG,
    category_counts, collapse_roles, exact_access, physical_oracle,
)
from tools.absol_support_tutor_frontier import (
    CROBAT, LUMINEON, TAPU_LELE, SUPPORTERS,
    exact_access as old_access, category_counts as old_counts,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

ROOT = Path(__file__).resolve().parents[3]
RESOURCES = ROOT / "resources"
SOURCE = ROOT / "results/competitive_deck_baselines/absol_garbodor_kobayashi_2026.json"
VARIANT = ROOT / "results/decks/mega-absol-lumineon-support-tutor/deck.json"

TOYS = (
    dict(mega=1, other_basic=1, lele=1, host=1, evolution=0,
         quick_ball=1, ultra_ball=0, communication=1, heavy_ball=1,
         energy=1, supporter=1, stone=1, bag=1, filler=0),
    dict(mega=1, other_basic=0, lele=1, host=1, evolution=1,
         quick_ball=1, ultra_ball=1, communication=1, heavy_ball=1,
         energy=1, supporter=1, stone=1, bag=0, filler=0),
    dict(mega=2, other_basic=1, lele=0, host=1, evolution=0,
         quick_ball=1, ultra_ball=0, communication=1, heavy_ball=1,
         energy=1, supporter=1, stone=1, bag=0, filler=0),
)


def raw_card(card_id: str) -> dict:
    set_id = card_id.rsplit("-", 1)[0]
    return next(
        c for c in json.loads(
            (RESOURCES / "cards" / "en" / (set_id + ".json"))
            .read_text(encoding="utf-8")
        ) if c["id"] == card_id
    )


def verify() -> None:
    for toy in TOYS:
        assert tuple(toy) == CATEGORIES
        for with_sign in (False, True):
            exact = exact_access(toy, with_sign, opening=3, prizes=2)
            physical = physical_oracle(toy, with_sign, opening=3, prizes=2)
            assert exact == physical, (toy, with_sign, exact, physical)
            original = old_access(collapse_roles(toy, with_sign), opening=3, prizes=2)
            assert exact["tutor_or_held"] == original["held_or_search_supporter"]

    assert raw_card(STONE)["name"] == "Forest Seal Stone"
    assert "Star Alchemy" == raw_card(STONE)["abilities"][0]["name"]
    assert any("Pokémon V" in rule for rule in raw_card(STONE)["rules"])
    assert any("Search your deck for up to 2 Pokémon Tool cards" in x
               for x in raw_card(BAG)["rules"])
    assert raw_card(LUMINEON)["abilities"][0]["name"] == "Luminous Sign"
    assert raw_card(CROBAT)["abilities"][0]["name"] == "Dark Asset"
    assert raw_card(TAPU_LELE)["abilities"][0]["name"] == "Wonder Tag"
    assert len(SUPPORTERS) == 8

    cases = (
        ("published_crobat", SOURCE, False),
        ("lumineon_swap", VARIANT, True),
    )
    records = load_all_card_records(RESOURCES)
    results = {}
    for label, manifest, with_sign in cases:
        lines = json.loads(manifest.read_text(encoding="utf-8"))["cards"]
        printed = {card["print_id"]: card["quantity"] for card in lines}
        assert len(printed) == len(lines) == 37
        assert sum(printed.values()) == 60
        proof = adjudicate_deck(
            tuple(DeckEntry(card_id, qty) for card_id, qty in printed.items()),
            RESOURCES, as_of=date(2026, 10, 15),
        )
        assert proof.construction.valid, (label, proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (label, proof.disposition)
        counted = category_counts(printed, records)
        assert counted["lele"] == counted["host"] == 1
        assert counted["supporter"] == 8 and counted["energy"] == 7
        assert counted["stone"] == counted["bag"] == 1
        assert counted["other_basic"] == 6 and counted["mega"] == 2
        exact = exact_access(counted, with_sign)
        original = old_access(old_counts(printed, records))
        assert exact["held_supporter"] == original["supporter_held"]
        assert exact["tutor_or_held"] == original["held_or_search_supporter"]
        assert exact["held_tutor_or_stone"] == (
            exact["tutor_or_held"] + exact["stone_new_when_tutor_fails"]
        )
        assert exact["stone_any"] >= exact["stone_direct"]
        results[label] = exact
        print(label+": "+", ".join(f"{key}={float(exact[key]):.9%}" for key in OUTCOMES))

    crobat = results["published_crobat"]
    lumineon = results["lumineon_swap"]
    assert crobat["stone_any"] == lumineon["stone_any"]
    raw_gain = lumineon["tutor_or_held"]-crobat["tutor_or_held"]
    stone_gain = lumineon["held_tutor_or_stone"]-crobat["held_tutor_or_stone"]
    assert 0 < stone_gain < raw_gain
    print(f"raw_tutor_gain_pp={float(raw_gain)*100:.9f}")
    print(f"stone_adjusted_gain_pp={float(stone_gain)*100:.9f}")
    print(f"shared_stone_redundancy_pp={float(raw_gain-stone_gain)*100:.9f}")
    print("PASS: six toy labeled physical world enumerations and exact old-solver bridge")
    print("PASS: two full October 15 paper Expanded 60-card construction proofs")
    print("LIMIT: static one-Item route, no Dark Asset draw, engine play or wins")


if __name__ == "__main__":
    verify()
