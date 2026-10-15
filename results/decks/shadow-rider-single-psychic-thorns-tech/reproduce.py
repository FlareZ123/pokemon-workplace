"""Print-aware proof for two full one-slot Shadow Rider counter variants."""
from __future__ import annotations

from collections import Counter
from datetime import date
from fractions import Fraction
from math import comb
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    POKEMON, TRAINERS, ENERGY, PRINT_IDS,
)
from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records


POKEMON_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|[^|]+\|\s*([a-z][a-z0-9]*-[a-zA-Z0-9]+)\s*\|$"
)
SHARED_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|[^|]+\|\s*([a-z][a-z0-9]*-[a-zA-Z0-9]+)\s*\|$"
)
TECHS = {"A": "sv5-78", "B": "xy4-36"}


def expected_original() -> Counter[str]:
    quantities = {**POKEMON, **TRAINERS, **ENERGY}
    assert len(quantities) == len(PRINT_IDS) == 33
    return Counter({PRINT_IDS[name]: qty for name, qty in quantities.items()})


def documented_variants():
    readme = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")
    pokemon = readme.split("### Pokémon (18 per variant)", 1)[1].split(
        "### Trainers (31 per variant)", 1
    )[0]
    trainers = readme.split("### Trainers (31 per variant)", 1)[1].split(
        "### Energy (11 per variant)", 1
    )[0]
    energy = readme.split("### Energy (11 per variant)", 1)[1].split(
        "## Why these two alternatives", 1
    )[0]
    a = Counter()
    b = Counter()
    for line in pokemon.splitlines():
        match = POKEMON_ROW.fullmatch(line.strip())
        if match:
            aq, bq, cid = match.groups()
            a[cid] += int(aq)
            b[cid] += int(bq)
    for line in (trainers + energy).splitlines():
        match = SHARED_ROW.fullmatch(line.strip())
        if match:
            qty, cid = match.groups()
            a[cid] += int(qty)
            b[cid] += int(qty)
    # Counter retains explicit zero rows for the other variant tech.\n    # Remove these rows before checking printed deck diversity and counts.\n    return {"A": +a, "B": +b}\n

def main() -> None:
    original = expected_original()
    actual = documented_variants()
    records = load_all_card_records(ROOT / "resources")

    for label, tech_id in TECHS.items():
        expected = original.copy()
        expected["sv9-56"] -= 1
        expected[tech_id] += 1
        documented = actual[label]
        assert documented == expected, (label, documented - expected, expected - documented)
        assert sum(documented.values()) == 60
        assert len(documented) == 34
        assert all(qty > 0 for qty in documented.values())
        assert sum(
            qty for cid, qty in documented.items() if records[cid].is_basic_pokemon
        ) == 14
        proof = adjudicate_deck(
            (DeckEntry(cid, qty) for cid, qty in documented.items()),
            ROOT / "resources",
            as_of=date(2026, 10, 15),
        )
        assert proof.construction.valid, proof.construction.issues
        assert proof.disposition == "eligible_snapshot", [
            (row.card_id, row.eligibility, row.reason)
            for row in proof.print_proofs if row.eligibility != "eligible"
        ]
        assert all(row.eligibility == "eligible" for row in proof.print_proofs)
        print(
            f"PASS {label} ({records[tech_id].name}): 60 legal cards, "
            "18 Pokemon / 31 Trainer / 11 Energy, 14 Basics; "
            "exactly one Clefairy-to-counter swap"
        )

    valid = 1 - Fraction(comb(46, 7), comb(60, 7))
    seen = Fraction(7, 60) / valid
    assert round(100 * float(valid), 6) == 86.140932
    assert round(100 * float(seen), 6) == 13.543697
    print("Both full 60-card candidates match documented lists and print proof")


if __name__ == "__main__":
    main()
