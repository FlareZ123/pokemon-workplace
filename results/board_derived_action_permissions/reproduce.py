"""Reproduce exact action permission queries from canonical lock state."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_causal_state import initialize_snapshot_lock_state
from attack_restriction_turn_windows import begin_turn, create_attack_restriction_window
from attack_source_scoped_restrictions import materialize_attack_restriction
from board_derived_action_permissions import evaluate_board_derived_action_permission
from board_object_kernel import make_board, make_pokemon
from source_scoped_action_restrictions import CardActionAttempt
from source_scoped_restriction_activation import build_restriction_activation_profiles


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


def _window(profile, *, source_player="B", other_player="A"):
    restriction = materialize_attack_restriction(profile)
    assert restriction is not None
    window = create_attack_restriction_window(
        profile,
        restriction,
        source_player=source_player,
        other_player=other_player,
    )
    return begin_turn(window, other_player)


def main() -> None:
    profiles = build_restriction_activation_profiles(ROOT / "resources")

    filler_a = make_pokemon("a-active", "A Active")
    filler_b = make_pokemon("b-active", "B Active")
    base_a = make_board(filler_a)
    base_b = make_board(filler_b)
    base_lock = initialize_snapshot_lock_state(base_a, base_b)
    assert base_lock.resolved

    ordinary_item = CardActionAttempt("item", "hand")
    baseline = evaluate_board_derived_action_permission(
        ordinary_item,
        player="A",
        player_board=base_a,
        opponent_board=base_b,
        profiles=profiles,
        lock_state=base_lock,
        player_id="A",
        opponent_id="B",
    )
    assert baseline.allowed
    assert not baseline.blocking_restrictions

    vileplume = make_pokemon(
        "vileplume",
        "Vileplume",
        print_id="xy7-3",
        tags=("Stage2",),
    )
    vileplume_board = make_board(vileplume)
    vileplume_lock = initialize_snapshot_lock_state(vileplume_board, base_b)
    assert vileplume_lock.resolved

    hand_item = evaluate_board_derived_action_permission(
        CardActionAttempt("item", "hand"),
        player="A",
        player_board=vileplume_board,
        opponent_board=base_b,
        profiles=profiles,
        lock_state=vileplume_lock,
        player_id="A",
        opponent_id="B",
    )
    assert not hand_item.allowed
    assert {row.card_id for row in hand_item.blocking_restrictions} == {"xy7-3"}

    prize_item = evaluate_board_derived_action_permission(
        CardActionAttempt("item", "prize_pending"),
        player="A",
        player_board=vileplume_board,
        opponent_board=base_b,
        profiles=profiles,
        lock_state=vileplume_lock,
        player_id="A",
        opponent_id="B",
    )
    assert prize_item.allowed

    arbok = make_pokemon(
        "arbok",
        "Team Rocket's Arbok",
        print_id="sv10-113",
        tags=("Stage1",),
    )
    arbok_board = make_board(arbok)
    arbok_lock = initialize_snapshot_lock_state(base_a, arbok_board)
    assert arbok_lock.resolved

    ability_pokemon = evaluate_board_derived_action_permission(
        CardActionAttempt(
            "pokemon",
            "hand",
            card_tags=frozenset({"has_ability"}),
        ),
        player="A",
        player_board=base_a,
        opponent_board=arbok_board,
        profiles=profiles,
        lock_state=arbok_lock,
        player_id="A",
        opponent_id="B",
    )
    assert not ability_pokemon.allowed
    assert {row.card_id for row in ability_pokemon.blocking_restrictions} == {
        "sv10-113"
    }

    rocket_ability_pokemon = evaluate_board_derived_action_permission(
        CardActionAttempt(
            "pokemon",
            "hand",
            card_tags=frozenset({"has_ability", "team_rocket"}),
        ),
        player="A",
        player_board=base_a,
        opponent_board=arbok_board,
        profiles=profiles,
        lock_state=arbok_lock,
        player_id="A",
        opponent_id="B",
    )
    assert rocket_ability_pokemon.allowed

    no_ability_pokemon = evaluate_board_derived_action_permission(
        CardActionAttempt("pokemon", "hand"),
        player="A",
        player_board=base_a,
        opponent_board=arbok_board,
        profiles=profiles,
        lock_state=arbok_lock,
        player_id="A",
        opponent_id="B",
    )
    assert no_ability_pokemon.allowed

    time_freeze = _profile(profiles, "xyp-XY77", "Time Freeze")
    time_freeze_window = _window(time_freeze)

    defending_evolution = evaluate_board_derived_action_permission(
        CardActionAttempt(
            "pokemon",
            "hand",
            mode="evolve",
            target_relation="defending_pokemon",
        ),
        player="A",
        player_board=base_a,
        opponent_board=base_b,
        profiles=profiles,
        lock_state=base_lock,
        player_id="A",
        opponent_id="B",
        attack_windows=(time_freeze_window,),
    )
    assert not defending_evolution.allowed
    assert {row.card_id for row in defending_evolution.blocking_restrictions} == {
        "xyp-XY77"
    }

    other_evolution = evaluate_board_derived_action_permission(
        CardActionAttempt(
            "pokemon",
            "hand",
            mode="evolve",
            target_relation="other_pokemon",
        ),
        player="A",
        player_board=base_a,
        opponent_board=base_b,
        profiles=profiles,
        lock_state=base_lock,
        player_id="A",
        opponent_id="B",
        attack_windows=(time_freeze_window,),
    )
    assert other_evolution.allowed

    basic_play = evaluate_board_derived_action_permission(
        CardActionAttempt(
            "pokemon",
            "hand",
            mode="play",
            target_relation="defending_pokemon",
        ),
        player="A",
        player_board=base_a,
        opponent_board=base_b,
        profiles=profiles,
        lock_state=base_lock,
        player_id="A",
        opponent_id="B",
        attack_windows=(time_freeze_window,),
    )
    assert basic_play.allowed

    cross_slicer = _profile(profiles, "xyp-XY75", "Cross Slicer")
    cross_slicer_window = _window(cross_slicer)

    defending_energy = evaluate_board_derived_action_permission(
        CardActionAttempt(
            "basic_energy",
            "hand",
            mode="attach",
            target_relation="defending_pokemon",
        ),
        player="A",
        player_board=base_a,
        opponent_board=base_b,
        profiles=profiles,
        lock_state=base_lock,
        player_id="A",
        opponent_id="B",
        attack_windows=(cross_slicer_window,),
    )
    assert not defending_energy.allowed
    assert {row.card_id for row in defending_energy.blocking_restrictions} == {
        "xyp-XY75"
    }

    other_energy = evaluate_board_derived_action_permission(
        CardActionAttempt(
            "basic_energy",
            "hand",
            mode="attach",
            target_relation="other_pokemon",
        ),
        player="A",
        player_board=base_a,
        opponent_board=base_b,
        profiles=profiles,
        lock_state=base_lock,
        player_id="A",
        opponent_id="B",
        attack_windows=(cross_slicer_window,),
    )
    assert other_energy.allowed

    discard_energy = evaluate_board_derived_action_permission(
        CardActionAttempt(
            "basic_energy",
            "discard",
            mode="attach",
            target_relation="defending_pokemon",
        ),
        player="A",
        player_board=base_a,
        opponent_board=base_b,
        profiles=profiles,
        lock_state=base_lock,
        player_id="A",
        opponent_id="B",
        attack_windows=(cross_slicer_window,),
    )
    assert discard_energy.allowed

    print(
        json.dumps(
            {
                "baseline_item_allowed": True,
                "vileplume_blocks_hand_item": True,
                "prize_origin_item_preserved": True,
                "potent_glare_blocks_ability_pokemon": True,
                "team_rocket_exception_preserved": True,
                "no_ability_pokemon_preserved": True,
                "time_freeze_blocks_only_defending_evolution": True,
                "cross_slicer_blocks_only_hand_energy_to_defending": True,
                "direct_predicate_matches_hybrid_projection": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
