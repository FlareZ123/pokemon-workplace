"""Reproduce Hand Control's forced out-of-turn Supporter transaction."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from build_expanded_legality_baseline import classify_effective_legality
from forced_supporter_execution import (
    ForcedSupporterState,
    SupporterInstance,
    begin_hand_control,
    finish_hand_control,
    forced_supporter_play_rows,
)
from turn_action_budget import TurnActionBudget

def load_set(set_id: str) -> list[dict]:
    return json.loads(
        (ROOT / "resources" / "cards" / "en" / f"{set_id}.json").read_text(
            encoding="utf-8"
        )
    )

def main() -> None:
    rows = forced_supporter_play_rows(ROOT / "resources")
    assert len(rows) == 1
    assert rows[0]["id"] == "xy3-36"
    assert rows[0]["name"] == "Hypno"
    assert rows[0]["attack_name"] == "Hand Control"
    assert "your opponent plays that Supporter card" in rows[0]["text"]

    hypno = next(card for card in load_set("xy3") if card["id"] == "xy3-36")
    status, _ = classify_effective_legality(hypno)
    assert status == "Legal"

    venomoth = next(card for card in load_set("xy4") if card["id"] == "xy4-2")
    dizzying_wind = next(
        attack for attack in venomoth["attacks"] if attack["name"] == "Dizzying Wind"
    )
    assert "during his or her next turn" in dizzying_wind["text"]

    weezing = next(card for card in load_set("sm12") if card["id"] == "sm12-77")
    blow_away = next(
        ability
        for ability in weezing["abilities"]
        if ability["name"] == "Blow-Away Bomb"
    )
    assert blow_away["text"].startswith("Once during your turn")

    supporter = SupporterInstance("supporter-1", "Example Supporter")
    initial = ForcedSupporterState(
        current_player="hypno_player",
        other_player="opponent",
        current_budget=TurnActionBudget(),
        other_budget=TurnActionBudget(),
        other_hand=(supporter,),
    )

    pending = begin_hand_control(initial, supporter.copy_id)
    assert pending is not None
    assert pending.other_hand == ()
    assert pending.resolving_supporter == supporter
    assert pending.event is not None
    assert pending.event.turn_owner == "hypno_player"
    assert pending.event.card_player == "opponent"
    assert pending.event.decision_controller == "hypno_player"
    assert pending.out_of_turn_supporter_plays == 1
    assert pending.other_budget == initial.other_budget
    assert not pending.current_budget.turn_ended

    finished = finish_hand_control(pending)
    assert finished is not None
    assert finished.resolving_supporter is None
    assert finished.other_discard == (supporter,)
    assert finished.other_budget == initial.other_budget
    assert finished.current_budget.turn_ended

    for destination in ("hand", "prize"):
        state = ForcedSupporterState(
            current_player="hypno_player",
            other_player="opponent",
            current_budget=TurnActionBudget(),
            other_budget=TurnActionBudget(),
            other_hand=(supporter,),
        )
        nested = begin_hand_control(state, supporter.copy_id)
        assert nested is not None
        result = finish_hand_control(nested, final_destination=destination)
        assert result is not None
        if destination == "hand":
            assert result.other_hand_return == (supporter,)
        else:
            assert result.other_prize == (supporter,)
        assert result.other_discard == ()

    assert begin_hand_control(pending, supporter.copy_id) is None

    print("forced_supporter_execution regression: PASS")
    print("forced-play corpus rows:", len(rows))

if __name__ == "__main__":
    main()
