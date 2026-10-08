"""Independent 8,925-world test for paid Active/Bench support replay."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_trigger_paid_replay import (
    ACTIVE, HAND, DECK, UNAVAILABLE,
    optimal_paid_replay, analyze_paid_replay,
)
from bench_trigger_pickup_replay import analyze_replay


def independently_enumerate_worlds() -> None:
    # A: singleton support; O/O: ordinary Basics; H/H: Quick Balls;
    # D: Nest Ball; R/R: coin pickups; X: discardable; F: filler.
    cards = "AOOHHDRRXF"
    valid = 0
    mass = Fraction(0)
    for opener in combinations(range(len(cards)), 3):
        original = [cards[i] for i in opener]
        if not any(name in "AO" for name in original):
            continue
        forced = "A" in original and "O" not in original
        after_opening = set(range(len(cards))) - set(opener)

        for prizes in combinations(after_opening, 2):
            after_prizes = after_opening - set(prizes)
            for drawn in after_prizes:
                visible = set(opener) | {drawn}
                shown = [cards[i] for i in visible]
                searchable_deck = after_prizes - {drawn}
                a_zone = (
                    ACTIVE if forced else
                    HAND if "A" in shown else
                    DECK if any(cards[i] == "A" for i in searchable_deck)
                    else UNAVAILABLE
                )
                other_hand = shown.count("O") - int(not forced)
                other_deck = sum(cards[i] == "O" for i in searchable_deck)
                score = optimal_paid_replay(
                    a_zone=a_zone,
                    other_in_hand=other_hand,
                    other_in_deck=other_deck,
                    quick_balls=shown.count("H"),
                    nest_balls=shown.count("D"),
                    discard_fuel=shown.count("X"),
                    sure_pickups=0,
                    coin_pickups=shown.count("R"),
                )
                mass += score
                valid += 1

    exact = analyze_paid_replay(
        deck_size=10, opening_size=3, prize_count=2, draws=1,
        other_basics=2, quick_balls=2, nest_balls=1,
        expendable=1, coin_pickups=2,
    )
    assert valid == 8925
    assert exact == mass / valid == Fraction(333, 595)
    print("Labeled accepted worlds:", valid, "exact paid replay:", exact)


def exact_action_witnesses() -> None:
    situations = (
        (dict(a_zone=HAND, other_in_hand=0, other_in_deck=0,
              quick_balls=0, nest_balls=0, discard_fuel=0,
              sure_pickups=0, coin_pickups=0), Fraction(1)),
        (dict(a_zone=DECK, other_in_hand=0, other_in_deck=0,
              quick_balls=1, nest_balls=0, discard_fuel=1,
              sure_pickups=0, coin_pickups=0), Fraction(1)),
        (dict(a_zone=DECK, other_in_hand=0, other_in_deck=0,
              quick_balls=0, nest_balls=1, discard_fuel=0,
              sure_pickups=0, coin_pickups=1), Fraction(1, 2)),
        (dict(a_zone=DECK, other_in_hand=0, other_in_deck=0,
              quick_balls=0, nest_balls=1, discard_fuel=0,
              sure_pickups=0, coin_pickups=2), Fraction(3, 4)),
        (dict(a_zone=DECK, other_in_hand=0, other_in_deck=0,
              quick_balls=1, nest_balls=1, discard_fuel=0,
              sure_pickups=0, coin_pickups=1), Fraction(1)),
        (dict(a_zone=ACTIVE, other_in_hand=1, other_in_deck=0,
              quick_balls=0, nest_balls=0, discard_fuel=0,
              sure_pickups=1, coin_pickups=0), Fraction(1)),
        (dict(a_zone=ACTIVE, other_in_hand=0, other_in_deck=1,
              quick_balls=0, nest_balls=1, discard_fuel=0,
              sure_pickups=0, coin_pickups=1), Fraction(1, 2)),
        (dict(a_zone=ACTIVE, other_in_hand=0, other_in_deck=1,
              quick_balls=1, nest_balls=0, discard_fuel=0,
              sure_pickups=1, coin_pickups=0), Fraction(0)),
        (dict(a_zone=ACTIVE, other_in_hand=0, other_in_deck=1,
              quick_balls=1, nest_balls=0, discard_fuel=1,
              sure_pickups=1, coin_pickups=0), Fraction(1)),
        (dict(a_zone=ACTIVE, other_in_hand=0, other_in_deck=1,
              quick_balls=1, nest_balls=0, discard_fuel=0,
              sure_pickups=0, coin_pickups=2), Fraction(1, 2)),
    )
    for state, expected in situations:
        assert optimal_paid_replay(**state) == expected, state
    print("Ten exact payment and pickup sequencing witnesses passed")


def sensitivity() -> None:
    for other in (1, 3, 5):
        for nests in (0, 2, 4):
            paid = analyze_paid_replay(
                other_basics=other, nest_balls=nests,
            )
            ideal = analyze_replay(
                other_basics=other, direct_bench=nests,
            ).combined
            assert Fraction(0) <= paid <= ideal <= 1
            print("Other Basics", other, "Nest Balls", nests,
                  "paid:", f"{100*float(paid):.6f}%",
                  "free-search ideal:", f"{100*float(ideal):.6f}%",
                  "gap:", f"{100*float(ideal-paid):.6f}pp")
    assert (analyze_paid_replay(other_basics=3, nest_balls=4)
            > analyze_paid_replay(other_basics=3, nest_balls=0))
    assert analyze_paid_replay(other_basics=0, quick_balls=0, nest_balls=0) == 0
    print("PASS: labeled oracle, exact action witnesses, bound sensitivity")


if __name__ == "__main__":
    independently_enumerate_worlds()
    exact_action_witnesses()
    sensitivity()
