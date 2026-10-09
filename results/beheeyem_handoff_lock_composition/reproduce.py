"""Compose Beheeyem's persistent Item lock with promoted Active lock sources."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ability_lock_causal_state import initialize_snapshot_lock_state
from attack_restriction_turn_windows import (
    begin_turn,
    create_attack_restriction_window,
    end_turn,
)
from attack_source_scoped_restrictions import materialize_attack_restriction
from board_derived_action_permissions import evaluate_board_derived_action_permission
from board_object_kernel import make_board, make_pokemon, switch_active
from source_scoped_action_restrictions import CardActionAttempt
from source_scoped_restriction_activation import build_restriction_activation_profiles


def one(profiles, card_id: str, needle: str):
    rows = [
        row for row in profiles
        if row.restriction.card_id == card_id
        and (needle in row.restriction.source or needle in row.restriction.text)
    ]
    assert len(rows) == 1, (card_id, needle, len(rows))
    return rows[0]


def query(
    attempt: CardActionAttempt,
    *,
    actor: str,
    a_board,
    b_board,
    profiles,
    window=None,
) -> bool:
    lock = initialize_snapshot_lock_state(a_board, b_board)
    assert lock.resolved
    answer = evaluate_board_derived_action_permission(
        attempt,
        player=actor,
        player_board=a_board,
        opponent_board=b_board,
        profiles=profiles,
        lock_state=lock,
        player_id="A",
        opponent_id="B",
        attack_windows=(window,) if window is not None else (),
    )
    return answer.allowed


def main() -> None:
    profiles = build_restriction_activation_profiles(ROOT / "resources")
    beheeyem = one(profiles, "sm11-91", "Mysterious Noise")
    assert beheeyem.activation_family == "attack_applied"
    assert beheeyem.duration_family == "opponent_next_turn"
    assert beheeyem.restriction.dimensions == frozenset({"item"})

    applied = materialize_attack_restriction(beheeyem)
    assert applied is not None
    waiting = create_attack_restriction_window(
        beheeyem, applied, source_player="A", other_player="B"
    )
    active_window = begin_turn(waiting, "B")

    standby = make_pokemon("a-standby", "Elgyem", print_id="sm11-90")
    enemy = make_board(make_pokemon("b-active", "Opponent Basic"))

    def a_board_for(name: str, card_id: str):
        return make_board(
            make_pokemon("a-anchor", name, print_id=card_id),
            (standby,),
        )

    stoutland_board = a_board_for("Stoutland", "bw7-122")
    assert not query(
        CardActionAttempt("item", "hand"),
        actor="B", a_board=stoutland_board, b_board=enemy,
        profiles=profiles, window=active_window,
    )
    assert not query(
        CardActionAttempt("supporter", "hand"),
        actor="B", a_board=stoutland_board, b_board=enemy,
        profiles=profiles, window=active_window,
    )
    assert query(
        CardActionAttempt("tool", "hand", mode="attach"),
        actor="B", a_board=stoutland_board, b_board=enemy,
        profiles=profiles, window=active_window,
    )
    assert query(
        CardActionAttempt("item", "prize_pending"),
        actor="B", a_board=stoutland_board, b_board=enemy,
        profiles=profiles, window=active_window,
    )

    honchkrow_board = a_board_for("Honchkrow-GX", "sm10-109")
    expected_denied = (
        CardActionAttempt("item", "hand"),
        CardActionAttempt("tool", "hand", mode="attach"),
        CardActionAttempt("stadium", "hand"),
        CardActionAttempt("special_energy", "hand", mode="attach"),
    )
    for attempt in expected_denied:
        assert not query(
            attempt,
            actor="B", a_board=honchkrow_board, b_board=enemy,
            profiles=profiles, window=active_window,
        ), attempt
    assert query(
        CardActionAttempt("supporter", "hand"),
        actor="B", a_board=honchkrow_board, b_board=enemy,
        profiles=profiles, window=active_window,
    )
    assert query(
        CardActionAttempt("basic_energy", "hand", mode="attach"),
        actor="B", a_board=honchkrow_board, b_board=enemy,
        profiles=profiles, window=active_window,
    )

    # The Mysterious Noise Item effect remains next turn even after source gone.
    expired_window = end_turn(active_window, "B")
    assert query(
        CardActionAttempt("item", "hand"),
        actor="B", a_board=stoutland_board, b_board=enemy,
        profiles=profiles, window=expired_window,
    )
    assert not query(
        CardActionAttempt("supporter", "hand"),
        actor="B", a_board=stoutland_board, b_board=enemy,
        profiles=profiles, window=expired_window,
    )
    stoutland_benched = switch_active(stoutland_board, "a-standby")
    assert stoutland_benched is not None
    assert query(
        CardActionAttempt("supporter", "hand"),
        actor="B", a_board=stoutland_benched, b_board=enemy,
        profiles=profiles, window=expired_window,
    )

    # Opposing Vileplume would lock Items for both players. With Weezing
    # promoted Active its Ability is suppressed, while Beheeyem's Item
    # restriction on the opposing player persists as an attack effect.
    vileplume = make_pokemon("b-vileplume", "Vileplume", print_id="xy7-3")
    enemy_vileplume = make_board(
        make_pokemon("b-active", "Opponent Basic"),
        (vileplume,),
    )
    without_weezing = a_board_for("Filler", "none")
    item = CardActionAttempt("item", "hand")
    assert not query(
        item, actor="A", a_board=without_weezing,
        b_board=enemy_vileplume, profiles=profiles,
    )
    weezing_board = a_board_for("Galarian Weezing", "swsh2-113")
    assert query(
        item, actor="A", a_board=weezing_board,
        b_board=enemy_vileplume, profiles=profiles, window=active_window,
    )
    assert not query(
        item, actor="B", a_board=weezing_board,
        b_board=enemy_vileplume, profiles=profiles, window=active_window,
    )
    assert query(
        item, actor="B", a_board=weezing_board,
        b_board=enemy_vileplume, profiles=profiles, window=expired_window,
    )
    weezing_benched = switch_active(weezing_board, "a-standby")
    assert weezing_benched is not None
    assert not query(
        item, actor="A", a_board=weezing_benched,
        b_board=enemy_vileplume, profiles=profiles, window=expired_window,
    )

    print(json.dumps(
        {
            "beheeyem_applied_item_lock_survives_source_departure": True,
            "stoutland_adds_active_supporter_lock": True,
            "honchkrow_adds_tool_stadium_special_energy_lock": True,
            "prize_origin_item_play_remains_available": True,
            "attack_item_lock_expires_but_active_stoutland_lock_remains": True,
            "benched_stoutland_no_longer_locks_supporters": True,
            "weezing_suppresses_opposing_symmetric_vileplume_item_lock": True,
            "weezing_plus_mysterious_noise_gives_asymmetric_item_lock": True,
            "post_window_weezing_lifts_item_lock_on_both_players": True,
            "weezing_leaving_active_reinstates_vileplume_item_lock": True,
        },
        indent=2, sort_keys=True,
    ))


if __name__ == "__main__":
    main()
