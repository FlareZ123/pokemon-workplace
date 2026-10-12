"""Exact joint Crobat V / Forest Seal Stone search route in Aichi Mega Absol."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records
from tools.mega_absol_named_item_access import exact_access as named_exact
from tools.mega_absol_seal_stone_bridge import (
    CATEGORIES, category_counts, exact_access, physical_oracle,
    project_named_categories,
)

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
MANIFEST = (
    ROOT / "results" / "competitive_deck_baselines"
    / "absol_garbodor_kobayashi_2026.json"
)

TOY_CASES = (
    dict(mega=1, other_basic=1, crobat=1, evolution=0,
         quick_ball=1, ultra_ball=0, vip_pass=0, communication=1,
         heavy_ball=1, energy=2, forest_seal_stone=1,
         adventure_bag=1, filler=2),
    dict(mega=2, other_basic=1, crobat=0, evolution=1,
         quick_ball=1, ultra_ball=1, vip_pass=1, communication=1,
         heavy_ball=0, energy=1, forest_seal_stone=1,
         adventure_bag=1, filler=1),
    dict(mega=1, other_basic=2, crobat=1, evolution=1,
         quick_ball=0, ultra_ball=1, vip_pass=1, communication=0,
         heavy_ball=1, energy=1, forest_seal_stone=1,
         adventure_bag=1, filler=1),
)


def verify() -> None:
    for toy in TOY_CASES:
        assert set(toy) == set(CATEGORIES) and sum(toy.values()) == 12
        exact = exact_access(toy, opening=3, prizes=2)
        brute = physical_oracle(toy, opening=3, prizes=2)
        assert exact == brute, (toy, exact, brute)
        assert exact["paid_item"] == (
            named_exact(
                project_named_categories(toy), opening=3, prizes=2
            )["energy_paid"]
        )

    source = json.loads(MANIFEST.read_text(encoding="utf-8"))["cards"]
    quantities = {row["print_id"]: row["quantity"] for row in source}
    assert sum(quantities.values()) == 60
    records = load_all_card_records(RESOURCES)

    # No other Pokémon V appears in the source deck. Mega Pokémon ex,
    # Pokémon-GX and other Rule Boxes cannot wield Star Alchemy.
    v_cards = {
        card_id: qty for card_id, qty in quantities.items()
        if "V" in records[card_id].subtypes
    }
    assert v_cards == {"swsh3-104": 1}, v_cards
    assert quantities["swsh12-156"] == 1
    assert quantities["sm8-167"] == 1

    def source_card(card_id):
        set_id = card_id.rsplit("-", 1)[0]
        return next(
            row for row in json.loads(
                (RESOURCES / "cards" / "en" / f"{set_id}.json")
                .read_text(encoding="utf-8")
            ) if row["id"] == card_id
        )

    seal = source_card("swsh12-156")
    crobat = source_card("swsh3-104")
    bag = source_card("sm8-167")
    assert any(
        "The Pokémon V this card is attached to" in rule
        for rule in seal["rules"]
    )
    assert any(
        move["name"] == "Star Alchemy"
        and "search your deck for a card" in move["text"]
        for move in seal["abilities"]
    )
    assert any(
        move["name"] == "Dark Asset"
        for move in crobat["abilities"]
    )
    assert any(
        "Search your deck for up to 2 Pokémon Tool cards" in rule
        for rule in bag["rules"]
    )

    cases = {
        "published": quantities,
        "third_mega_cut_temple": {
            **quantities, "me1-86": 3, "swsh10-155": 1,
        },
        "third_mega_cut_crobat": {
            **quantities, "me1-86": 3,
        },
    }
    del cases["third_mega_cut_crobat"]["swsh3-104"]

    scores = {}
    for name, deck in cases.items():
        proof = adjudicate_deck(
            tuple(DeckEntry(card_id, number)
                  for card_id, number in deck.items()),
            RESOURCES, as_of=date(2026, 10, 12),
        )
        assert proof.disposition == "eligible_snapshot"
        assert proof.construction.valid
        caps = category_counts(deck, records)
        assert caps["forest_seal_stone"] == 1
        assert caps["adventure_bag"] == 1
        assert caps["crobat"] == (0 if name.endswith("crobat") else 1)
        result = exact_access(caps)
        assert result["paid_item"] == named_exact(
            project_named_categories(caps)
        )["energy_paid"]
        assert (
            result["paid_plus_seal"]
            == result["paid_item"] + result["seal_increment"]
        )
        scores[name] = result
        print(name + ": " + ", ".join(
            f"{key}={float(value):.9%}"
            for key, value in result.items()
        ))

    assert scores["published"]["seal_increment"] > 0
    assert scores["third_mega_cut_temple"]["seal_increment"] > 0
    assert scores["third_mega_cut_crobat"]["seal_increment"] == 0
    assert (
        scores["third_mega_cut_temple"]["paid_plus_seal"]
        > scores["third_mega_cut_crobat"]["paid_plus_seal"]
    )
    print("PASS: exact physical two-target Prize math and toy oracle")
    print("PASS: conservative legality, cross-model marginal, Crobat-only V")
    print("LIMIT: prelock Crobat held, VSTAR Power unused, no Dark Asset draw")
    print("LIMIT: one named paid Item or Crobat/Seal route; no matchup wins")


if __name__ == "__main__":
    verify()
