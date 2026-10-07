"""Reproduce acquisition-versus-execution contention for deck-search payloads."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from acquired_trainer_action_window import (
    evaluate_acquired_trainer_action_window,
)
from discard_cost_witness import (
    DiscardCandidate,
    enumerate_discard_selections,
)
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from resource_constrained_connectors import (
    evaluate_resource_constrained_connectors,
)
from search_zone_transition import SearchZoneTarget
from trainer_search_profile_compiler import (
    compile_multi_output_trainer_profiles,
)
from trainer_search_state_adapter import (
    TrainerSearchState,
    adapt_compiled_search_profile_typed,
)
from trainer_search_transaction import (
    TrainerSearchExecutionState,
    execute_trainer_search_transaction,
)
from turn_action_budget import TurnActionBudget
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


def single_target_action(profile, target, demand):
    allocation = enumerate_typed_target_profiles(
        profile.base_outputs,
        (target.group,),
        (demand,),
    )
    return next(
        action
        for action in allocation.actions
        if action.output == (1,)
        and action.target_cost == (1,)
    )


def main() -> None:
    profiles = compile_multi_output_trainer_profiles(ROOT / "resources")
    rosa = representative(profiles, "Rosa")
    secret_box = representative(profiles, "Secret Box")

    boss_target = SearchZoneTarget(
        "boss",
        TargetGroup("Boss's Orders", 1, frozenset({SUPPORTER})),
    )
    supporter_demand = make_demand("supporter", "Supporter card")

    # Static connector feasibility correctly proves acquisition. It does not
    # promise that the acquired Supporter still has an action window.
    rosa_adaptation = adapt_compiled_search_profile_typed(
        rosa,
        (supporter_demand,),
        (boss_target.group,),
        TrainerSearchState(supporter_plays_remaining=1),
        play_condition_met=True,
    )
    assert rosa_adaptation is not None
    rosa_acquisition = evaluate_resource_constrained_connectors(
        (1,),
        rosa_adaptation.resource_capacities,
        (rosa_adaptation.connector,),
    )
    assert rosa_acquisition.exact_joint_feasible

    rosa_action = single_target_action(
        rosa,
        boss_target,
        supporter_demand,
    )
    rosa_state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("rosa", "hand"): 1,
                ("boss", "deck"): 1,
            }
        )
    )
    rosa_tx = execute_trainer_search_transaction(
        rosa_state,
        profile=rosa,
        action_card_class="rosa",
        demands=(supporter_demand,),
        targets=(boss_target,),
        search_action=rosa_action,
        play_condition_met=True,
    )
    assert rosa_tx.after.zones.count("boss", "hand") == 1
    rosa_boss_window = evaluate_acquired_trainer_action_window(
        rosa_tx.after,
        card_class="boss",
        action_class="Supporter",
    )
    assert not rosa_boss_window.window_available
    assert rosa_boss_window.quota_remaining == 0

    # A second Supporter allowance converts the same acquisition into a live
    # same-turn action window.
    dual_rosa_state = TrainerSearchExecutionState(
        zones=rosa_state.zones,
        budget=TurnActionBudget(supporter_play_limit=2),
    )
    dual_rosa_tx = execute_trainer_search_transaction(
        dual_rosa_state,
        profile=rosa,
        action_card_class="rosa",
        demands=(supporter_demand,),
        targets=(boss_target,),
        search_action=rosa_action,
        play_condition_met=True,
    )
    dual_boss_window = evaluate_acquired_trainer_action_window(
        dual_rosa_tx.after,
        card_class="boss",
        action_class="Supporter",
    )
    assert dual_boss_window.window_available
    assert dual_boss_window.quota_remaining == 1

    # A turn boundary also restores the ordinary Supporter quota if the payload
    # remains in hand.
    rosa_next_turn = TrainerSearchExecutionState(
        zones=rosa_tx.after.zones,
        budget=rosa_tx.after.budget.next_turn(),
        channels=rosa_tx.after.channels,
    )
    next_turn_boss_window = evaluate_acquired_trainer_action_window(
        rosa_next_turn,
        card_class="boss",
        action_class="Supporter",
    )
    assert next_turn_boss_window.window_available

    # The same broad Rosa Trainer output can find an Item. The Supporter quota
    # spent by Rosa does not consume the Item action channel.
    item_target = SearchZoneTarget(
        "quick_ball",
        TargetGroup("Quick Ball", 1, frozenset({ITEM})),
    )
    item_demand = make_demand("item", "Item card")
    rosa_item_action = single_target_action(
        rosa,
        item_target,
        item_demand,
    )
    rosa_item_tx = execute_trainer_search_transaction(
        TrainerSearchExecutionState(
            zones=ZoneCountState.from_mapping(
                {
                    ("rosa", "hand"): 1,
                    ("quick_ball", "deck"): 1,
                }
            )
        ),
        profile=rosa,
        action_card_class="rosa",
        demands=(item_demand,),
        targets=(item_target,),
        search_action=rosa_item_action,
        play_condition_met=True,
    )
    rosa_item_window = evaluate_acquired_trainer_action_window(
        rosa_item_tx.after,
        card_class="quick_ball",
        action_class="Item",
    )
    assert rosa_item_window.window_available

    # Secret Box is an Item, so finding a Supporter leaves the ordinary
    # Supporter quota untouched. Exact discard payment is still required.
    secret_action = single_target_action(
        secret_box,
        boss_target,
        supporter_demand,
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
    secret_boss_window = evaluate_acquired_trainer_action_window(
        secret_tx.after,
        card_class="boss",
        action_class="Supporter",
    )
    assert secret_boss_window.window_available
    assert secret_boss_window.quota_remaining == 1

    # Acquisition and execution locks remain separate: Supporter lock does not
    # stop the Item search, but it does close the acquired payload's window.
    locked_secret_state = TrainerSearchExecutionState(
        zones=secret_state.zones,
        channels=PlayerChannels(supporter_play=False),
    )
    locked_secret_tx = execute_trainer_search_transaction(
        locked_secret_state,
        profile=secret_box,
        action_card_class="secret_box",
        demands=(supporter_demand,),
        targets=(boss_target,),
        search_action=secret_action,
        discard_candidates=candidates,
        discard_selection=selection,
    )
    locked_boss_window = evaluate_acquired_trainer_action_window(
        locked_secret_tx.after,
        card_class="boss",
        action_class="Supporter",
    )
    assert locked_secret_tx.after.zones.count("boss", "hand") == 1
    assert not locked_boss_window.window_available

    print(
        json.dumps(
            {
                "rosa_static_supporter_acquisition_feasible": (
                    rosa_acquisition.exact_joint_feasible
                ),
                "rosa_same_turn_supporter_window": (
                    rosa_boss_window.window_available
                ),
                "rosa_dual_brains_like_window": (
                    dual_boss_window.window_available
                ),
                "rosa_next_turn_supporter_window": (
                    next_turn_boss_window.window_available
                ),
                "rosa_same_turn_item_window": (
                    rosa_item_window.window_available
                ),
                "secret_box_same_turn_supporter_window": (
                    secret_boss_window.window_available
                ),
                "secret_box_supporter_locked_acquisition": (
                    locked_secret_tx.after.zones.count("boss", "hand") == 1
                ),
                "secret_box_supporter_locked_window": (
                    locked_boss_window.window_available
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
