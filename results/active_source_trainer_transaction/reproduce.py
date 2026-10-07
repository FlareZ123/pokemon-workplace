"""Reproduce live-source aggregation feeding real Trainer transactions."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from active_source_scoped_restrictions import ContinuousRestrictionSource
from active_source_trainer_transaction import (
    execute_active_source_trainer_search_transaction,
)
from attack_restriction_turn_windows import (
    begin_turn,
    create_attack_restriction_window,
    end_turn,
)
from attack_source_scoped_restrictions import materialize_attack_restriction
from card_action_metadata import card_action_metadata_by_id
from continuous_source_scoped_restrictions import ContinuousRestrictionContext
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from source_scoped_restriction_activation import build_restriction_activation_profiles
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_transaction import TrainerSearchExecutionState
from typed_search_target_allocator import (
    ITEM,
    POKEMON_TOOL,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


def _profile(profiles, name: str):
    matches = [row for row in profiles if row.name == name]
    assert matches, name
    return matches[0]


def _restriction_profile(profiles, card_id: str, needle: str):
    matches = [
        row
        for row in profiles
        if row.restriction.card_id == card_id
        and (
            needle in row.restriction.source
            or needle in row.restriction.text
        )
    ]
    assert len(matches) == 1, (card_id, needle, len(matches))
    return matches[0]


def _rejected(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    resources = ROOT / "resources"
    trainer_profiles = compile_multi_output_trainer_profiles(resources)
    action_metadata = card_action_metadata_by_id(resources)
    restriction_profiles = build_restriction_activation_profiles(resources)

    arven = _profile(trainer_profiles, "Arven")
    arven_metadata = action_metadata[arven.card_id]
    targets = (
        SearchZoneTarget(
            "arven_item",
            TargetGroup("Arven Item", 1, frozenset({ITEM})),
        ),
        SearchZoneTarget(
            "arven_tool",
            TargetGroup("Arven Tool", 1, frozenset({POKEMON_TOOL})),
        ),
    )
    demands = (
        make_demand("item", "Item card"),
        make_demand("tool", "Pokémon Tool card"),
    )
    allocation = enumerate_typed_target_profiles(
        arven.base_outputs,
        tuple(target.group for target in targets),
        demands,
    )
    search_action = next(
        action for action in allocation.actions
        if action.output == (1, 1)
    )
    state = TrainerSearchExecutionState(
        zones=ZoneCountState.from_mapping(
            {
                ("arven", "hand"): 1,
                ("arven_item", "deck"): 1,
                ("arven_tool", "deck"): 1,
            }
        )
    )

    vileplume = _restriction_profile(
        restriction_profiles,
        "xy7-3",
        "Irritating Pollen",
    )
    vileplume_source = ContinuousRestrictionSource(
        profile=vileplume,
        context=ContinuousRestrictionContext(
            source_in_play=True,
            ability_enabled=True,
            source_active=False,
        ),
        source_player="A",
        other_player="B",
    )

    arven_under_vileplume = execute_active_source_trainer_search_transaction(
        state,
        player="A",
        profile=arven,
        action_metadata=arven_metadata,
        action_card_class="arven",
        demands=demands,
        targets=targets,
        search_action=search_action,
        continuous_sources=(vileplume_source,),
    )
    assert arven_under_vileplume.after.budget.supporter_used

    psyduck = _restriction_profile(
        restriction_profiles,
        "sm9-26",
        "Headache",
    )
    headache = materialize_attack_restriction(psyduck, coin_heads=True)
    assert headache is not None
    headache_window = create_attack_restriction_window(
        psyduck,
        headache,
        source_player="B",
        other_player="A",
    )
    headache_window = begin_turn(headache_window, "A")

    assert _rejected(
        lambda: execute_active_source_trainer_search_transaction(
            state,
            player="A",
            profile=arven,
            action_metadata=arven_metadata,
            action_card_class="arven",
            demands=demands,
            targets=targets,
            search_action=search_action,
            continuous_sources=(vileplume_source,),
            attack_windows=(headache_window,),
        )
    )

    arven_for_b = execute_active_source_trainer_search_transaction(
        state,
        player="B",
        profile=arven,
        action_metadata=arven_metadata,
        action_card_class="arven",
        demands=demands,
        targets=targets,
        search_action=search_action,
        continuous_sources=(vileplume_source,),
        attack_windows=(headache_window,),
    )
    assert arven_for_b.after.budget.supporter_used

    expired = end_turn(headache_window, "A")
    arven_after_expiry = execute_active_source_trainer_search_transaction(
        state,
        player="A",
        profile=arven,
        action_metadata=arven_metadata,
        action_card_class="arven",
        demands=demands,
        targets=targets,
        search_action=search_action,
        continuous_sources=(vileplume_source,),
        attack_windows=(expired,),
    )
    assert arven_after_expiry.after.budget.supporter_used

    print(
        json.dumps(
            {
                "arven_survives_live_item_lock": True,
                "live_headache_blocks_arven_for_target": True,
                "headache_does_not_block_source_player": True,
                "expired_headache_stops_blocking": True,
                "supporter_budget_still_owned_by_base_transaction": True,
                "active_sources_feed_transaction_without_manual_tuple": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
