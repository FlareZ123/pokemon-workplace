"""Reproduce joint Aichi Lumineon/Wonder Tag/Star Alchemy access comparison."""
from __future__ import annotations

from datetime import date
from pathlib import Path
import json

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records
from tools.mega_absol_lumineon_supporter import (
    CROBAT, LUMINEON, MEGA, TARGET, LELE,
    category_counts as name_counts,
    exact_access as name_access,
)
from tools.mega_absol_lumineon_stone_overlap import (
    STONE, BAG, FLAGS, CATEGORIES, category_counts, exact_access,
    physical_oracle,
)

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
MANIFEST = ROOT / "results" / "competitive_deck_baselines" / "absol_garbodor_kobayashi_2026.json"

TOYS = (
    dict(target=1, lele=1, host=1, mega=1, other_basic=1,
         evolution=1, quick=1, ultra=0, comm=1, heavy=1,
         energy=1, stone=1, bag=1, filler=0),
    dict(target=1, lele=1, host=1, mega=1, other_basic=1,
         evolution=0, quick=1, ultra=1, comm=0, heavy=1,
         energy=1, stone=1, bag=1, filler=1),
    dict(target=1, lele=1, host=0, mega=2, other_basic=2,
         evolution=0, quick=1, ultra=1, comm=0, heavy=0,
         energy=1, stone=1, bag=1, filler=1),
)


def verify() -> None:
    for toy in TOYS:
        assert tuple(toy) == CATEGORIES
        assert sum(toy.values()) == 12
        for sign in (False, True):
            exact = exact_access(toy, sign, opening=3, prizes=2)
            oracle = physical_oracle(toy, sign, opening=3, prizes=2)
            assert exact == oracle, (toy, sign, exact, oracle)

    records = load_all_card_records(RESOURCES)
    original = {
        c["print_id"]: c["quantity"] for c in
        json.loads(MANIFEST.read_text(encoding="utf-8"))["cards"]
    }
    assert sum(original.values()) == 60
    assert original[STONE] == original[BAG] == 1
    assert original[LELE] == original[CROBAT] == original[TARGET] == 1
    temple = {**original, MEGA: 3, "swsh10-155": 1}
    lumineon = {**temple, LUMINEON: 1}
    del lumineon[CROBAT]
    out = {}
    for label, quantities, sign in (
        ("published_crobat", original, False),
        ("plus_mega_minus_temple_crobat", temple, False),
        ("plus_mega_minus_temple_lumineon", lumineon, True),
    ):
        assert sum(quantities.values()) == 60
        proof = adjudicate_deck(
            tuple(
                DeckEntry(card_id, count)
                for card_id, count in quantities.items()
            ), RESOURCES, as_of=date(2026, 10, 12),
        )
        assert proof.construction.valid, (label, proof.construction.issues)
        assert proof.disposition == "eligible_snapshot", (
            label, proof.disposition
        )
        counts = category_counts(quantities, records)
        assert counts["host"] == counts["lele"] == counts["target"] == 1
        assert counts["stone"] == counts["bag"] == 1
        assert counts["filler"] >= 0
        linked = exact_access(counts, sign)
        ordinary = name_access(name_counts(quantities, records), sign)
        assert linked["named_body"] == ordinary["target_possession"], (
            label, linked, ordinary,
        )
        assert linked["union_stone"] >= linked["named_body"]
        assert linked["union_stone"] >= linked["stone_any"]
        out[label] = linked
        print(label + ": " + ", ".join(
            f"{key}={float(linked[key]):.9%}" for key in FLAGS
        ))

    crobat = out["plus_mega_minus_temple_crobat"]
    lumineon = out["plus_mega_minus_temple_lumineon"]
    assert crobat["stone_any"] == lumineon["stone_any"]
    assert lumineon["union_stone"] > crobat["union_stone"]
    assert (
        lumineon["union_stone"] - crobat["union_stone"] <
        lumineon["named_body"] - crobat["named_body"]
    )
    print("PASS: 3 paper legal 60s, 6 independent physical toy oracles")
    print("PASS: exact joint target/Lele/host/Stone prize packets")
    print("PASS: Stone/Sign connector-overlap narrows marginal Lumineon gain")
    print("LIMIT: one named Item bridge plus Tool, no deeper sequences or wins")


if __name__ == "__main__":
    verify()
