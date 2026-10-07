"""Reproduce staged acquisition plus execution objective planning."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from acquired_trainer_execution_capacity import (
    ExecutionTurnWindow,
    TrainerExecutionRequirement,
)
from staged_trainer_objectives import (
    TrainerAcquisitionAction,
    TrainerAcquisitionRequirement,
    evaluate_staged_trainer_objectives,
)


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


def main() -> None:
    green_card = _card_by_id("sm10-175")
    computer_card = _card_by_id("bw7-137")
    secret_card = _card_by_id("sv6-163")
    boss_card = _card_by_id("swsh2-154")
    quick_ball = _card_by_id("swsh1-179")

    assert "Supporter" in green_card.get("subtypes", ())
    assert "Search your deck for up to 2 Trainer cards" in _text(green_card)
    assert set(("Item", "ACE SPEC")) <= set(computer_card.get("subtypes", ()))
    assert "Search your deck for a card" in _text(computer_card)
    assert "discard 3 other cards" in _text(secret_card)
    assert "a Supporter card" in _text(secret_card)
    assert "an Item card" in _text(secret_card)
    assert "Supporter" in boss_card.get("subtypes", ())
    assert "Item" in quick_ball.get("subtypes", ())

    green_boss = TrainerAcquisitionAction(
        "Green -> Boss",
        "Supporter",
        copies=1,
        hand_outputs=(("boss", 1),),
    )
    computer_boss = TrainerAcquisitionAction(
        "Computer -> Boss",
        "Item",
        copies=1,
        hand_outputs=(("boss", 1),),
        discard_cost=2,
    )
    current = ExecutionTurnWindow(turn=0, supporter_plays_remaining=1)

    acquire_only = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1},
        discardable_cards=2,
        acquisition_actions=(green_boss, computer_boss),
        acquisition_requirements=(
            TrainerAcquisitionRequirement("Boss acquired", "boss"),
        ),
        windows=(current,),
    )
    assert acquire_only.exact_joint_feasible
    assert acquire_only.acquisition_actions == ("Green -> Boss",)
    assert acquire_only.discard_spent == 0
    assert dict(acquire_only.searchable_after_acquisition)["boss"] == 0
    assert dict(acquire_only.hand_after_acquisition)["boss"] == 1

    execute_now = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1},
        discardable_cards=2,
        acquisition_actions=(green_boss, computer_boss),
        execution_requirements=(
            TrainerExecutionRequirement(
                "Boss executed now",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
        ),
        windows=(current,),
    )
    assert execute_now.exact_joint_feasible
    assert execute_now.acquisition_actions == ("Computer -> Boss",)
    assert execute_now.discard_spent == 2
    assert execute_now.execution_result.witness[0].turn == 0

    insufficient_discard = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1},
        discardable_cards=1,
        acquisition_actions=(green_boss, computer_boss),
        execution_requirements=(
            TrainerExecutionRequirement(
                "Boss executed now",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
        ),
        windows=(current,),
    )
    assert not insufficient_discard.exact_joint_feasible
    assert insufficient_discard.maximum_completed_units == 0

    dual_supporter = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1},
        discardable_cards=2,
        acquisition_actions=(green_boss, computer_boss),
        execution_requirements=(
            TrainerExecutionRequirement(
                "Boss executed now",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
        ),
        windows=(
            ExecutionTurnWindow(
                turn=0,
                supporter_plays_remaining=2,
            ),
        ),
    )
    assert dual_supporter.exact_joint_feasible
    assert dual_supporter.acquisition_actions == ("Green -> Boss",)
    assert dual_supporter.discard_spent == 0

    next_turn = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1},
        discardable_cards=2,
        acquisition_actions=(green_boss, computer_boss),
        execution_requirements=(
            TrainerExecutionRequirement(
                "Boss by next turn",
                "boss",
                "Supporter",
                deadline_turn=1,
            ),
        ),
        windows=(
            current,
            ExecutionTurnWindow(turn=1, supporter_plays_remaining=1),
        ),
    )
    assert next_turn.exact_joint_feasible
    assert next_turn.acquisition_actions == ("Green -> Boss",)
    assert next_turn.discard_spent == 0
    assert next_turn.execution_result.witness[0].turn == 1

    green_pair = TrainerAcquisitionAction(
        "Green -> Boss + Quick Ball",
        "Supporter",
        copies=1,
        hand_outputs=(("boss", 1), ("quick_ball", 1)),
    )
    secret_pair = TrainerAcquisitionAction(
        "Secret Box -> Boss + Quick Ball",
        "Item",
        copies=1,
        hand_outputs=(("boss", 1), ("quick_ball", 1)),
        discard_cost=3,
    )
    two_stage = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1, "quick_ball": 1},
        discardable_cards=3,
        acquisition_actions=(green_pair, secret_pair),
        acquisition_requirements=(
            TrainerAcquisitionRequirement(
                "Quick Ball acquired",
                "quick_ball",
            ),
        ),
        execution_requirements=(
            TrainerExecutionRequirement(
                "Boss executed now",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
        ),
        windows=(current,),
    )
    assert two_stage.exact_joint_feasible
    assert two_stage.maximum_completed_units == 2
    assert two_stage.acquisition_actions == (
        "Secret Box -> Boss + Quick Ball",
    )
    assert two_stage.discard_spent == 3

    two_stage_low_discard = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1, "quick_ball": 1},
        discardable_cards=2,
        acquisition_actions=(green_pair, secret_pair),
        acquisition_requirements=(
            TrainerAcquisitionRequirement(
                "Quick Ball acquired",
                "quick_ball",
            ),
        ),
        execution_requirements=(
            TrainerExecutionRequirement(
                "Boss executed now",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
        ),
        windows=(current,),
    )
    assert not two_stage_low_discard.exact_joint_feasible
    assert two_stage_low_discard.maximum_completed_units == 1
    assert two_stage_low_discard.acquisition_actions == (
        "Green -> Boss + Quick Ball",
    )

    print(
        json.dumps(
            {
                "acquisition_only_action": acquire_only.acquisition_actions,
                "same_turn_execution_action": execute_now.acquisition_actions,
                "same_turn_execution_discard_spent": execute_now.discard_spent,
                "same_turn_with_one_fodder_feasible": (
                    insufficient_discard.exact_joint_feasible
                ),
                "dual_supporter_action": dual_supporter.acquisition_actions,
                "next_turn_action": next_turn.acquisition_actions,
                "two_stage_action": two_stage.acquisition_actions,
                "two_stage_completed_units": (
                    two_stage.maximum_completed_units
                ),
                "two_stage_low_discard_completed_units": (
                    two_stage_low_discard.maximum_completed_units
                ),
                "searchable_target_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
