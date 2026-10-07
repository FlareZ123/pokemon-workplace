"""Reproduce atomic Item/Supporter search transactions."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from discard_cost_witness import (
    DiscardCandidate,
    enumerate_discard_selections,
)
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_search_transaction,
)
from turn_action_budget import TurnActionBudget
from typed_search_target_allocator import (
    BASIC_ENERGY,
    BASIC_POKEMON,
    ITEM,
    POKEMON_TOOL,
    SPECIAL_ENERGY,
    STADIUM,
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


def expect_value_error(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")

    secret_box = representative(profiles, "Secret Box")
    secret_targets = (
        SearchZoneTarget(
            "target_item",
            TargetGroup("Item target", 1, frozenset({ITEM})),
        ),
        SearchZoneTarget(
            "target_tool",
            TargetGroup("Tool target", 1, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            "target_supporter",
            TargetGroup("Supporter target", 1, frozenset({SUPPORTER})),
        ),
        SearchZoneTarget(
            "target_stadium",
            TargetGroup("Stadium target", 1, frozenset({STADIUM})),
        ),
    )
    secret_demands = (
        make_demand("item", "Item card"),
        make_demand("tool", "Pokémon Tool card"),
        make_demand("supporter", "Supporter card"),
        make_demand("stadium", "Stadium card"),
    )
    secret_allocation = enumerate_typed_target_profiles(
        secret_box.base_outputs,
        tuple(target.group for target in secret_targets),
        secret_demands,
    )
    secret_action = next(
        action
        for action in secret_allocation.actions
        if action.output == (1, 1, 1, 1)
    )

    secret_state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("secret_box", "hand"): 1,
                ("fodder_a", "hand"): 1,
                ("fodder_b", "hand"): 1,
                ("boss", "hand"): 1,
                ("fodder_c", "hand"): 1,
                ("target_item", "deck"): 1,
                ("target_tool", "deck"): 1,
                ("target_supporter", "deck"): 1,
                ("target_stadium", "deck"): 1,
            }
        )
    )
    secret_candidates = (
        DiscardCandidate("fodder_a"),
        DiscardCandidate("fodder_b"),
        DiscardCandidate("boss", max_copies=0),
        DiscardCandidate("fodder_c"),
    )
    secret_selections = enumerate_discard_selections(
        secret_state.zones,
        secret_candidates,
        3,
    )
    assert len(secret_selections) == 1

    secret_tx = execute_trainer_search_transaction(
        secret_state,
        profile=secret_box,
        action_card_class="secret_box",
        demands=secret_demands,
        targets=secret_targets,
        search_action=secret_action,
        discard_candidates=secret_candidates,
        discard_selection=secret_selections[0],
    )
    assert secret_tx.discard_cost == 3
    assert not secret_tx.used_conditional_outputs
    assert secret_tx.after.zones.count("secret_box", "discard") == 1
    assert secret_tx.after.zones.count("boss", "hand") == 1
    for card_class in (
        "target_item",
        "target_tool",
        "target_supporter",
        "target_stadium",
    ):
        assert secret_tx.after.zones.count(card_class, "hand") == 1
    assert not secret_tx.after.budget.supporter_used

    item_lock_rejected = expect_value_error(
        lambda: execute_trainer_search_transaction(
            TrainerSearchExecutionState(
                zones=secret_state.zones,
                channels=PlayerChannels(item_play=False),
            ),
            profile=secret_box,
            action_card_class="secret_box",
            demands=secret_demands,
            targets=secret_targets,
            search_action=secret_action,
            discard_candidates=secret_candidates,
            discard_selection=secret_selections[0],
        )
    )
    assert item_lock_rejected

    arven = representative(profiles, "Arven")
    arven_targets = (
        SearchZoneTarget(
            "arven_item_target",
            TargetGroup("Arven Item target", 2, frozenset({ITEM})),
        ),
        SearchZoneTarget(
            "arven_tool_target",
            TargetGroup("Arven Tool target", 2, frozenset({POKEMON_TOOL})),
        ),
    )
    arven_demands = (
        make_demand("item", "Item card"),
        make_demand("tool", "Pokémon Tool card"),
    )
    arven_allocation = enumerate_typed_target_profiles(
        arven.base_outputs,
        tuple(target.group for target in arven_targets),
        arven_demands,
    )
    arven_action = next(
        action
        for action in arven_allocation.actions
        if action.output == (1, 1)
    )
    arven_state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("arven", "hand"): 2,
                ("arven_item_target", "deck"): 2,
                ("arven_tool_target", "deck"): 2,
            }
        )
    )
    arven_first = execute_trainer_search_transaction(
        arven_state,
        profile=arven,
        action_card_class="arven",
        demands=arven_demands,
        targets=arven_targets,
        search_action=arven_action,
    )
    assert arven_first.after.budget.supporter_used
    assert arven_first.after.zones.count("arven", "hand") == 1
    assert arven_first.after.zones.count("arven", "discard") == 1

    second_arven_rejected = expect_value_error(
        lambda: execute_trainer_search_transaction(
            arven_first.after,
            profile=arven,
            action_card_class="arven",
            demands=arven_demands,
            targets=arven_targets,
            search_action=arven_action,
        )
    )
    assert second_arven_rejected

    dual_arven_state = TrainerSearchExecutionState(
        zones=arven_state.zones,
        budget=TurnActionBudget(supporter_play_limit=2),
    )
    dual_arven_first = execute_trainer_search_transaction(
        dual_arven_state,
        profile=arven,
        action_card_class="arven",
        demands=arven_demands,
        targets=arven_targets,
        search_action=arven_action,
    )
    dual_arven_second = execute_trainer_search_transaction(
        dual_arven_first.after,
        profile=arven,
        action_card_class="arven",
        demands=arven_demands,
        targets=arven_targets,
        search_action=arven_action,
    )
    assert dual_arven_second.after.budget.supporter_plays_used == 2
    assert dual_arven_second.after.budget.supporter_play_limit == 2
    assert dual_arven_second.after.zones.count("arven", "hand") == 0
    assert dual_arven_second.after.zones.count("arven", "discard") == 2

    guzma_hala = representative(profiles, "Guzma & Hala")
    gh_targets = (
        SearchZoneTarget(
            "gh_stadium",
            TargetGroup("G&H Stadium", 1, frozenset({STADIUM})),
        ),
        SearchZoneTarget(
            "gh_tool",
            TargetGroup("G&H Tool", 1, frozenset({POKEMON_TOOL})),
        ),
        SearchZoneTarget(
            "gh_special",
            TargetGroup("G&H Special Energy", 1, frozenset({SPECIAL_ENERGY})),
        ),
    )
    gh_demands = (
        make_demand("stadium", "Stadium card"),
        make_demand("tool", "Pokémon Tool card"),
        make_demand("special", "Special Energy card"),
    )
    gh_allocation = enumerate_typed_target_profiles(
        guzma_hala.base_outputs + guzma_hala.conditional_outputs,
        tuple(target.group for target in gh_targets),
        gh_demands,
    )
    gh_action = next(
        action
        for action in gh_allocation.actions
        if action.output == (1, 1, 1)
    )
    gh_state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("guzma_hala", "hand"): 1,
                ("gh_fodder_a", "hand"): 1,
                ("gh_fodder_b", "hand"): 1,
                ("gh_stadium", "deck"): 1,
                ("gh_tool", "deck"): 1,
                ("gh_special", "deck"): 1,
            }
        )
    )
    gh_candidates = (
        DiscardCandidate("gh_fodder_a"),
        DiscardCandidate("gh_fodder_b"),
    )
    gh_selection = enumerate_discard_selections(
        gh_state.zones,
        gh_candidates,
        2,
    )[0]
    gh_tx = execute_trainer_search_transaction(
        gh_state,
        profile=guzma_hala,
        action_card_class="guzma_hala",
        demands=gh_demands,
        targets=gh_targets,
        search_action=gh_action,
        discard_candidates=gh_candidates,
        discard_selection=gh_selection,
    )
    assert gh_tx.discard_cost == 2
    assert gh_tx.used_conditional_outputs
    assert gh_tx.after.budget.supporter_used
    assert gh_tx.after.zones.count("guzma_hala", "discard") == 1
    for card_class in ("gh_stadium", "gh_tool", "gh_special"):
        assert gh_tx.after.zones.count(card_class, "hand") == 1

    print(
        json.dumps(
            {
                "secret_box_targets_moved": 4,
                "secret_box_exact_discard_cost": secret_tx.discard_cost,
                "secret_box_preserved_boss": True,
                "item_lock_rejected": item_lock_rejected,
                "arven_supporter_budget_consumed": arven_first.after.budget.supporter_used,
                "second_arven_same_turn_rejected": second_arven_rejected,
                "two_arven_with_limit_two_succeeded": True,
                "guzma_hala_conditional_branch": gh_tx.used_conditional_outputs,
                "guzma_hala_discard_cost": gh_tx.discard_cost,
                "card_totals_conserved": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
