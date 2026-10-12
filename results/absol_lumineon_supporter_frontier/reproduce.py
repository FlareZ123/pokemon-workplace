"""Reproduce full legal Aichi Crobat-to-Lumineon Supporter access frontier."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records
from tools.mega_absol_lumineon_supporter import (
    CATEGORIES, FLAGS, TARGET, LELE, CROBAT, LUMINEON, MEGA,
    category_counts, exact_access, physical_oracle,
)

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
MANIFEST = (
    ROOT / "results" / "competitive_deck_baselines"
    / "absol_garbodor_kobayashi_2026.json"
)
TOYS = (
    dict(target=1, lele=1, host=1, mega=1, other_basic=2,
         evolution=1, quick=1, ultra=0, comm=1, heavy=1, energy=1,
         filler=1),
    dict(target=1, lele=1, host=1, mega=1, other_basic=1,
         evolution=0, quick=1, ultra=1, comm=1, heavy=1, energy=2,
         filler=1),
    dict(target=1, lele=1, host=0, mega=2, other_basic=2,
         evolution=0, quick=1, ultra=1, comm=1, heavy=1, energy=1,
         filler=1),
)


def source_card(card_id: str) -> dict:
    set_id = card_id.rsplit("-", 1)[0]
    return next(
        row for row in json.loads(
            (RESOURCES / "cards" / "en" / f"{set_id}.json")
            .read_text(encoding="utf-8")
        ) if row["id"] == card_id
    )


def verify() -> None:
    for toy in TOYS:
        assert tuple(toy) == CATEGORIES
        assert sum(toy.values()) == 12
        for sign in (False, True):
            exact = exact_access(toy, sign, opening=3, prizes=2)
            physical = physical_oracle(toy, sign, opening=3, prizes=2)
            assert exact == physical, (toy, sign, exact, physical)

    records = load_all_card_records(RESOURCES)
    for body, ability in ((LELE, "Wonder Tag"), (LUMINEON, "Luminous Sign")):
        raw = source_card(body)
        assert raw["supertype"] == "Pokémon"
        assert "Basic" in raw["subtypes"]
        assert records[body].is_basic_pokemon
        assert len(raw["abilities"]) == 1
        assert raw["abilities"][0]["name"] == ability
        assert (
            "When you play this Pokémon from your hand onto your Bench"
            in raw["abilities"][0]["text"]
        )
        assert "search your deck for a Supporter card" in (
            raw["abilities"][0]["text"]
        )
    assert source_card(TARGET)["name"] == "Crispin"
    assert "Supporter" in source_card(TARGET)["subtypes"]
    assert "V" in source_card(LUMINEON)["subtypes"]
    assert "V" in source_card(CROBAT)["subtypes"]
    assert any(
        "Pokémon V" in rule for rule in source_card("swsh12-156")["rules"]
    )
    assert source_card(CROBAT)["abilities"][0]["name"] == "Dark Asset"

    published = {
        c["print_id"]: c["quantity"] for c in
        json.loads(MANIFEST.read_text(encoding="utf-8"))["cards"]
    }
    assert len(published) == 37 and sum(published.values()) == 60
    assert published[CROBAT] == 1
    assert published[LELE] == published[TARGET] == 1
    assert published["swsh10-155"] == 2
    keep = {**published, MEGA: 3, "swsh10-155": 1}
    lumineon = {**keep, LUMINEON: 1}
    del lumineon[CROBAT]
    results = {}
    for title, quantities, has_sign in (
        ("published_crobat", published, False),
        ("plus_mega_cut_temple_crobat", keep, False),
        ("plus_mega_cut_temple_lumineon", lumineon, True),
    ):
        assert sum(quantities.values()) == 60
        proof = adjudicate_deck(
            tuple(
                DeckEntry(card_id, count)
                for card_id, count in quantities.items()
            ), RESOURCES, as_of=date(2026, 10, 12),
        )
        assert proof.construction.valid, (title, proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (
            title, proof.disposition
        )
        caps = category_counts(quantities, records)
        assert caps["host"] == caps["lele"] == caps["target"] == 1
        assert caps["quick"] == 4 and caps["ultra"] == 2
        assert caps["comm"] == caps["heavy"] == 1
        assert caps["energy"] == 7
        assert caps["mega"] == (2 if title == "published_crobat" else 3)
        output = exact_access(caps, has_sign)
        results[title] = output
        print(title + ": " + ", ".join(
            f"{key}={float(output[key]):.9%}" for key in FLAGS
        ))
    keep_crobat = results["plus_mega_cut_temple_crobat"]
    keep_lumineon = results["plus_mega_cut_temple_lumineon"]
    assert (
        keep_lumineon["target_held"] == keep_crobat["target_held"]
    )
    assert (
        keep_lumineon["target_possession"]
        > keep_crobat["target_possession"]
    )
    assert (
        keep_lumineon["target_possession"]
        - keep_crobat["target_possession"]
        > 0
    )
    print("PASS: three fully validated October 12 paper Expanded 60s")
    print("PASS: six independent (3 physical toy x 2 policies) oracles")
    print("PASS: source card hand-entry trigger and V host verified")
    print("LIMIT: Supporter access, not its usage, setup line or match wins")


if __name__ == "__main__":
    verify()
