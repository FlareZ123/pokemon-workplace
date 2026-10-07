"""Reproduce board-derived lock state feeding real Trainer transactions."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_causal_state import initialize_snapshot_lock_state
from attack_restriction_turn_windows import begin_turn, create_attack_restriction_window
from attack_source_scoped_restrictions import materialize_attack_restriction
from board_derived_trainer_transaction import (
    execute_board_derived_trainer_search_transaction,
)
from board_object_kernel import ToolAttachment, make_board, make_pokemon
from card_action_metadata import card_action_metadata_by_id
from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from multicopy_zone_state import ZoneCountState
from search_zone_transition import SearchZoneTarget
from source_scoped_restriction_activation import build_restriction_activation_profiles
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


def _secret_box_case(trainer_profiles, metadata):
    secret_box = _profile(trainer_profiles, "Secret Box")
    secret_metadata = metadata[secret_box.card_id]
    targets = (
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
    demands = (
        make_demand("item", "Item card"),
        make_demand("tool", "Pokémon Tool card"),
        make_demand("supporter", "Supporter card"),
        make_demand("stadium", "Stadium card"),
    )
    allocation = enumerate_typed_target_profiles(
        secret_box.base_outputs,
        tuple(target.group for target in targets),
        demands,
    )
    action = next(
        row for row in allocation.actions
        if row.output == (1, 1, 1, 1)
    )
    state = TrainerSearchExecutionState(
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
    candidates = (
        DiscardCandidate("fodder_a"),
        DiscardCandidate("fodder_b"),
        DiscardCandidate("fodder_c"),
    )
    selection = enumerate_discard_selections(
        state.zones,
        candidates,
        3,
    )[0]
    return (
        secret_box,
        secret_metadata,
        targets,
        demands,
        action,
        state,
        candidates,
        selection,
    )


def _arven_case(trainer_profiles, metadata):
    arven = _profile(trainer_profiles, "Arven")
    arven_metadata = metadata[arven.card_id]
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
    action = next(
        row for row in allocation.actions
        if row.output == (1, 1)
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
    return arven, arven_metadata, targets, demands, action, state


def main() -> None:
    resources = ROOT / "resources"
    trainer_profiles = compile_multi_output_trainer_profiles(resources)
    metadata = card_action_metadata_by_id(resources)
    restriction_profiles = build_restriction_activation_profiles(resources)

    (
        secret_box,
        secret_metadata,
        secret_targets,
        secret_demands,
        secret_action,
        secret_state,
        secret_candidates,
        secret_selection,
    ) = _secret_box_case(trainer_profiles, metadata)

    arven, arven_metadata, arven_targets, arven_demands, arven_action, arven_state = (
        _arven_case(trainer_profiles, metadata)
    )

    vileplume = make_pokemon(
        "vileplume",
        "Vileplume",
        print_id="xy7-3",
        tags=("Stage2",),
    )
    opponent_filler = make_pokemon("opponent-filler", "Opponent Filler")
    vileplume_board = make_board(vileplume)
    filler_board = make_board(opponent_filler)
    vileplume_lock = initialize_snapshot_lock_state(vileplume_board, filler_board)
    assert vileplume_lock.resolved

    assert _rejected(
        lambda: execute_board_derived_trainer_search_transaction(
            secret_state,
            player="A",
            player_board=vileplume_board,
            opponent_board=filler_board,
            restriction_profiles=restriction_profiles,
            lock_state=vileplume_lock,
            profile=secret_box,
            action_metadata=secret_metadata,
            action_card_class="secret_box",
            demands=secret_demands,
            targets=secret_targets,
            search_action=secret_action,
            player_id="A",
            opponent_id="B",
            discard_candidates=secret_candidates,
            discard_selection=secret_selection,
        )
    )

    arven_under_vileplume = execute_board_derived_trainer_search_transaction(
        arven_state,
        player="A",
        player_board=vileplume_board,
        opponent_board=filler_board,
        restriction_profiles=restriction_profiles,
        lock_state=vileplume_lock,
        profile=arven,
        action_metadata=arven_metadata,
        action_card_class="arven",
        demands=arven_demands,
        targets=arven_targets,
        search_action=arven_action,
        player_id="A",
        opponent_id="B",
    )
    assert arven_under_vileplume.after.budget.supporter_used

    garbodor = make_pokemon(
        "garbodor",
        "Garbodor",
        print_id="xy9-57",
        tags=("Stage1",),
        tool=ToolAttachment("garbodor-tool", "Float Stone"),
    )
    garbodor_board = make_board(garbodor)
    suppressed_lock = initialize_snapshot_lock_state(
        vileplume_board,
        garbodor_board,
    )
    assert suppressed_lock.resolved
    secret_under_garbotoxin = execute_board_derived_trainer_search_transaction(
        secret_state,
        player="A",
        player_board=vileplume_board,
        opponent_board=garbodor_board,
        restriction_profiles=restriction_profiles,
        lock_state=suppressed_lock,
        profile=secret_box,
        action_metadata=secret_metadata,
        action_card_class="secret_box",
        demands=secret_demands,
        targets=secret_targets,
        search_action=secret_action,
        player_id="A",
        opponent_id="B",
        discard_candidates=secret_candidates,
        discard_selection=secret_selection,
    )
    assert secret_under_garbotoxin.after.zones.count("secret_box", "discard") == 1

    hood_vileplume = make_pokemon(
        "vileplume",
        "Vileplume",
        print_id="xy7-3",
        tags=("Stage2",),
        tool=ToolAttachment("hood", "Stealthy Hood"),
    )
    hood_board = make_board(hood_vileplume)
    hood_lock = initialize_snapshot_lock_state(hood_board, garbodor_board)
    assert hood_lock.resolved
    assert _rejected(
        lambda: execute_board_derived_trainer_search_transaction(
            secret_state,
            player="A",
            player_board=hood_board,
            opponent_board=garbodor_board,
            restriction_profiles=restriction_profiles,
            lock_state=hood_lock,
            profile=secret_box,
            action_metadata=secret_metadata,
            action_card_class="secret_box",
            demands=secret_demands,
            targets=secret_targets,
            search_action=secret_action,
            player_id="A",
            opponent_id="B",
            discard_candidates=secret_candidates,
            discard_selection=secret_selection,
        )
    )

    jammed_lock = initialize_snapshot_lock_state(
        hood_board,
        garbodor_board,
        stadium_name="Jamming Tower",
    )
    assert jammed_lock.resolved
    secret_under_jamming = execute_board_derived_trainer_search_transaction(
        secret_state,
        player="A",
        player_board=hood_board,
        opponent_board=garbodor_board,
        restriction_profiles=restriction_profiles,
        lock_state=jammed_lock,
        profile=secret_box,
        action_metadata=secret_metadata,
        action_card_class="secret_box",
        demands=secret_demands,
        targets=secret_targets,
        search_action=secret_action,
        stadium_name="Jamming Tower",
        player_id="A",
        opponent_id="B",
        discard_candidates=secret_candidates,
        discard_selection=secret_selection,
    )
    assert secret_under_jamming.after.zones.count("secret_box", "discard") == 1

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
        lambda: execute_board_derived_trainer_search_transaction(
            arven_state,
            player="A",
            player_board=vileplume_board,
            opponent_board=garbodor_board,
            restriction_profiles=restriction_profiles,
            lock_state=suppressed_lock,
            profile=arven,
            action_metadata=arven_metadata,
            action_card_class="arven",
            demands=arven_demands,
            targets=arven_targets,
            search_action=arven_action,
            player_id="A",
            opponent_id="B",
            attack_windows=(headache_window,),
        )
    )

    print(
        json.dumps(
            {
                "live_vileplume_blocks_secret_box": True,
                "arven_survives_vileplume_item_lock": True,
                "garbotoxin_suppression_reopens_secret_box": True,
                "stealthy_hood_restores_vileplume_lock": True,
                "jamming_tower_reopens_secret_box_via_garbotoxin": True,
                "temporal_headache_still_blocks_arven": True,
                "transaction_consumes_board_and_causal_lock_state_directly": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
