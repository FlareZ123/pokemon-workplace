"""Verify Arven T1 + Gladion T2 access against physical small decks."""

from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from grand_tree_arven_prefetch import (
    ArvenPrefetchOpening, min_turn_to_use_both_supporters
)
from turn_action_budget import TurnAction, TurnActionBudget


def oracle(m: ArvenPrefetchOpening) -> Fraction:
    labels = (
        ("B",)*m.basics
        + ("A",)*m.arven
        + ("G",)*m.gladion
        + ("T","S1","S2","Comm")
        + ("F",)*(m.total-m.basics-m.arven-m.gladion-4)
    )
    universe = tuple(range(m.total))
    assert len(labels) == m.total
    accepted = 0
    favorable_fraction = Fraction()
    for hand in itertools.combinations(universe,m.opening):
        hand_set = set(hand)
        if not any(labels[i] == "B" for i in hand):
            continue
        accepted += 1
        chosen = [labels[i] for i in hand]
        if (
            "A" not in chosen or "G" not in chosen or "T" not in chosen
            or "S1" in chosen or "S2" in chosen or "Comm" in chosen
        ):
            continue
        remaining = tuple(i for i in universe if i not in hand_set)
        prize_count = 0
        progress = Fraction()
        for prize in itertools.combinations(remaining,m.prizes):
            prize_count += 1
            pset = set(prize)
            if (
                sum(labels[i] == "S1" for i in prize) != 1
                or any(labels[i] in ("S2","Comm") for i in prize)
            ):
                continue
            deck = tuple(i for i in remaining if i not in pset)
            first_success = Fraction()
            for first in deck:
                if labels[first] in ("S2","Comm"):
                    continue
                # Arven fetches Comm from the remaining deck at T1.
                deck_after_arven = tuple(
                    i for i in deck
                    if i != first and labels[i] != "Comm"
                )
                assert len(deck_after_arven) == len(deck)-2
                second_success = sum(
                    labels[second] != "S2" for second in deck_after_arven
                )
                first_success += Fraction(second_success,len(deck_after_arven))
            progress += first_success / len(deck)
        favorable_fraction += progress / prize_count
    return favorable_fraction / accepted


def verify_card_text() -> None:
    cards = json.loads((ROOT/"resources"/"cards"/"en"/"sv1.json").read_text())
    arven = next(c for c in cards if c["id"] == "sv1-166")
    assert arven["legalities"]["expanded"] == "Legal"
    assert "Supporter" in arven["subtypes"]
    assert "Search your deck for an Item card and a Pokémon Tool card" in arven["rules"][0]
    comms = json.loads((ROOT/"resources"/"cards"/"en"/"sm9.json").read_text())
    item = next(c for c in comms if c["id"] == "sm9-152")
    assert "Item" in item["subtypes"]
    assert item["legalities"]["expanded"] == "Legal"
    assert item["name"] == "Pokémon Communication"


def main() -> None:
    verify_card_text()
    for m in (
        ArvenPrefetchOpening(10,2,1,1,4,2),
        ArvenPrefetchOpening(10,2,1,1,4,3),
        ArvenPrefetchOpening(11,2,2,1,5,2),
        ArvenPrefetchOpening(11,2,2,1,5,3),
        ArvenPrefetchOpening(11,3,1,2,5,2),
        ArvenPrefetchOpening(11,3,1,2,5,3),
        ArvenPrefetchOpening(11,2,2,2,5,2),
        ArvenPrefetchOpening(11,2,2,2,5,3),
    ):
        exact = m.certificate_probability_going_second()
        independent = oracle(m)
        assert exact == independent, (m,exact,independent)

    assert min_turn_to_use_both_supporters(going_first=True) == 3
    assert min_turn_to_use_both_supporters(going_first=False) == 2
    budget = TurnActionBudget()
    after_arven = budget.consume(TurnAction.SUPPORTER)
    assert after_arven is not None
    assert after_arven.consume(TurnAction.SUPPORTER) is None
    after_gladion = after_arven.next_turn().consume(TurnAction.SUPPORTER)
    assert after_gladion is not None

    for num in range(1,5):
        m = ArvenPrefetchOpening(arven=num,gladion=num)
        print("Arven",num,"Gladion",num,
              "P T2 prefetched line|Basic",float(
                  m.certificate_probability_going_second()
              )*100,"%")
    print("grand_tree_arven_prefetch: PASS")


if __name__ == "__main__":
    main()
