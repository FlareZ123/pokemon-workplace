"""Reproduce typed search-target allocation and semantic overlap guards."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from trainer_search_profile_compiler import (
    SearchOutput,
    compile_multi_output_trainer_profiles,
)
from typed_search_target_allocator import (
    BASIC_ENERGY,
    BASIC_POKEMON,
    ENERGY,
    ITEM,
    POKEMON,
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STAGE_1_POKEMON,
    STAGE_2_POKEMON,
    SUPPORTER,
    TRAINER,
    DemandChannel,
    SearchSelector,
    TargetGroup,
    UnsupportedSearchSelector,
    enumerate_typed_target_profiles,
    make_demand,
    selector_from_label,
)


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def main() -> None:
    compiled = compile_multi_output_trainer_profiles(ROOT / "resources")
    labels = sorted(
        {
            output.label
            for profile in compiled
            for output in (
                profile.base_outputs
                + profile.conditional_outputs
            )
        }
    )
    unsupported = []
    for label in labels:
        try:
            selector_from_label(label)
        except UnsupportedSearchSelector:
            unsupported.append(label)
    assert unsupported == []

    quick_ball = TargetGroup(
        "Quick Ball",
        1,
        frozenset({ITEM}),
    )
    boss = TargetGroup(
        "Boss's Orders",
        1,
        frozenset({SUPPORTER}),
    )
    tool = TargetGroup(
        "Float Stone",
        1,
        frozenset({POKEMON_TOOL}),
    )

    assert TRAINER in quick_ball.tags
    assert TRAINER in tool.tags
    assert ITEM not in tool.tags

    broad_trainer = enumerate_typed_target_profiles(
        (SearchOutput("Trainer card", 1),),
        (quick_ball, boss),
        (
            make_demand("need item", "Item card"),
            make_demand("need supporter", "Supporter card"),
        ),
    )
    assert not broad_trainer.full_demand_feasible
    assert broad_trainer.minimum_unmet_units == 1
    assert set(broad_trainer.profiles) == {
        (1, 0),
        (0, 1),
    }

    overlapping_axes_one_copy = enumerate_typed_target_profiles(
        (
            SearchOutput("Trainer card", 1),
            SearchOutput("Item card", 1),
        ),
        (quick_ball,),
        (
            make_demand("distinct trainer", "Trainer card"),
            make_demand("distinct item", "Item card"),
        ),
    )
    assert not overlapping_axes_one_copy.full_demand_feasible
    assert overlapping_axes_one_copy.minimum_unmet_units == 1

    overlapping_axes_two_copies = enumerate_typed_target_profiles(
        (
            SearchOutput("Trainer card", 1),
            SearchOutput("Item card", 1),
        ),
        (
            TargetGroup(
                "Quick Ball",
                2,
                frozenset({ITEM}),
            ),
        ),
        (
            make_demand("distinct trainer", "Trainer card"),
            make_demand("distinct item", "Item card"),
        ),
    )
    assert overlapping_axes_two_copies.full_demand_feasible

    item_only = enumerate_typed_target_profiles(
        (SearchOutput("Item card", 1),),
        (tool,),
        (make_demand("item", "Item card"),),
    )
    assert item_only.profiles == ()
    assert not item_only.full_demand_feasible

    secret_box = representative(compiled, "Secret Box")
    secret_targets = (
        TargetGroup("Item target", 1, frozenset({ITEM})),
        TargetGroup("Tool target", 1, frozenset({POKEMON_TOOL})),
        TargetGroup("Supporter target", 1, frozenset({SUPPORTER})),
        TargetGroup("Stadium target", 1, frozenset({"stadium"})),
    )
    secret_demands = (
        make_demand("item", "Item card"),
        make_demand("tool", "Pokémon Tool card"),
        make_demand("supporter", "Supporter card"),
        make_demand("stadium", "Stadium card"),
    )
    secret_result = enumerate_typed_target_profiles(
        secret_box.base_outputs,
        secret_targets,
        secret_demands,
    )
    assert secret_result.full_demand_feasible
    assert (1, 1, 1, 1) in secret_result.profiles

    basic_fire = TargetGroup(
        "Basic Fire Energy",
        1,
        frozenset({BASIC_ENERGY, "type:fire"}),
    )
    dce = TargetGroup(
        "Double Colorless Energy",
        1,
        frozenset({SPECIAL_ENERGY}),
    )
    assert ENERGY in basic_fire.tags
    assert ENERGY in dce.tags

    one_energy_search = enumerate_typed_target_profiles(
        (SearchOutput("Energy card", 1),),
        (basic_fire, dce),
        (
            make_demand("basic", "Basic Energy card"),
            make_demand("special", "Special Energy card"),
        ),
    )
    assert not one_energy_search.full_demand_feasible
    assert one_energy_search.minimum_unmet_units == 1

    two_energy_search = enumerate_typed_target_profiles(
        (SearchOutput("Energy card", 2),),
        (basic_fire, dce),
        (
            make_demand("basic", "Basic Energy card"),
            make_demand("special", "Special Energy card"),
        ),
    )
    assert two_energy_search.full_demand_feasible

    dawn = representative(compiled, "Dawn")
    basic = TargetGroup(
        "Basic target",
        1,
        frozenset({BASIC_POKEMON}),
    )
    stage_one = TargetGroup(
        "Stage 1 target",
        1,
        frozenset({STAGE_1_POKEMON}),
    )
    stage_two = TargetGroup(
        "Stage 2 target",
        1,
        frozenset({STAGE_2_POKEMON}),
    )
    assert POKEMON in basic.tags
    assert POKEMON in stage_one.tags
    assert POKEMON in stage_two.tags

    dawn_result = enumerate_typed_target_profiles(
        dawn.base_outputs,
        (basic, stage_one, stage_two),
        (
            make_demand("basic", "Basic Pokémon"),
            make_demand("stage 1", "Stage 1 Pokémon"),
            make_demand("stage 2", "Stage 2 Pokémon"),
        ),
    )
    assert dawn_result.full_demand_feasible

    irida = representative(compiled, "Irida")
    water_basic = TargetGroup(
        "Water Basic",
        1,
        frozenset({BASIC_POKEMON, "type:water"}),
    )
    fire_basic = TargetGroup(
        "Fire Basic",
        1,
        frozenset({BASIC_POKEMON, "type:fire"}),
    )
    water_only = enumerate_typed_target_profiles(
        (irida.base_outputs[0],),
        (water_basic, fire_basic),
        (make_demand("water", "Water Pokémon"),),
    )
    assert water_only.full_demand_feasible

    no_water = enumerate_typed_target_profiles(
        (irida.base_outputs[0],),
        (fire_basic,),
        (make_demand("water", "Water Pokémon"),),
    )
    assert not no_water.full_demand_feasible

    sabrina_brycen = representative(compiled, "Sabrina & Brycen")
    different_types = sabrina_brycen.conditional_outputs[0]
    three_pokemon_demand = (
        make_demand("three pokemon", "Pokémon", copies=3),
    )
    three_distinct_types = enumerate_typed_target_profiles(
        (different_types,),
        (
            TargetGroup(
                "Water target",
                1,
                frozenset({BASIC_POKEMON, "type:water"}),
            ),
            TargetGroup(
                "Fire target",
                1,
                frozenset({BASIC_POKEMON, "type:fire"}),
            ),
            TargetGroup(
                "Lightning target",
                1,
                frozenset({BASIC_POKEMON, "type:lightning"}),
            ),
        ),
        three_pokemon_demand,
    )
    assert three_distinct_types.full_demand_feasible

    duplicate_type_pool = enumerate_typed_target_profiles(
        (different_types,),
        (
            TargetGroup(
                "Water copies",
                2,
                frozenset({BASIC_POKEMON, "type:water"}),
            ),
            TargetGroup(
                "Fire target",
                1,
                frozenset({BASIC_POKEMON, "type:fire"}),
            ),
        ),
        three_pokemon_demand,
    )
    assert not duplicate_type_pool.full_demand_feasible
    assert duplicate_type_pool.minimum_unmet_units == 1

    untyped_pool = enumerate_typed_target_profiles(
        (different_types,),
        (
            TargetGroup(
                "Unknown-type target",
                3,
                frozenset({BASIC_POKEMON}),
            ),
        ),
        three_pokemon_demand,
    )
    assert not untyped_pool.full_demand_feasible

    print(
        json.dumps(
            {
                "compiled_labels": len(labels),
                "supported_structural_labels": len(labels) - len(unsupported),
                "unsupported_labels": unsupported,
                "sabrina_three_distinct_types_feasible": three_distinct_types.full_demand_feasible,
                "sabrina_duplicate_type_pool_feasible": duplicate_type_pool.full_demand_feasible,
                "broad_trainer_two_demands_feasible": broad_trainer.full_demand_feasible,
                "overlapping_axes_one_copy_feasible": overlapping_axes_one_copy.full_demand_feasible,
                "overlapping_axes_two_copies_feasible": overlapping_axes_two_copies.full_demand_feasible,
                "tool_counts_as_item": ITEM in tool.tags,
                "secret_box_four_axis_feasible": secret_result.full_demand_feasible,
                "one_energy_search_two_demands_feasible": one_energy_search.full_demand_feasible,
                "two_energy_search_two_demands_feasible": two_energy_search.full_demand_feasible,
                "dawn_three_stage_feasible": dawn_result.full_demand_feasible,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
