"""Reproduce source-scoped permission gating on real Trainer transactions."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from card_action_metadata import card_action_metadata_by_id
from discard_cost_witness import (
    DiscardCandidate,
    enumerate_discard_selections,
)
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from source_scoped_action_restrictions import (
    build_source_scoped_action_restrictions,
)
from source_scoped_trainer_transaction import (
    execute_source_scoped_trainer_search_transaction,
)
from trainer_search_profile_compiler import compile_multi_output_trainer_profiles
from trainer_search_transaction import TrainerSearchExecutionState
from typed_search_target_allocator import (
    ITEM,
    POKEMON_TOOL,
    STADIUM,
    SUPPORTER,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)


def representative(profiles: tuple, name: str):
    matches = [profile for profile in profiles if profile.name == name]
    assert matches, name
    return matches[0]


def one_restriction(rows, card_id: str, needle: str):
    matches = [
        row
        for row in rows
        if row.card_id == card_id
        and (needle in row.source or needle in row.text)
    ]
    assert len(matches) == 1, (card_id, needle, len(matches))
    return matches[0]


def rejected(fn) -> bool:
    try:
        fn()
    except ValueError:
        return True
    return False


def main() -> None:
    resources = ROOT / "resources"
    profiles = compile_multi_output_trainer_profiles(resources)
    metadata = card_action_metadata_by_id(resources)
    restrictions = build_source_scoped_action_restrictions(resources)

    secret_box = representative(profiles, "Secret Box")
    assert secret_box.card_id == "sv6-163"
    secret_metadata = metadata[secret_box.card_id]
    assert secret_metadata.card_kind == "item"
    assert "ace_spec" in secret_metadata.tags

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
        DiscardCandidate("fodder_c"),
    )
    secret_selection = enumerate_discard_selections(
        secret_state.zones,
        secret_candidates,
        3,
    )[0]

    secret_baseline = execute_source_scoped_trainer_search_transaction(
        secret_state,
        profile=secret_box,
        action_metadata=secret_metadata,
        action_card_class="secret_box",
        demands=secret_demands,
        targets=secret_targets,
        search_action=secret_action,
        discard_candidates=secret_candidates,
        discard_selection=secret_selection,
    )
    assert secret_baseline.after.channels == secret_state.channels
    assert secret_baseline.after.zones.count("secret_box", "discard") == 1

    vileplume = one_restriction(
        restrictions,
        "xy7-3",
        "Irritating Pollen",
    )
    assert rejected(
        lambda: execute_source_scoped_trainer_search_transaction(
            secret_state,
            profile=secret_box,
            action_metadata=secret_metadata,
            active_restrictions=(vileplume,),
            action_card_class="secret_box",
            demands=secret_demands,
            targets=secret_targets,
            search_action=secret_action,
            discard_candidates=secret_candidates,
            discard_selection=secret_selection,
        )
    )

    sealing_scream = one_restriction(
        restrictions,
        "bw11-87",
        "Sealing Scream",
    )
    assert rejected(
        lambda: execute_source_scoped_trainer_search_transaction(
            secret_state,
            profile=secret_box,
            action_metadata=secret_metadata,
            active_restrictions=(sealing_scream,),
            action_card_class="secret_box",
            demands=secret_demands,
            targets=secret_targets,
            search_action=secret_action,
            discard_candidates=secret_candidates,
            discard_selection=secret_selection,
        )
    )

    arven = representative(profiles, "Arven")
    arven_metadata = metadata[arven.card_id]
    assert arven_metadata.card_kind == "supporter"
    arven_targets = (
        SearchZoneTarget(
            "arven_item",
            TargetGroup("Arven Item", 1, frozenset({ITEM})),
        ),
        SearchZoneTarget(
            "arven_tool",
            TargetGroup("Arven Tool", 1, frozenset({POKEMON_TOOL})),
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
                ("arven", "hand"): 1,
                ("arven_item", "deck"): 1,
                ("arven_tool", "deck"): 1,
            }
        )
    )

    arven_under_vileplume = execute_source_scoped_trainer_search_transaction(
        arven_state,
        profile=arven,
        action_metadata=arven_metadata,
        active_restrictions=(vileplume,),
        action_card_class="arven",
        demands=arven_demands,
        targets=arven_targets,
        search_action=arven_action,
    )
    assert arven_under_vileplume.after.budget.supporter_used
    assert arven_under_vileplume.after.channels == arven_state.channels

    dark_moon = one_restriction(
        restrictions,
        "sm11-125",
        "Dark Moon-GX",
    )
    assert rejected(
        lambda: execute_source_scoped_trainer_search_transaction(
            arven_state,
            profile=arven,
            action_metadata=arven_metadata,
            active_restrictions=(dark_moon,),
            action_card_class="arven",
            demands=arven_demands,
            targets=arven_targets,
            search_action=arven_action,
        )
    )

    print(
        json.dumps(
            {
                "secret_box_baseline_succeeds": True,
                "vileplume_blocks_hand_secret_box": True,
                "sealing_scream_blocks_ace_spec_secret_box": True,
                "arven_survives_item_only_vileplume": True,
                "dark_moon_blocks_arven_supporter": True,
                "base_channels_restored_after_transaction": True,
                "exact_metadata_drives_ace_spec_selector": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
