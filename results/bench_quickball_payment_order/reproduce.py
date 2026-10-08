"""Independent exact labeled-world oracle for Quick Ball/support sequencing."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_quickball_access import analyze_quickball_access
from bench_quickball_sequence import (
    UNAVAILABLE, HAND, DECK, optimal_sequence_probability,
    payment_first_probability,
)
from bench_double_trigger_access import analyze as idealized_pair


def independent_labeled_oracle() -> None:
    # A/B singleton supports; O ordinary starter; H/H Quick Balls;
    # R/R coin pickups; D wrong-zone Bench search; X discardable; F filler.
    cards = "ABOHHRRDXF"
    count = 0
    adaptive_mass = Fraction(0)
    payment_first_mass = Fraction(0)
    for opener in combinations(range(len(cards)), 4):
        if not any(cards[i] in "ABO" for i in opener):
            continue
        active = (next(i for i in opener if cards[i] == "O")
                  if 2 in opener else
                  next(i for i in opener if cards[i] in "AB"))
        rest = [i for i in range(len(cards)) if i not in opener]
        for prizes in combinations(rest, 2):
            deck_after_prizes = [i for i in rest if i not in prizes]
            for drawn in combinations(deck_after_prizes, 1):
                hand = set(opener) | set(drawn)
                real_hand = hand - {active}
                live_deck = set(deck_after_prizes) - set(drawn)

                def target_zone(name: str) -> int:
                    if any(cards[i] == name for i in real_hand):
                        return HAND
                    if any(cards[i] == name for i in live_deck):
                        return DECK
                    return UNAVAILABLE

                args = dict(
                    a=target_zone("A"), b=target_zone("B"),
                    quick_balls=sum(cards[i] == "H" for i in hand),
                    discard_fuel=sum(cards[i] in "DX" for i in hand),
                    sure_pickups=0,
                    coin_pickups=sum(cards[i] == "R" for i in hand),
                    free_slots=1,
                )
                count += 1
                adaptive_mass += optimal_sequence_probability(**args)
                payment_first_mass += payment_first_probability(**args)

    result = analyze_quickball_access(
        deck_size=10, opening_size=4, prize_count=2,
        later_random_draws=1, other_basics=1, quick_balls=2,
        direct_bench_items=1, expendable_cards=1,
        coin_pickups=2, free_slots=1,
    )
    assert result.adaptive == adaptive_mass / count
    assert result.payment_first == payment_first_mass / count
    assert count == 10500
    assert result.payment_first == Fraction(37, 750)
    assert result.adaptive == Fraction(167, 2625)
    print("Independent labeled worlds:", count)
    print("Exact payment-first:", result.payment_first)
    print("Exact adaptive:", result.adaptive)


def sequencing_witnesses() -> None:
    scenarios = (
        (dict(a=HAND, b=DECK, quick_balls=1, discard_fuel=0,
              sure_pickups=1, coin_pickups=0), Fraction(1), Fraction(0)),
        (dict(a=HAND, b=DECK, quick_balls=1, discard_fuel=0,
              sure_pickups=0, coin_pickups=1), Fraction(1, 2), Fraction(0)),
        (dict(a=HAND, b=DECK, quick_balls=1, discard_fuel=0,
              sure_pickups=0, coin_pickups=2), Fraction(3, 4), Fraction(1, 2)),
        (dict(a=DECK, b=DECK, quick_balls=2, discard_fuel=0,
              sure_pickups=0, coin_pickups=2), Fraction(1, 2), Fraction(0)),
        (dict(a=DECK, b=DECK, quick_balls=2, discard_fuel=0,
              sure_pickups=1, coin_pickups=1), Fraction(1), Fraction(0)),
        (dict(a=HAND, b=HAND, quick_balls=0, discard_fuel=0,
              sure_pickups=0, coin_pickups=1), Fraction(1, 2), Fraction(1, 2)),
    )
    for args, expected_adaptive, expected_payment in scenarios:
        adaptive = optimal_sequence_probability(**args)
        payment = payment_first_probability(**args)
        assert adaptive == expected_adaptive, (args, adaptive)
        assert payment == expected_payment, (args, payment)
    print("Six hand/coin sequencing witnesses passed")


def sensitivity() -> None:
    for direct, expendable in ((0, 0), (0, 2), (2, 0), (4, 0), (4, 2)):
        access = analyze_quickball_access(
            direct_bench_items=direct, expendable_cards=expendable,
        )
        ideal = idealized_pair(
            draws=4, direct_connectors=direct, coin_pickups=4,
        ).stochastic_exact
        assert Fraction(0) <= access.payment_first <= access.adaptive <= ideal
        print("D/X:", direct, expendable,
              "payment first:", f"{100*float(access.payment_first):.6f}%",
              "adaptive:", f"{100*float(access.adaptive):.6f}%",
              "ideal:", f"{100*float(ideal):.6f}%")
    assert (analyze_quickball_access(direct_bench_items=2).adaptive
            == analyze_quickball_access(expendable_cards=2).adaptive)
    assert (analyze_quickball_access(direct_bench_items=2).payment_first
            == analyze_quickball_access(expendable_cards=2).payment_first)
    print("PASS: exact oracle, payment symmetry, upper bound")


if __name__ == "__main__":
    independent_labeled_oracle()
    sequencing_witnesses()
    sensitivity()
