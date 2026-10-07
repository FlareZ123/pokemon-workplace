"""Reproduce physical target lifetimes for Defending-Pokemon restrictions."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_restriction_turn_windows import create_attack_restriction_window
from attack_source_scoped_restrictions import materialize_attack_restriction
from board_object_kernel import evolve, make_board, make_pokemon, switch_active
from source_scoped_action_restrictions import CardActionAttempt
from source_scoped_restriction_activation import build_restriction_activation_profiles
from target_bound_attack_restrictions import (
    advance_target_binding,
    begin_target_bound_turn,
    bind_defending_pokemon_window,
    target_bound_restriction_blocks_attempt,
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
    bound = bind_defending_pokemon_window(window, target_board)
    return begin_target_bound_turn(bound, "A")


def main() -> None:
    profiles = build_restriction_activation_profiles(ROOT / "resources")

    target = make_pokemon(
        "target",
        "Target Basic",
        print_id="target-basic",
        tags=("Basic",),
    )
    pivot = make_pokemon(
        "pivot",
        "Pivot Basic",
        print_id="pivot-basic",
        tags=("Basic",),
    )
    target_board = make_board(target, (pivot,))

    time_freeze = _profile(profiles, "xyp-XY77", "Time Freeze")
    time_bound = _bound_window(time_freeze, target_board)

    evolve_attempt = CardActionAttempt(
        "pokemon",
        "hand",
        mode="evolve",
    )
    assert target_bound_restriction_blocks_attempt(
        time_bound,
        player="A",
        attempt=evolve_attempt,
        target_object_id="target",
    )
    assert not target_bound_restriction_blocks_attempt(
        time_bound,
        player="A",
        attempt=evolve_attempt,
        target_object_id="pivot",
    )

    switched = switch_active(target_board, "pivot")
    assert switched is not None
    after_switch = advance_target_binding(time_bound, target_board, switched)
    assert not after_switch.target_effect_live
    assert not target_bound_restriction_blocks_attempt(
        after_switch,
        player="A",
        attempt=evolve_attempt,
        target_object_id="target",
    )

    switched_back = switch_active(switched, "target")
    assert switched_back is not None
    after_return = advance_target_binding(after_switch, switched, switched_back)
    assert not after_return.target_effect_live
    assert not target_bound_restriction_blocks_attempt(
        after_return,
        player="A",
        attempt=evolve_attempt,
        target_object_id="target",
    )

    fresh_time_bound = _bound_window(time_freeze, target_board)
    evolved = evolve(
        target_board,
        "target",
        new_card_name="Target Evolution",
        new_tags=("Stage1",),
    )
    assert evolved is not None
    after_evolution = advance_target_binding(
        fresh_time_bound,
        target_board,
        evolved,
    )
    assert not after_evolution.target_effect_live
    assert not target_bound_restriction_blocks_attempt(
        after_evolution,
        player="A",
        attempt=evolve_attempt,
        target_object_id="target",
    )

    cross_slicer = _profile(profiles, "xyp-XY75", "Cross Slicer")
    cross_bound = _bound_window(cross_slicer, target_board)
    attach_attempt = CardActionAttempt(
        "basic_energy",
        "hand",
        mode="attach",
    )
    assert target_bound_restriction_blocks_attempt(
        cross_bound,
        player="A",
        attempt=attach_attempt,
        target_object_id="target",
    )
    assert not target_bound_restriction_blocks_attempt(
        cross_bound,
        player="A",
        attempt=attach_attempt,
        target_object_id="pivot",
    )

    discard_attach = CardActionAttempt(
        "basic_energy",
        "discard",
        mode="attach",
    )
    assert not target_bound_restriction_blocks_attempt(
        cross_bound,
        player="A",
        attempt=discard_attach,
        target_object_id="target",
    )

    assert not target_bound_restriction_blocks_attempt(
        cross_bound,
        player="B",
        attempt=attach_attempt,
        target_object_id="target",
    )

    print(
        json.dumps(
            {
                "time_freeze_bound_to_original_defending_object": True,
                "different_target_remains_legal": True,
                "switch_to_bench_clears_effect": True,
                "switch_back_does_not_restore_effect": True,
                "evolution_clears_effect": True,
                "cross_slicer_uses_physical_target_identity": True,
                "non_hand_attachment_remains_legal": True,
                "source_player_not_affected": True,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
