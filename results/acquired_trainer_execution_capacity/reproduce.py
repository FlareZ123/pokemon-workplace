"""Reproduce joint execution capacity for already acquired Trainer payloads."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from acquired_trainer_execution_capacity import (
    ExecutionTurnWindow,
    TrainerExecutionRequirement,
    evaluate_trainer_execution_capacity,
    execution_window_from_state,
)
from discard_cost_witness import (
    DiscardCandidate,
    enumerate_discard_selections,
)
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_search_transaction,
)
from turn_action_budget import TurnActionBudget
from typed_search_target_allocator import (
    SUPPORTER,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def main() -> None:
    current = ExecutionTurnWindow(turn=0, supporter_plays_remaining=1)
    next_turn = ExecutionTurnWindow(turn=1, supporter_plays_remaining=1)

    two_supporters = (
        TrainerExecutionRequirement(
            "gust now",
            "boss",
            "Supporter",
            deadline_turn=0,
        ),
        TrainerExecutionRequirement(
            "draw now",
            "research",
            "Supporter",
            deadline_turn=0,
        ),
    )
    ordinary_collision = evaluate_trainer_execution_capacity(
        {"boss": 1, "research": 1},
        two_supporters,
        (current,),
    )
    assert ordinary_collision.individually_feasible == (True, True)
    assert not ordinary_collision.exact_joint_feasible
    assert ordinary_collision.maximum_executed_units == 1
    assert ordinary_collision.minimum_unexecuted_units == 1

    dual_current = ExecutionTurnWindow(
        turn=0,
        supporter_plays_remaining=2,
    )
    dual_success = evaluate_trainer_execution_capacity(
        {"boss": 1, "research": 1},
        two_supporters,
        (dual_current,),
    )
    assert dual_success.exact_joint_feasible
    assert {step.turn for step in dual_success.witness} == {0}

    split_deadlines = (
        TrainerExecutionRequirement(
            "gust now",
            "boss",
            "Supporter",
            deadline_turn=0,
        ),
        TrainerExecutionRequirement(
            "draw next",
            "research",
            "Supporter",
            earliest_turn=1,
            deadline_turn=1,
        ),
    )
    split_success = evaluate_trainer_execution_capacity(
        {"boss": 1, "research": 1},
        split_deadlines,
        (current, next_turn),
    )
    assert split_success.exact_joint_feasible
    assert tuple(step.turn for step in split_success.witness) == (0, 1)

    both_next = (
        TrainerExecutionRequirement(
            "gust next",
            "boss",
            "Supporter",
            earliest_turn=1,
            deadline_turn=1,
        ),
        TrainerExecutionRequirement(
            "draw next",
            "research",
            "Supporter",
            earliest_turn=1,
            deadline_turn=1,
        ),
    )
    next_collision = evaluate_trainer_execution_capacity(
        {"boss": 1, "research": 1},
        both_next,
        (current, next_turn),
    )
    assert next_collision.individually_feasible == (True, True)
    assert not next_collision.exact_joint_feasible

    physical_reuse = evaluate_trainer_execution_capacity(
        {"boss": 1},
        (
            TrainerExecutionRequirement(
                "gust target A",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
            TrainerExecutionRequirement(
                "gust target B",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
        ),
        (dual_current,),
    )
    assert physical_reuse.individually_feasible == (True, True)
    assert not physical_reuse.exact_joint_feasible
    assert physical_reuse.minimum_unexecuted_units == 1

    mixed_classes = evaluate_trainer_execution_capacity(
        {"boss": 1, "quick_ball": 1},
        (
            TrainerExecutionRequirement(
                "gust",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
            TrainerExecutionRequirement(
                "search basic",
                "quick_ball",
                "Item",
                deadline_turn=0,
            ),
        ),
        (current,),
    )
    assert mixed_classes.exact_joint_feasible

    locked_now_open_next = evaluate_trainer_execution_capacity(
        {"boss": 1},
        (
            TrainerExecutionRequirement(
                "gust by next",
                "boss",
                "Supporter",
                deadline_turn=1,
            ),
        ),
        (
            ExecutionTurnWindow(
                turn=0,
                supporter_plays_remaining=1,
                channels=current.channels.__class__(supporter_play=False),
            ),
            next_turn,
        ),
    )
    assert locked_now_open_next.exact_joint_feasible
    assert locked_now_open_next.witness[0].turn == 1

    # Integrate the scheduler with the exact search transactions from the
    # preceding searched-Trainer execution-window result.
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    rosa = representative(profiles, "Rosa")
    secret_box = representative(profiles, "Secret Box")
    boss_target = SearchZoneTarget(
        "boss",
        TargetGroup("Boss's Orders", 1, frozenset({SUPPORTER})),
    )
    supporter_demand = make_demand("supporter", "Supporter card")

    rosa_allocation = enumerate_typed_target_profiles(
        rosa.base_outputs,
        (boss_target.group,),
        (supporter_demand,),
    )
    rosa_action = next(
        action
        for action in rosa_allocation.actions
        if action.output == (1,)
        and action.target_cost == (1,)
    )
    rosa_tx = execute_trainer_search_transaction(
        TrainerSearchExecutionState(
            zones=ZoneCountState.from_mapping(
                {
                    ("rosa", "hand"): 1,
                    ("boss", "deck"): 1,
                }
            )
        ),
        profile=rosa,
        action_card_class="rosa",
        demands=(supporter_demand,),
        targets=(boss_target,),
        search_action=rosa_action,
        play_condition_met=True,
    )
    rosa_deadline = evaluate_trainer_execution_capacity(
        {"boss": rosa_tx.after.zones.count("boss", "hand")},
        (
            TrainerExecutionRequirement(
                "gust this turn",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
        ),
        (execution_window_from_state(0, rosa_tx.after),),
    )
    assert not rosa_deadline.exact_joint_feasible

    secret_allocation = enumerate_typed_target_profiles(
        secret_box.base_outputs,
        (boss_target.group,),
        (supporter_demand,),
    )
    secret_action = next(
        action
        for action in secret_allocation.actions
        if action.output == (1,)
        and action.target_cost == (1,)
    )
    secret_state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("secret_box", "hand"): 1,
                ("fodder_a", "hand"): 1,
                ("fodder_b", "hand"): 1,
                ("fodder_c", "hand"): 1,
                ("boss", "deck"): 1,
            }
        )
    )
    candidates = (
        DiscardCandidate("fodder_a"),
        DiscardCandidate("fodder_b"),
        DiscardCandidate("fodder_c"),
    )
    selection = enumerate_discard_selections(
        secret_state.zones,
        candidates,
        3,
    )[0]
    secret_tx = execute_trainer_search_transaction(
        secret_state,
        profile=secret_box,
        action_card_class="secret_box",
        demands=(supporter_demand,),
        targets=(boss_target,),
        search_action=secret_action,
        discard_candidates=candidates,
        discard_selection=selection,
    )
    secret_deadline = evaluate_trainer_execution_capacity(
        {"boss": secret_tx.after.zones.count("boss", "hand")},
        (
            TrainerExecutionRequirement(
                "gust this turn",
                "boss",
                "Supporter",
                deadline_turn=0,
            ),
        ),
        (execution_window_from_state(0, secret_tx.after),),
    )
    assert secret_deadline.exact_joint_feasible

    print(
        json.dumps(
            {
                "two_supporters_individually_feasible": all(
                    ordinary_collision.individually_feasible
                ),
                "two_supporters_ordinary_joint_feasible": (
                    ordinary_collision.exact_joint_feasible
                ),
                "two_supporters_dual_quota_joint_feasible": (
                    dual_success.exact_joint_feasible
                ),
                "split_turn_deadlines_joint_feasible": (
                    split_success.exact_joint_feasible
                ),
                "two_next_turn_supporters_joint_feasible": (
                    next_collision.exact_joint_feasible
                ),
                "one_physical_copy_two_requirements_joint_feasible": (
                    physical_reuse.exact_joint_feasible
                ),
                "mixed_item_supporter_joint_feasible": (
                    mixed_classes.exact_joint_feasible
                ),
                "locked_now_open_next_joint_feasible": (
                    locked_now_open_next.exact_joint_feasible
                ),
                "rosa_same_turn_gust_executable": (
                    rosa_deadline.exact_joint_feasible
                ),
                "secret_box_same_turn_gust_executable": (
                    secret_deadline.exact_joint_feasible
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
