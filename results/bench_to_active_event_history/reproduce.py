from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_to_active_dependency_catalog import (
    build_bench_to_active_dependency_catalog,
    summarize_catalog,
)
from board_object_kernel import knock_out, make_board, make_pokemon, switch_active
from position_event_history import (
    ACTIVE,
    BENCH,
    TurnPositionHistory,
    advance_position_turn,
    derive_position_events,
    moved_bench_to_active_during_last_turn,
    moved_bench_to_active_this_turn,
    record_board_transition,
)
from trigger_deferral_kernel import (
    make_trigger_state,
    record_trigger,
    resolve_next_step,
    start_ready_effect,
)


def main() -> None:
    rows = build_bench_to_active_dependency_catalog(ROOT / "resources")
    summary = summarize_catalog(rows)

    assert summary == {
        "profiles": 44,
        "names": 19,
        "source_kind": {"ability": 22, "attack": 22},
        "dependency_kind": {
            "named_ally_move_ability_trigger": 1,
            "opponent_last_turn_attack_condition": 1,
            "self_move_ability_trigger": 21,
            "self_move_attack_condition": 21,
        },
    }

    ability_names = Counter(
        row.card_name
        for row in rows
        if row.dependency_kind == "self_move_ability_trigger"
    )
    assert ability_names["Iron Valiant ex"] == 6
    assert ability_names["Weavile"] == 2

    actor_before = make_board(
        make_pokemon("lead", "Lead"),
        (
            make_pokemon(
                "valiant",
                "Iron Valiant ex",
                print_id="sv4-89",
            ),
            make_pokemon("pivot", "Pivot"),
        ),
    )
    actor_after = switch_active(actor_before, "valiant")
    assert actor_after is not None

    events = derive_position_events(
        actor_before,
        actor_after,
        turn_player_id="actor",
        board_owner_id="actor",
        turn_index=0,
    )
    assert len(events) == 2
    assert {(row.object_id, row.from_position, row.to_position) for row in events} == {
        ("lead", ACTIVE, BENCH),
        ("valiant", BENCH, ACTIVE),
    }

    history = TurnPositionHistory(current_player="actor")
    history = record_board_transition(
        history,
        board_owner_id="actor",
        before=actor_before,
        after=actor_after,
    )
    assert moved_bench_to_active_this_turn(
        history,
        board_owner_id="actor",
        object_id="valiant",
    )
    assert not moved_bench_to_active_this_turn(
        history,
        board_owner_id="actor",
        object_id="lead",
    )

    # A promotion after Knock Out is still a Bench-to-Active event for the
    # promoted physical object. The removed Active does not create a fake
    # Active-to-Bench event because it left play.
    ko_before = make_board(
        make_pokemon("ko-active", "Victim"),
        (make_pokemon("promote", "Replacement"),),
    )
    ko_result = knock_out(ko_before, "ko-active", promote_object_id="promote")
    assert ko_result is not None
    ko_after, _removed = ko_result
    assert ko_after is not None
    ko_events = derive_position_events(
        ko_before,
        ko_after,
        turn_player_id="actor",
        board_owner_id="actor",
        turn_index=0,
    )
    assert tuple(
        (row.object_id, row.from_position, row.to_position)
        for row in ko_events
    ) == (("promote", BENCH, ACTIVE),)

    # History retains the last completed turn, which is enough for attack text
    # such as Gumshoos's "during your opponent's last turn" condition.
    opp_before = make_board(
        make_pokemon("opp-lead", "Lead"),
        (make_pokemon("opp-pivot", "Pivot"),),
    )
    opp_after = switch_active(opp_before, "opp-pivot")
    assert opp_after is not None
    opp_history = TurnPositionHistory(current_player="opponent")
    opp_history = record_board_transition(
        opp_history,
        board_owner_id="opponent",
        before=opp_before,
        after=opp_after,
    )
    opp_history = advance_position_turn(opp_history, next_player="actor")
    assert moved_bench_to_active_during_last_turn(
        opp_history,
        turn_player_id="opponent",
        board_owner_id="opponent",
        object_id="opp-pivot",
    )

    # A position-triggered Ability created while another effect is resolving
    # can use the existing trigger-deferral scheduler without changing it.
    scheduler = make_trigger_state("switch-effect")
    scheduler = start_ready_effect(
        scheduler,
        effect_id="switch-effect",
        steps=("move", "finish"),
    )
    assert scheduler is not None
    scheduler = record_trigger(
        scheduler,
        effect_id="sv4-89:Tachyon Bits",
    )
    assert scheduler is not None
    assert "sv4-89:Tachyon Bits" in scheduler.deferred_effects

    first = resolve_next_step(scheduler)
    assert first is not None
    _step, scheduler = first
    assert "sv4-89:Tachyon Bits" in scheduler.deferred_effects

    second = resolve_next_step(scheduler)
    assert second is not None
    _step, scheduler = second
    assert "sv4-89:Tachyon Bits" in scheduler.ready_effects

    print("Bench-to-Active event history regression passed")
    print(summary)


if __name__ == "__main__":
    main()
