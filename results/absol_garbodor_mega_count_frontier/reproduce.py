"""Exact initial Mega Absol access in the 2026 Aichi eighth-place deck.

Conditional on at least one Basic in the seven-card opening hand.
Six Prize cards are dealt after the hand, followed by one natural draw.
This models visible card identity, not searches, payments, Energy or attacks.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import json

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry, load_all_card_records

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
MANIFEST = ROOT / "results" / "competitive_deck_baselines" / "absol_garbodor_kobayashi_2026.json"
MEGA = "me1-86"
CUT_NONBASIC = "swsh10-155"  # Temple of Sinnoh, 2 -> 1
CUT_OTHER_BASIC = "swsh3-104"  # Crobat V, 1 -> 0


def exact_counts(n: int, mega: int, basics: int, opening: int, prizes: int):
    all_open = comb(n, opening)
    valid = all_open - comb(n - basics, opening)
    held = all_open - comb(n - mega, opening)
    no_mega_valid = comb(n - mega, opening) - comb(n - basics, opening)
    prize_event = (
        Fraction(comb(n - opening - mega, prizes - mega), comb(n - opening, prizes))
        if mega <= prizes else Fraction(0)
    )
    return {
        "valid_opening": Fraction(valid, all_open),
        "opening_mega_given_valid": Fraction(held, valid),
        "held_mega_by_first_draw_given_valid": (
            Fraction(held, valid)
            + Fraction(no_mega_valid, valid) * Fraction(mega, n - opening)
        ),
        "all_mega_prized_given_valid": Fraction(no_mega_valid, valid) * prize_event,
    }


def brute_counts(n: int, mega: int, basics: int, opening: int, prizes: int):
    universe = set(range(n))
    mega_cards = set(range(mega))
    basic_cards = set(range(basics))
    valid_openers = 0
    held_openers = 0
    valid_completed = 0
    held_by_first_draw = 0
    all_prized = 0
    for hand_tuple in combinations(range(n), opening):
        hand = set(hand_tuple)
        if not hand.intersection(basic_cards):
            continue
        valid_openers += 1
        held_openers += bool(hand.intersection(mega_cards))
        remaining = universe - hand
        for prize_tuple in combinations(sorted(remaining), prizes):
            prize_cards = set(prize_tuple)
            for draw in remaining - prize_cards:
                valid_completed += 1
                held_by_first_draw += bool(hand.intersection(mega_cards) or draw in mega_cards)
                all_prized += mega_cards.issubset(prize_cards)
    return {
        "valid_opening": Fraction(valid_openers, comb(n, opening)),
        "opening_mega_given_valid": Fraction(held_openers, valid_openers),
        "held_mega_by_first_draw_given_valid": Fraction(held_by_first_draw, valid_completed),
        "all_mega_prized_given_valid": Fraction(all_prized, valid_completed),
    }


def verify() -> None:
    # Enumerate every labeled hand, Prize combination, and natural-draw
    # outcome in three distinct toy deck sizes, independently of the formula.
    for params in ((10, 1, 3, 2, 2), (10, 2, 4, 3, 2), (12, 3, 5, 3, 3)):
        exact = exact_counts(*params)
        brute = brute_counts(*params)
        assert exact == brute, (params, exact, brute)

    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))["cards"]
    records = load_all_card_records(RESOURCES)
    original = {row["print_id"]: row["quantity"] for row in rows}
    assert len(original) == 37 and sum(original.values()) == 60
    assert original[MEGA] == 2
    assert original[CUT_NONBASIC] == 2
    assert original[CUT_OTHER_BASIC] == 1
    assert records[MEGA].is_basic_pokemon
    assert records[CUT_OTHER_BASIC].is_basic_pokemon
    assert not records[CUT_NONBASIC].is_basic_pokemon

    cases = [
        ("published", original),
        ("third_mega_cut_temple", dict(original)),
        ("third_mega_cut_crobat", dict(original)),
    ]
    cases[1][1][MEGA] += 1
    cases[1][1][CUT_NONBASIC] -= 1
    cases[2][1][MEGA] += 1
    del cases[2][1][CUT_OTHER_BASIC]

    outputs = {}
    for title, quantities in cases:
        assert sum(quantities.values()) == 60
        proof = adjudicate_deck(
            [DeckEntry(card_id, count) for card_id, count in quantities.items()],
            RESOURCES,
            as_of=__import__("datetime").date(2026, 10, 12),
        )
        assert proof.disposition == "eligible_snapshot", (title, proof.disposition)
        assert proof.construction.valid, (title, proof.construction.issues)
        basics = sum(
            count for card_id, count in quantities.items()
            if records[card_id].is_basic_pokemon
        )
        result = exact_counts(60, quantities[MEGA], basics, 7, 6)
        outputs[title] = result
        print(
            title, "mega=", quantities[MEGA], "basics=", basics,
            ", ".join(f"{key}={float(v) * 100:.9f}%"
                      for key, v in result.items()),
        )
    assert outputs["published"]["held_mega_by_first_draw_given_valid"] < (
        outputs["third_mega_cut_temple"]["held_mega_by_first_draw_given_valid"]
    )
    assert outputs["third_mega_cut_temple"]["valid_opening"] > (
        outputs["published"]["valid_opening"]
    )
    assert outputs["third_mega_cut_crobat"]["valid_opening"] == (
        outputs["published"]["valid_opening"]
    )
    print("PASS: labeled toy enumeration, three snapshot-legal 60-card decks")
    print("LIMIT: no search, Energy, damage, matchup or win-rate simulation")


if __name__ == "__main__":
    verify()
