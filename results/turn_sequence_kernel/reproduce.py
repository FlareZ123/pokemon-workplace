"""Reproduce ordinary and extra-turn action-budget boundaries."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_expanded_legality_baseline import classify_effective_legality
from turn_action_budget import TurnAction, TurnActionBudget
from turn_sequence_kernel import (
    TurnSequenceState,
    advance_turn,
    close_turn_voluntarily,
    close_turn_with_attack,
)


def find_card(card_id: str) -> dict:
    set_id = card_id.split("-", 1)[0]
    cards = json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )
    return next(card for card in cards if card["id"] == card_id)


def main() -> None:
    dialga = find_card("sm5-100")
    status, _ = classify_effective_legality(dialga)
    assert status == "Legal"
    timeless = next(
        attack for attack in dialga["attacks"] if attack["name"] == "Timeless-GX"
    )
    assert "Take another turn after this one." in timeless["text"]
    assert "Skip the between-turns step." in timeless["text"]

    star_dialga = find_card("swsh10-114")
    status, _ = classify_effective_legality(star_dialga)
    assert status == "Legal"
    star_chronos = next(
        attack
        for attack in star_dialga["attacks"]
        if attack["name"] == "Star Chronos"
    )
    assert "Take another turn after this one." in star_chronos["text"]
    assert "Skip Pokémon Checkup." in star_chronos["text"]

    base = TurnSequenceState("A", "B")

    # Ordinary end passes control and performs Pokémon Checkup.
    voluntary = close_turn_voluntarily(base)
    assert voluntary is not None and voluntary.budget.turn_ended
    normal_next = advance_turn(voluntary)
    assert normal_next is not None
    assert normal_next.state.current_player == "B"
    assert normal_next.pokemon_checkup_occurs
    assert not normal_next.same_player_continues
    assert normal_next.state.budget == TurnActionBudget()

    # Spend several current-turn resources before the extra-turn attack.
    budget = base.budget
    for action in (
        TurnAction.SUPPORTER,
        TurnAction.STADIUM_PLAY,
        TurnAction.MANUAL_ENERGY_ATTACHMENT,
        TurnAction.RETREAT,
    ):
        budget = budget.consume(action)
        assert budget is not None

    before_timeless = TurnSequenceState("A", "B", budget=budget)
    timeless_end = close_turn_with_attack(
        before_timeless,
        take_another_turn=True,
        skip_pokemon_checkup=True,
    )
    assert timeless_end is not None
    assert timeless_end.budget.turn_ended

    extra = advance_turn(timeless_end)
    assert extra is not None
    assert extra.state.current_player == "A"
    assert extra.state.other_player == "B"
    assert extra.same_player_continues
    assert not extra.pokemon_checkup_occurs

    # The scheduled turn is a new turn, so ordinary turn bandwidth resets.
    for action in (
        TurnAction.SUPPORTER,
        TurnAction.STADIUM_PLAY,
        TurnAction.MANUAL_ENERGY_ATTACHMENT,
        TurnAction.RETREAT,
        TurnAction.ATTACK,
    ):
        assert extra.state.budget.can(action)

    # The following ordinary attack ends that new turn and passes control.
    second_attack_end = close_turn_with_attack(extra.state)
    assert second_attack_end is not None
    after_extra = advance_turn(second_attack_end)
    assert after_extra is not None
    assert after_extra.state.current_player == "B"
    assert after_extra.pokemon_checkup_occurs
    assert not after_extra.same_player_continues

    print("turn_sequence_kernel regression: PASS")


if __name__ == "__main__":
    main()
