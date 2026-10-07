"""Reproduce end-to-end typed Trainer search state adaptation."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from lock_state_kernel import PlayerChannels, apply_play_lock
from resource_constrained_connectors import evaluate_resource_constrained_connectors
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_state_adapter import (
    TrainerSearchState,
    adapt_compiled_search_profile_typed,
)
from typed_search_target_allocator import (
    BASIC_ENERGY,
    BASIC_POKEMON,
    ITEM,
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STADIUM,
    SUPPORTER,
    TargetGroup,
    make_demand,
)


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    if not matches:
        raise AssertionError(f"{name} missing")
    return matches[0]


def exact_result(adaptation, demand):
    assert adaptation is not None
    return evaluate_resource_constrained_connectors(
        demand,
        adaptation.resource_capacities,
        (adaptation.connector,),
    )


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")

    # Broad compiled categories satisfy narrower demands through physical targets.
    rosa = representative(profiles, "Rosa")
    rosa_targets = (
        TargetGroup("Bagon", 1, frozenset({BASIC_POKEMON, "type:dragon"})),
        TargetGroup("Quick Ball", 1, frozenset({ITEM})),
        TargetGroup("Basic Fire Energy", 1, frozenset({BASIC_ENERGY, "type:fire"})),
    )
    rosa_demands = (
        make_demand("basic attacker", "Basic Pokémon"),
        make_demand("item", "Item card"),
        make_demand("basic energy", "Basic Energy card"),
    )
    rosa_state = TrainerSearchState(supporter_plays_remaining=1)
    rosa_adapted = adapt_compiled_search_profile_typed(
        rosa,
        rosa_demands,
        rosa_targets,
        rosa_state,
        play_condition_met=True,
    )
    rosa_result = exact_result(rosa_adapted, (1, 1, 1))
    assert rosa_result.exact_joint_feasible

    assert adapt_compiled_search_profile_typed(
        rosa,
        rosa_demands,
        rosa_targets,
        TrainerSearchState(
            channels=apply_play_lock(PlayerChannels(), "supporter"),
        ),
        play_condition_met=True,
    ) is None

    # A conditional axis can be the only useful path to a broad demand.
    guzma_hala = representative(profiles, "Guzma & Hala")
    tool_target = (
        TargetGroup("Float Stone", 1, frozenset({POKEMON_TOOL})),
    )
    trainer_demand = (
        make_demand("trainer", "Trainer card"),
    )
    paid_gh = adapt_compiled_search_profile_typed(
        guzma_hala,
        trainer_demand,
        tool_target,
        TrainerSearchState(
            discardable_cards=2,
            supporter_plays_remaining=1,
        ),
    )
    paid_gh_result = exact_result(paid_gh, (1,))
    assert paid_gh_result.exact_joint_feasible
    assert any(
        action.cost[0] == 2
        for action in paid_gh.connector.profiles
    )

    unpaid_gh = adapt_compiled_search_profile_typed(
        guzma_hala,
        trainer_demand,
        tool_target,
        TrainerSearchState(
            discardable_cards=0,
            supporter_plays_remaining=1,
        ),
    )
    assert unpaid_gh is None

    # Search-text output, discard cost, subtype matching, and target depletion
    # all reach the shared connector solver in one state.
    secret_box = representative(profiles, "Secret Box")
    secret_targets = (
        TargetGroup("Item target", 1, frozenset({ITEM})),
        TargetGroup("Tool target", 1, frozenset({POKEMON_TOOL})),
        TargetGroup("Supporter target", 1, frozenset({SUPPORTER})),
        TargetGroup("Stadium target", 1, frozenset({STADIUM})),
    )
    secret_demands = (
        make_demand("item", "Item card"),
        make_demand("tool", "Pokémon Tool card"),
        make_demand("supporter", "Supporter card"),
        make_demand("stadium", "Stadium card"),
    )
    secret_adapted = adapt_compiled_search_profile_typed(
        secret_box,
        secret_demands,
        secret_targets,
        TrainerSearchState(discardable_cards=3),
    )
    secret_result = exact_result(secret_adapted, (1, 1, 1, 1))
    assert secret_result.exact_joint_feasible
    assert len(secret_adapted.resource_capacities) == 7

    assert adapt_compiled_search_profile_typed(
        secret_box,
        secret_demands,
        secret_targets,
        TrainerSearchState(discardable_cards=2),
    ) is None

    # Target counts are now shared resources across several connector copies.
    arven = representative(profiles, "Arven")
    item_demand_two = (
        make_demand("two distinct items", "Item card", copies=2),
    )
    one_item_target = (
        TargetGroup("Quick Ball", 1, frozenset({ITEM})),
    )
    two_arven_one_target = adapt_compiled_search_profile_typed(
        arven,
        item_demand_two,
        one_item_target,
        TrainerSearchState(supporter_plays_remaining=2),
        copies=2,
    )
    one_target_result = exact_result(
        two_arven_one_target,
        (2,),
    )
    assert one_target_result.raw_naive_joint_reachable
    assert not one_target_result.exact_joint_feasible

    two_item_targets = (
        TargetGroup("Quick Ball", 2, frozenset({ITEM})),
    )
    two_arven_two_targets = adapt_compiled_search_profile_typed(
        arven,
        item_demand_two,
        two_item_targets,
        TrainerSearchState(supporter_plays_remaining=2),
        copies=2,
    )
    two_target_result = exact_result(
        two_arven_two_targets,
        (2,),
    )
    assert two_target_result.exact_joint_feasible

    print(
        json.dumps(
            {
                "rosa_broad_to_narrow_joint_feasible": rosa_result.exact_joint_feasible,
                "guzma_hala_conditional_tool_to_trainer_feasible": paid_gh_result.exact_joint_feasible,
                "secret_box_full_state_feasible": secret_result.exact_joint_feasible,
                "typed_resource_dimensions_for_secret_box": len(secret_adapted.resource_capacities),
                "two_arven_single_item_target_feasible": one_target_result.exact_joint_feasible,
                "two_arven_two_item_targets_feasible": two_target_result.exact_joint_feasible,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
