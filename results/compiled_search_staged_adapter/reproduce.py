"""Reproduce compiled search profiles flowing into staged objectives."""

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
from compiled_search_staged_adapter import (
    adapt_compiled_search_to_staged_action,
)
from search_zone_transition import SearchZoneTarget
from single_output_search_profile_compiler import (
    compile_single_output_revealed_search_profiles,
)
from staged_trainer_objectives import (
    TrainerAcquisitionRequirement,
    evaluate_staged_trainer_objectives,
)
from trainer_search_profile_compiler import (
    compile_multi_output_trainer_profiles,
)
from typed_search_target_allocator import (
    ITEM,
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
    single = compile_single_output_revealed_search_profiles(ROOT / "resources")
    multi = compile_multi_output_trainer_profiles(ROOT / "resources")
    skyla = representative(single, "Skyla")
    secret = representative(multi, "Secret Box")

    boss = SearchZoneTarget(
        "boss",
        TargetGroup("Boss's Orders", 1, frozenset({SUPPORTER})),
    )
    quick_ball = SearchZoneTarget(
        "quick_ball",
        TargetGroup("Quick Ball", 1, frozenset({ITEM})),
    )

    boss_trainer_demand = make_demand("boss trainer", "Trainer card")
    skyla_alloc = enumerate_typed_target_profiles(
        skyla.base_outputs,
        (boss.group,),
        (boss_trainer_demand,),
    )
    skyla_boss_action = next(
        action
        for action in skyla_alloc.actions
        if action.target_cost == (1,)
    )
    staged_skyla = adapt_compiled_search_to_staged_action(
        skyla,
        (boss_trainer_demand,),
        (boss,),
        skyla_boss_action,
        name="Skyla -> Boss",
    )
    assert staged_skyla.action_class == "Supporter"
    assert staged_skyla.discard_cost == 0
    assert staged_skyla.hand_outputs == (("boss", 1),)

    boss_demand = make_demand("boss supporter", "Supporter card")
    secret_boss_alloc = enumerate_typed_target_profiles(
        secret.base_outputs,
        (boss.group,),
        (boss_demand,),
    )
    secret_boss_action = next(
        action
        for action in secret_boss_alloc.actions
        if action.target_cost == (1,)
    )
    staged_secret_boss = adapt_compiled_search_to_staged_action(
        secret,
        (boss_demand,),
        (boss,),
        secret_boss_action,
        name="Secret Box -> Boss",
    )
    assert staged_secret_boss.action_class == "Item"
    assert staged_secret_boss.discard_cost == 3

    current = ExecutionTurnWindow(turn=0, supporter_plays_remaining=1)

    acquisition_only = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1},
        discardable_cards=3,
        acquisition_actions=(staged_skyla, staged_secret_boss),
        acquisition_requirements=(
            TrainerAcquisitionRequirement("Boss acquired", "boss"),
        ),
        windows=(current,),
    )
    assert acquisition_only.exact_joint_feasible
    assert acquisition_only.acquisition_actions == ("Skyla -> Boss",)
    assert acquisition_only.discard_spent == 0

    execution_now = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1},
        discardable_cards=3,
        acquisition_actions=(staged_skyla, staged_secret_boss),
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
    assert execution_now.exact_joint_feasible
    assert execution_now.acquisition_actions == ("Secret Box -> Boss",)
    assert execution_now.discard_spent == 3

    dual_supporter = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1},
        discardable_cards=3,
        acquisition_actions=(staged_skyla, staged_secret_boss),
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
    assert dual_supporter.acquisition_actions == ("Skyla -> Boss",)
    assert dual_supporter.discard_spent == 0

    pair_demands = (
        make_demand("quick item", "Item card"),
        make_demand("boss supporter", "Supporter card"),
    )
    secret_pair_alloc = enumerate_typed_target_profiles(
        secret.base_outputs,
        (quick_ball.group, boss.group),
        pair_demands,
    )
    secret_pair_action = next(
        action
        for action in secret_pair_alloc.actions
        if action.target_cost == (1, 1)
        and action.output == (1, 1)
    )
    staged_secret_pair = adapt_compiled_search_to_staged_action(
        secret,
        pair_demands,
        (quick_ball, boss),
        secret_pair_action,
        name="Secret Box -> Quick Ball + Boss",
    )
    assert staged_secret_pair.hand_outputs == (
        ("boss", 1),
        ("quick_ball", 1),
    )

    two_stage = evaluate_staged_trainer_objectives(
        {},
        searchable_cards={"boss": 1, "quick_ball": 1},
        discardable_cards=3,
        acquisition_actions=(staged_skyla, staged_secret_pair),
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
    assert two_stage.acquisition_actions == (
        "Secret Box -> Quick Ball + Boss",
    )
    assert two_stage.maximum_completed_units == 2

    print(
        json.dumps(
            {
                "skyla_action_class": staged_skyla.action_class,
                "secret_box_discard_cost": staged_secret_boss.discard_cost,
                "acquisition_only_choice": acquisition_only.acquisition_actions,
                "same_turn_execution_choice": execution_now.acquisition_actions,
                "dual_supporter_choice": dual_supporter.acquisition_actions,
                "secret_box_pair_outputs": staged_secret_pair.hand_outputs,
                "two_stage_choice": two_stage.acquisition_actions,
                "two_stage_completed_units": two_stage.maximum_completed_units,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
