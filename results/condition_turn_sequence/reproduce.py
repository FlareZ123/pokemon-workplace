"""Reproduce Special Condition behavior across a skipped Pokémon Checkup."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from condition_turn_sequence import advance_with_conditions  # noqa: E402
from special_condition_state import ConditionKind, regular_condition  # noqa: E402
from timed_special_conditions import (  # noqa: E402
    TimedConditionState,
    apply_timed_condition,
)
from turn_sequence_kernel import (  # noqa: E402
    TurnSequenceState,
    close_turn_voluntarily,
    close_turn_with_attack,
)


def load_card(path: str, card_id: str) -> dict[str, object]:
    cards = json.loads((ROOT / path).read_text(encoding="utf-8"))
    return next(card for card in cards if card["id"] == card_id)


def attack_text(card: dict[str, object], attack_name: str) -> str:
    attacks = card.get("attacks", [])
    assert isinstance(attacks, list)
    return next(
        attack["text"]
        for attack in attacks
        if attack.get("name") == attack_name
    )


def main() -> None:
    dialga = load_card("resources/cards/en/swsh10.json", "swsh10-114")
    assert dialga["name"] == "Origin Forme Dialga VSTAR"
    assert attack_text(dialga, "Star Chronos") == (
        "Take another turn after this one. (Skip Pokémon Checkup.) "
        "(You can't use more than 1 VSTAR Power in a game.)"
    )

    conditions = apply_timed_condition(
        TimedConditionState("A"),
        regular_condition(ConditionKind.POISONED),
        applied_turn_serial=9,
    )
    sequence = TurnSequenceState("A", "B")

    ended = close_turn_with_attack(
        sequence,
        take_another_turn=True,
        skip_pokemon_checkup=True,
    )
    assert ended is not None

    first_boundary = advance_with_conditions(
        ended,
        conditions,
        current_turn_serial=10,
    )
    assert first_boundary is not None
    assert first_boundary.turn_advance.same_player_continues
    assert not first_boundary.turn_advance.pokemon_checkup_occurs
    assert first_boundary.checkup_outcome is None
    assert first_boundary.conditions.get(ConditionKind.POISONED) is not None

    extra_turn = first_boundary.turn_advance.state
    extra_turn_ended = close_turn_voluntarily(extra_turn)
    assert extra_turn_ended is not None

    second_boundary = advance_with_conditions(
        extra_turn_ended,
        first_boundary.conditions,
        current_turn_serial=11,
    )
    assert second_boundary is not None
    assert not second_boundary.turn_advance.same_player_continues
    assert second_boundary.turn_advance.pokemon_checkup_occurs
    assert second_boundary.checkup_outcome is not None
    assert second_boundary.checkup_outcome.damage_counter_events == (
        (ConditionKind.POISONED, 1),
    )
    assert second_boundary.conditions.get(ConditionKind.POISONED) is not None

    print("Star Chronos skipped the first Checkup")
    print("Poison counter events after skipped boundary: 0")
    print(
        "Poison counter events after extra turn:",
        second_boundary.checkup_outcome.total_damage_counters,
    )
    print("condition/turn-sequence regression passed")


if __name__ == "__main__":
    main()
