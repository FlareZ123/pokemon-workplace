"""Reproduce exact Special Condition recovery probabilities."""

from __future__ import annotations

from fractions import Fraction
import json
from math import isinf
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from condition_coin_models import (  # noqa: E402
    asleep_recovery_probability,
    burn_recovery_probability,
    expected_checks_to_coin_recovery,
)


def load_card(path: str, card_id: str) -> dict[str, object]:
    cards = json.loads((ROOT / path).read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def ability_text(card: dict[str, object], ability_name: str) -> str:
    abilities = card.get("abilities", [])
    assert isinstance(abilities, list)
    return next(
        ability["text"]
        for ability in abilities
        if ability.get("name") == ability_name
    )


def main() -> None:
    slaking = load_card("resources/cards/en/sv2.json", "sv2-162")
    centiskorch = load_card("resources/cards/en/swsh5.json", "swsh5-30")
    forest = load_card("resources/cards/en/sm11.json", "sm11-207")
    volcano = load_card("resources/cards/en/sm75.json", "sm75-63")

    assert slaking["legalities"]["expanded"] == "Legal"
    assert centiskorch["legalities"]["expanded"] == "Legal"
    assert forest["legalities"]["expanded"] == "Legal"
    assert volcano["legalities"]["expanded"] == "Legal"

    assert ability_text(slaking, "Stir and Snooze") == (
        "If this Pokémon is Asleep, flip 2 coins instead of 1 during Pokémon "
        "Checkup. If either of them is tails, this Pokémon is still Asleep."
    )
    assert ability_text(centiskorch, "Overheater") == (
        "Whenever your opponent flips a coin for their Burned Pokémon during "
        "Pokémon Checkup, it doesn't recover from that Special Condition even "
        "if the result is heads."
    )
    assert forest["rules"][0] == (
        "If a Pokémon is Asleep, its owner flips 2 coins instead of 1 for that "
        "Special Condition between turns. If either of them is tails, that "
        "Pokémon is still Asleep."
    )
    assert volcano["rules"][0] == (
        "Whenever a player flips a coin for the Special Condition Burned "
        "between turns, that Special Condition isn't removed even if the result "
        "is heads."
    )

    default_sleep = asleep_recovery_probability()
    two_coin_sleep = asleep_recovery_probability(coin_count=2)
    default_burn = burn_recovery_probability()
    locked_burn = burn_recovery_probability(recovery_suppressed=True)

    assert default_sleep == Fraction(1, 2)
    assert two_coin_sleep == Fraction(1, 4)
    assert default_burn == Fraction(1, 2)
    assert locked_burn == 0

    assert expected_checks_to_coin_recovery(default_sleep) == 2
    assert expected_checks_to_coin_recovery(two_coin_sleep) == 4
    assert expected_checks_to_coin_recovery(default_burn) == 2
    assert isinf(expected_checks_to_coin_recovery(locked_burn))

    print("default Sleep recovery:", default_sleep)
    print("two-coin all-heads Sleep recovery:", two_coin_sleep)
    print("default Burn recovery:", default_burn)
    print("suppressed Burn coin recovery:", locked_burn)
    print("expected Sleep checks, default/two-coin:", 2, 4)
    print("condition recovery probability regressions passed")


if __name__ == "__main__":
    main()
