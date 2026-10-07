"""Reproduce ordinary evolution composed with live lock state."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_causal_state import initialize_snapshot_lock_state
from attack_restriction_turn_windows import create_attack_restriction_window
from attack_source_scoped_restrictions import materialize_attack_restriction
from board_derived_action_permissions import evaluate_board_derived_action_permission
from board_object_kernel import ToolAttachment, make_board, make_pokemon
from card_action_metadata import card_action_metadata_by_id
from evolution_stack_state import PokemonStack, StackCard, make_evolution_state
from identity_materialization import CardInstance, IdentityLedger
from lock_gated_evolution_transaction import execute_lock_gated_evolution
from multicopy_zone_state import ZoneCountState
from source_scoped_action_restrictions import CardActionAttempt
from source_scoped_restriction_activation import build_restriction_activation_profiles
from target_bound_attack_restrictions import (
    begin_target_bound_turn,
    bind_defending_pokemon_window,
)


def _ledger(*rows: CardInstance) -> IdentityLedger:
    return IdentityLedger(
        ZoneCountState.from_mapping({}),
        tuple(sorted(rows, key=lambda row: row.instance_id)),
    )


def _profile(profiles, card_id: str, needle: str):
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


def _bound_window(profile, target_board):
    restriction = materialize_attack_restriction(profile)
    assert restriction is not None
    window = create_attack_restriction_window(
        profile,
        restriction,
        source_player="B",
        other_player="A",
    )
    return begin_target_bound_turn(
        bind_defending_pokemon_window(window, target_board),
        "A",
    )


def main() -> None:
    resources = ROOT / "resources"
    profiles = build_restriction_activation_profiles(resources)
    metadata = card_action_metadata_by_id(resources)

    # Baseline Gloom -> Vileplume physical evolution.
    gloom = make_pokemon(
        "active",
        "Gloom",
        print_id="gloom-print",
        tags=("Grass", "Stage1"),
    )
    opponent = make_pokemon("opponent", "Opponent Basic", tags=("Basic",))
    gloom_board = make_board(gloom)
    opponent_board = make_board(opponent)

    gloom_card = StackCard(
        "gloom-card",
        "Gloom",
        1,
        90,
        "Oddish",
        frozenset({"Grass", "Stage1"}),
        print_id="gloom-print",
    )
    vileplume_card = StackCard(
        "vileplume-card",
        "Vileplume",
        2,
        130,
        "Gloom",
        frozenset({"Grass", "Stage2"}),
        print_id="xy7-3",
    )
    state = make_evolution_state(
        gloom_board,
        (PokemonStack("active", (gloom_card,)),),
    )
    ledger = _ledger(
        CardInstance(
            "gloom-card",
            "gloom-class",
            "Gloom",
            "in_play",
            board_object_id="active",
        ),
        CardInstance("vileplume-card", "vileplume-class", "Vileplume", "hand"),
    )
    lock_state = initialize_snapshot_lock_state(gloom_board, opponent_board)
    assert lock_state.resolved

    success = execute_lock_gated_evolution(
        state,
        ledger,
        "active",
        vileplume_card,
        actor="A",
        player_board=gloom_board,
        opponent_board=opponent_board,
        profiles=profiles,
        lock_state=lock_state,
        action_metadata=metadata["xy7-3"],
        player_id="A",
        opponent_id="B",
    )
    assert success.permission.allowed
    assert success.transition is not None
    evolved_board = success.transition.state.board
    evolved = evolved_board.get("active")
    assert evolved.card_name == "Vileplume"
    assert evolved.print_id == "xy7-3"

    subsequent_item = evaluate_board_derived_action_permission(
        CardActionAttempt("item", "hand"),
        player="A",
        player_board=evolved_board,
        opponent_board=opponent_board,
        profiles=profiles,
        lock_state=success.lock_state,
        player_id="A",
        opponent_id="B",
    )
    assert not subsequent_item.allowed
    assert {row.card_id for row in subsequent_item.blocking_restrictions} == {
        "xy7-3"
    }

    # A physically bound Time Freeze must stop the evolution before mutation.
    time_freeze = _profile(profiles, "xyp-XY77", "Time Freeze")
    time_bound = _bound_window(time_freeze, gloom_board)
    blocked = execute_lock_gated_evolution(
        state,
        ledger,
        "active",
        vileplume_card,
        actor="A",
        player_board=gloom_board,
        opponent_board=opponent_board,
        profiles=profiles,
        lock_state=lock_state,
        action_metadata=metadata["xy7-3"],
        player_id="A",
        opponent_id="B",
        target_bound_attack_windows=(time_bound,),
    )
    assert not blocked.permission.allowed
    assert blocked.transition is None
    assert blocked.lock_state == lock_state
    assert blocked.target_bound_windows == (time_bound,)

    # Trubbish -> Garbodor with an attached Tool changes Ability topology.
    float_stone = ToolAttachment("garb-tool", "Float Stone")
    trubbish = make_pokemon(
        "garb-line",
        "Trubbish",
        print_id="trubbish-print",
        tags=("Psychic", "Basic"),
        tool=float_stone,
    )
    trubbish_board = make_board(trubbish)
    opposing_vileplume = make_pokemon(
        "opp-vileplume",
        "Vileplume",
        print_id="xy7-3",
        tags=("Grass", "Stage2"),
    )
    vileplume_board = make_board(opposing_vileplume)

    trubbish_card = StackCard(
        "trubbish-card",
        "Trubbish",
        0,
        70,
        tags=frozenset({"Psychic", "Basic"}),
        print_id="trubbish-print",
    )
    garbodor_card = StackCard(
        "garbodor-card",
        "Garbodor",
        1,
        100,
        "Trubbish",
        frozenset({"Psychic", "Stage1"}),
        print_id="xy9-57",
    )
    garb_state = make_evolution_state(
        trubbish_board,
        (PokemonStack("garb-line", (trubbish_card,)),),
    )
    garb_ledger = _ledger(
        CardInstance(
            "trubbish-card",
            "trubbish-class",
            "Trubbish",
            "in_play",
            board_object_id="garb-line",
        ),
        CardInstance(
            "garb-tool",
            "tool-class",
            "Float Stone",
            "attached",
            attached_to="garb-line",
        ),
        CardInstance("garbodor-card", "garbodor-class", "Garbodor", "hand"),
    )
    pre_garb_lock = initialize_snapshot_lock_state(
        trubbish_board,
        vileplume_board,
    )
    assert pre_garb_lock.resolved

    item_before = evaluate_board_derived_action_permission(
        CardActionAttempt("item", "hand"),
        player="B",
        player_board=trubbish_board,
        opponent_board=vileplume_board,
        profiles=profiles,
        lock_state=pre_garb_lock,
        player_id="A",
        opponent_id="B",
    )
    assert not item_before.allowed

    garb_result = execute_lock_gated_evolution(
        garb_state,
        garb_ledger,
        "garb-line",
        garbodor_card,
        actor="A",
        player_board=trubbish_board,
        opponent_board=vileplume_board,
        profiles=profiles,
        lock_state=pre_garb_lock,
        action_metadata=metadata["xy9-57"],
        player_id="A",
        opponent_id="B",
    )
    assert garb_result.permission.allowed
    assert garb_result.transition is not None
    garbodor_board = garb_result.transition.state.board
    garbodor = garbodor_board.get("garb-line")
    assert garbodor.print_id == "xy9-57"
    assert garbodor.tool == float_stone
    assert garb_result.lock_state.resolved
    assert "opp-vileplume" in (
        garb_result.lock_state.resolution.opponent_suppressed_object_ids or ()
    )

    item_after = evaluate_board_derived_action_permission(
        CardActionAttempt("item", "hand"),
        player="B",
        player_board=garbodor_board,
        opponent_board=vileplume_board,
        profiles=profiles,
        lock_state=garb_result.lock_state,
        player_id="A",
        opponent_id="B",
    )
    assert item_after.allowed

    print(
        json.dumps(
            {
                "ordinary_evolution_updates_exact_print": True,
                "new_vileplume_immediately_blocks_followup_item": True,
                "bound_time_freeze_blocks_before_mutation": True,
                "garbodor_evolution_preserves_tool": True,
                "causal_ability_state_advances_after_evolution": True,
                "garbotoxin_suppresses_opposing_vileplume": True,
                "item_permission_reopens_after_suppression": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
