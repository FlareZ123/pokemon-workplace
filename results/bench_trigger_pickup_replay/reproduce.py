"""Independent labeled worlds for Nest Ball pickup replay and Active rescue."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_trigger_pickup_replay import analyze_replay
from bench_active_trigger_rescue import analyze_rescue


def labeled_worlds() -> None:
    cards = "AOOHDRRFFF"
    valid = 0
    baseline_mass = Fraction(0)
    active_mass = Fraction(0)
    bench_mass = Fraction(0)
    for opener in combinations(range(len(cards)), 3):
        original = [cards[i] for i in opener]
        if not any(x in "AO" for x in original):
            continue
        forced = "A" in original and "O" not in original
        deck_before_prizes = set(range(len(cards))) - set(opener)
        for prizes in combinations(deck_before_prizes, 2):
            deck_after_prizes = deck_before_prizes - set(prizes)
            for drawn in deck_after_prizes:
                seen = set(opener) | {drawn}
                hand_cards = [cards[i] for i in seen]
                remaining = deck_after_prizes - {drawn}
                a_deck = any(cards[i] == "A" for i in remaining)
                o_deck = any(cards[i] == "O" for i in remaining)
                n_other = hand_cards.count("O")
                n_hand = hand_cards.count("H")
                n_direct = hand_cards.count("D")
                n_coins = hand_cards.count("R")
                p_pickup = Fraction((1 << n_coins) - 1, 1 << n_coins)

                ordinary = (("A" in hand_cards and not forced)
                            or (a_deck and n_hand > 0))
                active = (
                    forced and
                    (n_other > 0 or (o_deck and n_hand+n_direct > 0))
                    and n_coins > 0
                )
                bench = a_deck and n_hand == 0 and n_direct > 0 and n_coins > 0
                valid += 1
                baseline_mass += int(ordinary)
                active_mass += p_pickup if active and not ordinary else 0
                bench_mass += p_pickup if bench and not ordinary else 0

    actual = analyze_replay(
        deck_size=10, opening_size=3, prize_count=2, draws=1,
        other_basics=2, hand_search=1, direct_bench=1, coin_pickups=2,
    )
    assert valid == 8925
    assert actual.no_pickup == baseline_mass / valid
    assert actual.active_recovery == active_mass / valid
    assert actual.bench_replay == bench_mass / valid
    assert actual.no_pickup == Fraction(46, 119)
    assert actual.active_recovery == Fraction(353, 5950)
    assert actual.bench_replay == Fraction(53, 1785)
    assert actual.combined == Fraction(8489, 17850)
    print("Independent labeled worlds:", valid)
    print("No pickup:", actual.no_pickup)
    print("Active rescue:", actual.active_recovery)
    print("Bench-origin pickup replay:", actual.bench_replay)
    print("Combined:", actual.combined)


def sensitivity() -> None:
    for other in (1, 3, 5):
        for direct in (0, 2, 4):
            result = analyze_replay(other_basics=other, direct_bench=direct)
            prior = analyze_rescue(
                other_basics=other, direct_bench_items=direct,
            )
            assert result.no_pickup == prior.no_active_recovery
            assert (result.no_pickup + result.active_recovery
                    == prior.with_active_recovery)
            if direct == 0:
                assert result.bench_replay == 0
            assert result.combined >= prior.with_active_recovery
            print("O", other, "direct", direct,
                  "base:", f"{100*float(result.no_pickup):.6f}%",
                  "Active gain:", f"{100*float(result.active_recovery):.6f}pp",
                  "Bench replay gain:", f"{100*float(result.bench_replay):.6f}pp",
                  "combined:", f"{100*float(result.combined):.6f}%")
    impossible = analyze_replay(coin_pickups=0)
    assert impossible.active_recovery == impossible.bench_replay == 0
    assert analyze_replay(direct_bench=4).bench_replay > 0
    print("PASS: independent oracle, prior Active recovery, pickup gates")


if __name__ == "__main__":
    labeled_worlds()
    sensitivity()
