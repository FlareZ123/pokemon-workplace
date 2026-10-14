"""Closed-turn regression across physical search and acquired Trainer projections.

Run on the repository's pinned card database, without an opponent policy.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from acquired_trainer_action_window import evaluate_acquired_trainer_action_window
from acquired_trainer_execution_capacity import (
    ExecutionTurnWindow,
    TrainerExecutionRequirement,
    evaluate_trainer_execution_capacity,
    execution_window_from_state,
)
from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_retrieval_transaction,
)
from turn_action_budget import TurnAction, TurnActionBudget
from typed_search_retrieval import enumerate_typed_retrieval_actions
from typed_search_target_allocator import (
    ITEM,
    POKEMON_TOOL,
    STADIUM,
    SUPPORTER,
    TargetGroup,
)


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    secret_box = next(p for p in profiles if p.name == "Secret Box")
    assert secret_box.action_class == "Item"
    assert secret_box.required_discard_other_cards == 3

    targets = (
        SearchZoneTarget("target_item", TargetGroup("Item", 1, frozenset({ITEM}))),
        SearchZoneTarget(
            "target_tool",
            TargetGroup("Tool", 1, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            "target_supporter",
            TargetGroup("Supporter", 1, frozenset({SUPPORTER})),
        ),
        SearchZoneTarget(
            "target_stadium",
            TargetGroup("Stadium", 1, frozenset({STADIUM})),
        ),
    )
    retrievals = enumerate_typed_retrieval_actions(
        secret_box.base_outputs,
        tuple(target.group for target in targets),
    )
    full = next(
        action
        for action in retrievals
        if action.target_cost == (1, 1, 1, 1)
    )
    zones = ZoneCountState.from_mapping({
        ("secret_box", "hand"): 1,
        ("fodder_a", "hand"): 1,
        ("fodder_b", "hand"): 1,
        ("fodder_c", "hand"): 1,
        ("held_item", "hand"): 1,
        ("held_tool", "hand"): 1,
        **{(target.card_class, "deck"): 1 for target in targets},
    })
    candidates = tuple(DiscardCandidate(n) for n in (
        "fodder_a", "fodder_b", "fodder_c"
    ))
    choices = enumerate_discard_selections(zones, candidates, 3)
    assert len(choices) == 1

    def play(state: TrainerSearchExecutionState):
        return execute_trainer_retrieval_transaction(
            state,
            profile=secret_box,
            action_card_class="secret_box",
            targets=targets,
            retrieval_action=full,
            discard_candidates=candidates,
            discard_selection=choices[0],
        )

    open_state = TrainerSearchExecutionState(zones=zones)
    successful = play(open_state)
    assert successful.after.zones.count("secret_box", "discard") == 1
    assert successful.after.zones.count("target_item", "hand") == 1
    assert successful.after.budget.remaining(TurnAction.SUPPORTER) == 1

    checked = []
    for action in (TurnAction.ATTACK, TurnAction.END_TURN):
        ended_budget = TurnActionBudget().consume(action)
        assert ended_budget is not None and ended_budget.turn_ended
        closed_state = TrainerSearchExecutionState(
            zones=zones,
            budget=ended_budget,
        )

        try:
            play(closed_state)
        except ValueError as exc:
            assert "turn has ended" in str(exc), str(exc)
        else:
            raise AssertionError(f"Secret Box played after {action.value}")

        for card_class, action_class in (
            ("held_item", "Item"),
            ("held_tool", "Pokémon Tool"),
        ):
            acquired = evaluate_acquired_trainer_action_window(
                closed_state,
                card_class=card_class,
                action_class=action_class,
            )
            assert acquired.copies_in_hand == 1
            assert acquired.channel_open
            assert not acquired.window_available

        closed_window = execution_window_from_state(0, closed_state)
        assert not closed_window.channels.item_play
        assert not closed_window.channels.tool_play
        assert not closed_window.channels.supporter_play
        assert not closed_window.channels.stadium_play
        assert closed_window.channels.pokemon_play

        requirements = (
            TrainerExecutionRequirement(
                "item now",
                "held_item",
                "Item",
                deadline_turn=0,
            ),
            TrainerExecutionRequirement(
                "tool now",
                "held_tool",
                "Pokémon Tool",
                deadline_turn=0,
            ),
        )
        blocked = evaluate_trainer_execution_capacity(
            {"held_item": 1, "held_tool": 1},
            requirements,
            (closed_window,),
        )
        assert blocked.maximum_executed_units == 0
        assert not blocked.exact_joint_feasible

        next_turn = evaluate_trainer_execution_capacity(
            {"held_item": 1, "held_tool": 1},
            (
                TrainerExecutionRequirement(
                    "item next turn",
                    "held_item",
                    "Item",
                    earliest_turn=1,
                    deadline_turn=1,
                ),
                TrainerExecutionRequirement(
                    "tool next turn",
                    "held_tool",
                    "Pokémon Tool",
                    earliest_turn=1,
                    deadline_turn=1,
                ),
            ),
            (closed_window, ExecutionTurnWindow(turn=1)),
        )
        assert next_turn.exact_joint_feasible
        assert next_turn.maximum_executed_units == 2
        checked.append(action.value)

    print(json.dumps({
        "printed_card": secret_box.card_id,
        "open_turn_secret_box_executable": True,
        "closed_by": checked,
        "closed_turn_retrieval_rejected": True,
        "closed_turn_item_and_tool_window": False,
        "fresh_next_turn_item_and_tool_window": True,
        "scope": "generic Trainer play window, not match win rate",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
