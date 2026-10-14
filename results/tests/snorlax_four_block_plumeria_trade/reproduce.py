"""Validate 4-Block/2-Beach/3-Plumeria paper Expanded counterfactual."""

from __future__ import annotations
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from results.tests.snorlax_starter_draw_frontier.reproduce import (
    BASE, VARIANT, at_least_one_in_seven, combinations,
    counts, metrics, verify_legality,
)
from tools.deck_validator import load_all_card_records

ALT = ROOT / "results/decks/snorlax-stall-4block-2beach-english/manifest.json"


def access(copies: int, basics: int) -> Fraction:
    total = combinations(60, 7)
    joint = (
        total - combinations(60-basics, 7)
        - combinations(60-copies, 7)
        + combinations(60-basics-copies, 7)
    )
    return Fraction(joint, total) / at_least_one_in_seven(basics)


def main() -> None:
    base = json.loads(BASE.read_text(encoding="utf-8"))
    one_beach = json.loads(VARIANT.read_text(encoding="utf-8"))
    two_beach = json.loads(ALT.read_text(encoding="utf-8"))
    expected = counts(base["cards"])
    expected["Snorlax"] += 1
    expected["Plumeria"] -= 1
    assert counts(two_beach["cards"]) == expected
    assert counts(one_beach["cards"])["Tropical Beach"] == 1
    assert counts(two_beach["cards"])["Tropical Beach"] == 2
    assert all(
        {r["name"]: r["print_id"] for r in d["cards"]}
        == {r["name"]: r["print_id"] for r in base["cards"]}
        for d in (one_beach, two_beach)
    )
    assert verify_legality(two_beach["cards"], load_all_card_records(ROOT / "resources")) == 12
    a = metrics(snorlax=4, basics=12, beach=1)
    b = metrics(snorlax=4, basics=12, beach=2)
    assert a["valid_opening"] == b["valid_opening"]
    assert a["snorlax_given_valid"] == b["snorlax_given_valid"]
    assert a["beach_given_valid"] < b["beach_given_valid"]
    assert access(3, 12) < access(4, 12)
    print("PASS: second 60-card English eligible four-Block allocation")
    print("One Beach versus two Beaches (Basic-valid opener):")
    print("  Beach access:", float(a["beach_given_valid"]), float(b["beach_given_valid"]))
    print("  Plumeria access:", float(access(4, 12)), float(access(3, 12)))
    print("LIMIT: constrained card access only; full match strength untested")


if __name__ == "__main__":
    main()
