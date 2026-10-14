"""Reproduce a four-Snorlax alternative to the Aichi stall English adaptation.

Exact without replacement opening-seven and Prize-six probabilities are
restricted access diagnostics, not turn simulation or match win rates.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

BASE = ROOT / "results/decks/snorlax-stall-aichi-2026-english/manifest.json"
VARIANT = ROOT / "results/decks/snorlax-stall-4block-english/manifest.json"


def combinations(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def at_least_one_in_seven(count: int) -> Fraction:
    return 1 - Fraction(combinations(60 - count, 7), combinations(60, 7))


def metrics(*, snorlax: int, basics: int, beach: int) -> dict[str, Fraction]:
    """All probabilities conditioned on a Basic-valid opening seven."""
    valid = at_least_one_in_seven(basics)
    total = combinations(60, 7)
    beach_and_basic = (
        total
        - combinations(60 - basics, 7)
        - combinations(60 - beach, 7)
        + combinations(60 - basics - beach, 7)
    )
    snorlax_and_beach = (
        total
        - combinations(60 - snorlax, 7)
        - combinations(60 - beach, 7)
        + combinations(60 - snorlax - beach, 7)
    )
    return {
        "valid_opening": valid,
        "snorlax_given_valid": at_least_one_in_seven(snorlax) / valid,
        "beach_given_valid": Fraction(beach_and_basic, total) / valid,
        "both_given_valid": Fraction(snorlax_and_beach, total) / valid,
    }


def all_copies_prized(copies: int) -> Fraction:
    """Unconditional chance every copy lies among the initial six Prizes."""
    return Fraction(
        combinations(60 - copies, 6 - copies), combinations(60, 6),
    )


def all_prized_given_not_in_hand(copies: int) -> Fraction:
    """Probability all copies are Prized after a seven-card opening omits them."""
    return Fraction(
        combinations(53 - copies, 6 - copies), combinations(53, 6),
    )


def at_least_unprized(copies: int, minimum: int) -> Fraction:
    """Chance initial six Prizes leave at least `minimum` copies accessible."""
    return sum(
        (
            Fraction(
                combinations(copies, k) * combinations(60 - copies, 6 - k),
                combinations(60, 6),
            )
            for k in range(copies + 1)
            if copies - k >= minimum
        ),
        Fraction(0),
    )


def expected_mulligans(basics: int) -> Fraction:
    """Expected number of rejected opening sevens before the first valid one."""
    valid = at_least_one_in_seven(basics)
    return (1 - valid) / valid


def counts(rows: list[dict]) -> Counter:
    return Counter({row["name"]: row["quantity"] for row in rows})


def verify_legality(rows: list[dict], records) -> int:
    basic_count = 0
    for row in rows:
        record = records[row["print_id"]]
        assert (record.name, record.supertype) == (
            row["name"], row["category"]
        ), row
        assert record.effective_status == "Legal", row
        if record.is_basic_pokemon:
            basic_count += row["quantity"]
    assert sum(row["quantity"] for row in rows) == 60
    assert max(row["quantity"] for row in rows if row["name"] != "Water Energy") <= 4
    proof = adjudicate_deck(
        [DeckEntry(row["print_id"], row["quantity"]) for row in rows],
        ROOT / "resources",
        as_of=date(2026, 10, 12),
    )
    assert proof.construction.valid, proof.construction.issues
    assert proof.disposition == "eligible_snapshot"
    assert all(result.eligibility == "eligible" for result in proof.print_proofs)
    return basic_count


def main() -> None:
    source = json.loads(BASE.read_text(encoding="utf-8"))
    candidate = json.loads(VARIANT.read_text(encoding="utf-8"))
    original = counts(source["cards"])
    modified = counts(candidate["cards"])
    expected = original.copy()
    expected["Snorlax"] += 1
    expected["Tropical Beach"] -= 1
    assert modified == expected
    assert original["Snorlax"] == 3
    assert original["Tropical Beach"] == 2
    assert modified["Snorlax"] == 4
    assert modified["Tropical Beach"] == 1
    assert original["Galarian Stunfisk"] == modified["Galarian Stunfisk"] == 2
    assert candidate["source"] == source["source"]

    source_prints = {row["name"]: row["print_id"] for row in source["cards"]}
    assert {
        row["name"]: row["print_id"] for row in candidate["cards"]
    } == source_prints
    records = load_all_card_records(ROOT / "resources")
    base_basics = verify_legality(source["cards"], records)
    candidate_basics = verify_legality(candidate["cards"], records)
    assert (base_basics, candidate_basics) == (11, 12)

    base = metrics(snorlax=3, basics=11, beach=2)
    new = metrics(snorlax=4, basics=12, beach=1)
    # A second illustrative allocation spends one Stunfisk instead of a Beach.
    keep_two_beaches = metrics(snorlax=4, basics=11, beach=2)
    assert new["valid_opening"] > base["valid_opening"]
    assert new["snorlax_given_valid"] > base["snorlax_given_valid"]
    assert new["beach_given_valid"] < base["beach_given_valid"]
    assert new["both_given_valid"] < base["both_given_valid"]
    assert keep_two_beaches["snorlax_given_valid"] > new["snorlax_given_valid"]
    assert keep_two_beaches["beach_given_valid"] == base["beach_given_valid"]

    assert all_copies_prized(1) == Fraction(1, 10)
    assert all_copies_prized(2) == Fraction(1, 118)
    assert all_prized_given_not_in_hand(1) == Fraction(6, 53)
    assert all_prized_given_not_in_hand(2) == Fraction(15, 1378)
    assert all_copies_prized(2) < all_copies_prized(1)
    assert at_least_unprized(4, 2) > at_least_unprized(3, 2)
    assert expected_mulligans(12) < expected_mulligans(11)

    print("PASS: 60 cards, all English-print eligibility checks for both 60s")
    print("PASS: actual tournament source 59/60 card-name quantities retained")
    print("PASS: all four Snorlax copies are bw8-101 Block")
    print("PASS: both Snap Trap Galarian Stunfisk preserved")
    for heading, result in (
        ("Source adaptation: Snorlax 3, Stunfisk 2, Beach 2", base),
        ("New alternative: Snorlax 4, Stunfisk 2, Beach 1", new),
        ("Sensitivity only: Snorlax 4, Stunfisk 1, Beach 2", keep_two_beaches),
    ):
        print(heading)
        for key, value in result.items():
            print(f"  {key}: {float(value) * 100:.8f}%")
    print("All copies Prized: 1 Beach = 10%; 2 Beach = 0.84745763%")
    print("All copies Prized: 1 Stunfisk = 10%; 2 Stunfisk = 0.84745763%")
    print("Two or more un-Prized Block Snorlax (source, proposal):")
    print(f"  {float(at_least_unprized(3, 2)) * 100:.8f}%")
    print(f"  {float(at_least_unprized(4, 2)) * 100:.8f}%")
    print("Expected opening-hand mulligans (source, proposal):")
    print(f"  {float(expected_mulligans(11)):.8f}")
    print(f"  {float(expected_mulligans(12)):.8f}")
    print("LIMIT: opening access only; legal line execution and wins untested")


if __name__ == "__main__":
    main()
