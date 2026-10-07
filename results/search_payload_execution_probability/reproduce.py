"""Reproduce exact acquisition-versus-execution probability ranking."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
import json
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from singleton_payload_execution_probability import analyze_singleton_payload


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


def _brute_small(preserves_window: bool) -> tuple[Fraction, Fraction]:
    cards = (
        ("starter-1", "starter"),
        ("starter-2", "starter"),
        ("target", "target"),
        ("connector-1", "connector"),
        ("connector-2", "connector"),
        ("fodder-1", "fodder"),
        ("fodder-2", "fodder"),
        ("filler-1", "filler"),
        ("filler-2", "filler"),
        ("filler-3", "filler"),
    )
    valid = 0
    acquired = 0
    executed = 0

    for hand_indexes in combinations(range(len(cards)), 3):
        hand = {cards[index][0] for index in hand_indexes}
        hand_types = [cards[index][1] for index in hand_indexes]
        if "starter" not in hand_types:
            continue

        remaining = [
            index
            for index in range(len(cards))
            if index not in hand_indexes
        ]
        for prize_indexes in combinations(remaining, 2):
            prizes = {cards[index][0] for index in prize_indexes}
            valid += 1

            direct = "target" in hand
            connector_usable = (
                hand_types.count("connector") >= 1
                and hand_types.count("fodder") >= 1
            )
            route = (
                not direct
                and connector_usable
                and "target" not in prizes
            )
            acquired += int(direct or route)
            executed += int(
                direct or (route and preserves_window)
            )

    return Fraction(acquired, valid), Fraction(executed, valid)


def _assert_close(actual: Fraction, expected: float) -> None:
    if not isclose(float(actual), expected, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"{float(actual)} != {expected}")


def main() -> None:
    green = _card_by_id("sm10-175")
    computer = _card_by_id("bw7-137")
    secret = _card_by_id("sv6-163")
    boss = _card_by_id("swsh2-154")

    assert "Supporter" in green.get("subtypes", ())
    assert "no Pokémon with Abilities in play" in _text(green)
    assert "Search your deck for up to 2 Trainer cards" in _text(green)

    assert set(("Item", "ACE SPEC")) <= set(computer.get("subtypes", ()))
    assert "Discard 2 cards from your hand" in _text(computer)
    assert "Search your deck for a card" in _text(computer)

    assert set(("Item", "ACE SPEC")) <= set(secret.get("subtypes", ()))
    assert "discard 3 other cards from your hand" in _text(secret)
    assert "a Supporter card" in _text(secret)

    assert "Supporter" in boss.get("subtypes", ())

    manual = (
        ROOT
        / "resources"
        / "manual"
        / "EN_advanced_manual-2025-transcription-structured.md"
    ).read_text(encoding="utf-8")
    assert "players can use any number of Item cards during their turn" in manual
    assert "players may only use one Supporter during their turn" in manual

    # Independent labeled small-deck enumeration validates both endpoint modes.
    for preserves in (False, True):
        exact = analyze_singleton_payload(
            deck_size=10,
            hand_size=3,
            prize_count=2,
            starter_copies=2,
            connector_copies=2,
            dedicated_fodder=2,
            connector_discard_cost=1,
            connector_preserves_payload_window=preserves,
        )
        brute_acquired, brute_executed = _brute_small(preserves)
        assert exact.acquisition_probability == brute_acquired
        assert exact.same_turn_execution_probability == brute_executed

    rows = []
    for fodder in (10, 20, 35):
        green_metrics = analyze_singleton_payload(
            starter_copies=12,
            connector_copies=4,
            dedicated_fodder=fodder,
            connector_discard_cost=0,
            connector_preserves_payload_window=False,
        )
        computer_metrics = analyze_singleton_payload(
            starter_copies=12,
            connector_copies=1,
            dedicated_fodder=fodder,
            connector_discard_cost=2,
            connector_preserves_payload_window=True,
        )
        secret_metrics = analyze_singleton_payload(
            starter_copies=12,
            connector_copies=1,
            dedicated_fodder=fodder,
            connector_discard_cost=3,
            connector_preserves_payload_window=True,
        )
        green_two_supporters = analyze_singleton_payload(
            starter_copies=12,
            connector_copies=4,
            dedicated_fodder=fodder,
            connector_discard_cost=0,
            connector_preserves_payload_window=True,
        )

        direct = green_metrics.direct_hand_probability
        assert computer_metrics.direct_hand_probability == direct
        assert secret_metrics.direct_hand_probability == direct

        assert green_metrics.acquisition_probability > computer_metrics.acquisition_probability
        assert computer_metrics.acquisition_probability > secret_metrics.acquisition_probability

        assert computer_metrics.same_turn_execution_probability > secret_metrics.same_turn_execution_probability
        assert secret_metrics.same_turn_execution_probability > green_metrics.same_turn_execution_probability

        assert green_metrics.same_turn_execution_probability == direct
        assert green_metrics.connector_execution_increment == 0
        assert (
            green_two_supporters.same_turn_execution_probability
            == green_two_supporters.acquisition_probability
        )

        rows.append(
            {
                "dedicated_fodder": fodder,
                "direct_percent": 100 * float(direct),
                "green_x4_acquisition_percent": 100 * float(
                    green_metrics.acquisition_probability
                ),
                "green_x4_same_turn_execution_percent": 100 * float(
                    green_metrics.same_turn_execution_probability
                ),
                "computer_x1_acquisition_percent": 100 * float(
                    computer_metrics.acquisition_probability
                ),
                "computer_x1_same_turn_execution_percent": 100 * float(
                    computer_metrics.same_turn_execution_probability
                ),
                "secret_box_x1_acquisition_percent": 100 * float(
                    secret_metrics.acquisition_probability
                ),
                "secret_box_x1_same_turn_execution_percent": 100 * float(
                    secret_metrics.same_turn_execution_probability
                ),
                "green_x4_two_supporter_execution_percent": 100 * float(
                    green_two_supporters.same_turn_execution_probability
                ),
            }
        )

    _assert_close(Fraction.from_float(rows[0]["direct_percent"] / 100), 0.10979633144060803)
    assert all(
        isclose(row["green_x4_acquisition_percent"], 41.49311132053168, abs_tol=1e-10)
        for row in rows
    )

    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
