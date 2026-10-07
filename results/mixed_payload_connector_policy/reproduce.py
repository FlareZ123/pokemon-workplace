"""Reproduce endpoint-sensitive policy for Green + Computer Search."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
import json
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from mixed_payload_connector_policy import analyze_mixed_payload_policy


def _card_by_id(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in cards if card["id"] == card_id)


def _text(card: dict) -> str:
    return " ".join(card.get("rules") or ())


def _brute_small():
    cards = (
        ("starter-1", "starter"),
        ("starter-2", "starter"),
        ("target", "target"),
        ("green-1", "supporter_connector"),
        ("green-2", "supporter_connector"),
        ("computer", "item_connector"),
        ("fodder-1", "fodder"),
        ("fodder-2", "fodder"),
        ("filler-1", "filler"),
        ("filler-2", "filler"),
    )
    valid = 0
    acquired = 0
    optimal = 0
    green_priority = 0
    overlap = 0

    for hand_indexes in combinations(range(len(cards)), 3):
        hand_names = {cards[index][0] for index in hand_indexes}
        hand_types = [cards[index][1] for index in hand_indexes]
        if "starter" not in hand_types:
            continue
        remaining = [
            index
            for index in range(len(cards))
            if index not in hand_indexes
        ]
        for prize_indexes in combinations(remaining, 2):
            prize_names = {cards[index][0] for index in prize_indexes}
            valid += 1
            direct = "target" in hand_names
            green_route = hand_types.count("supporter_connector") > 0
            item_route = (
                hand_types.count("item_connector") > 0
                and hand_types.count("fodder") >= 1
            )
            target_in_deck = not direct and "target" not in prize_names
            acquired_route = target_in_deck and (green_route or item_route)
            item_success = target_in_deck and item_route

            acquired += int(direct or acquired_route)
            optimal += int(direct or item_success)
            green_priority += int(
                direct or (
                    item_success and not green_route
                )
            )
            overlap += int(
                target_in_deck and green_route and item_route
            )

    return tuple(
        Fraction(value, valid)
        for value in (acquired, optimal, green_priority, overlap)
    )


def main() -> None:
    green = _card_by_id("sm10-175")
    computer = _card_by_id("bw7-137")
    boss = _card_by_id("swsh2-154")

    assert "Supporter" in green.get("subtypes", ())
    assert "Search your deck for up to 2 Trainer cards" in _text(green)
    assert set(("Item", "ACE SPEC")) <= set(computer.get("subtypes", ()))
    assert "Discard 2 cards from your hand" in _text(computer)
    assert "Supporter" in boss.get("subtypes", ())

    small = analyze_mixed_payload_policy(
        deck_size=10,
        hand_size=3,
        prize_count=2,
        starter_copies=2,
        supporter_connector_copies=2,
        item_connector_copies=1,
        dedicated_fodder=2,
        item_discard_cost=1,
    )
    brute = _brute_small()
    assert (
        small.acquisition_probability,
        small.optimal_same_turn_execution_probability,
        small.supporter_priority_same_turn_execution_probability,
        small.decision_overlap_probability,
    ) == brute

    rows = []
    for fodder in (10, 20, 35):
        metrics = analyze_mixed_payload_policy(
            starter_copies=12,
            supporter_connector_copies=4,
            item_connector_copies=1,
            dedicated_fodder=fodder,
            item_discard_cost=2,
        )
        assert (
            metrics.optimal_same_turn_execution_probability
            - metrics.supporter_priority_same_turn_execution_probability
            == metrics.decision_overlap_probability
        )
        assert (
            metrics.next_turn_execution_probability
            == metrics.acquisition_probability
        )
        rows.append(
            {
                "dedicated_fodder": fodder,
                "acquisition_percent": 100 * float(
                    metrics.acquisition_probability
                ),
                "optimal_same_turn_execution_percent": 100 * float(
                    metrics.optimal_same_turn_execution_probability
                ),
                "green_priority_same_turn_execution_percent": 100 * float(
                    metrics.supporter_priority_same_turn_execution_probability
                ),
                "next_turn_execution_percent": 100 * float(
                    metrics.next_turn_execution_probability
                ),
                "decision_overlap_percent": 100 * float(
                    metrics.decision_overlap_probability
                ),
            }
        )

    expected = (
        (43.07679742467179, 13.088027781452274, 12.563319248200925, 0.5247085332513499),
        (45.54230310084679, 16.612511312218952, 15.028824924375922, 1.5836863878430307),
        (47.209160117679545, 19.447174620169598, 16.69568194120868, 2.7514926789609175),
    )
    for row, values in zip(rows, expected, strict=True):
        actual = (
            row["acquisition_percent"],
            row["optimal_same_turn_execution_percent"],
            row["green_priority_same_turn_execution_percent"],
            row["decision_overlap_percent"],
        )
        assert all(
            isclose(a, b, rel_tol=0.0, abs_tol=1e-10)
            for a, b in zip(actual, values, strict=True)
        )

    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
