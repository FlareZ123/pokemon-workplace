from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_damage_bridge import (
    BoardEventProgram,
    close_copy_attack_if_no_knockouts,
    replay_copy_attack_board,
)
from attack_copy_kernel import (
    AttackDef,
    CopySelector,
    PokemonRef,
    State,
    TurnBoundaryEffect,
    choose_exact,
    resolve_attack,
)
from board_object_kernel import make_board, make_pokemon
from canonical_turn_sequence_owner import TurnScheduleState, advance_turn
from damage_board_bridge import EffectCounterPlacement
from damage_calculation_kernel import AttackDamage, DamageContext
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state

HAUGHTY = "persian:haughty-order"
TIMELESS = "dialga:timeless-gx"
PHANTOM = "dragapult:phantom-dive"

TIMELESS_EVENT = "body:timeless-gx"
PHANTOM_EVENT = "body:phantom-dive"

ATTACKS = {
    HAUGHTY: AttackDef(
        HAUGHTY,
        "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    ),
    TIMELESS: AttackDef(
        TIMELESS,
        "Timeless-GX",
        is_gx=True,
        effect_label=TIMELESS_EVENT,
        turn_boundary_effect=TurnBoundaryEffect(
            take_another_turn=True,
            skip_pokemon_checkup=True,
        ),
    ),
    PHANTOM: AttackDef(
        PHANTOM,
        "Phantom Dive",
        effect_label=PHANTOM_EVENT,
    ),
}


def copy_resolution(selected_attack: str) -> object:
    return resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=ATTACKS,
        state=State(
            pokemon=(
                PokemonRef(
                    "p2-revealed-source",
                    "Revealed source",
                    "P2",
                    "revealed",
                    attacks=(selected_attack,),
                ),
            )
        ),
        choose=choose_exact((selected_attack,)),
    )


def fresh_turn_state():
    return make_state({}, turn_budget=TurnActionBudget())


def test_timeless_knockout_blocks_extra_turn_handoff() -> None:
    resolution = copy_resolution(TIMELESS)
    assert resolution.state.events == (
        "reveal_top_10",
        TIMELESS_EVENT,
        "shuffle_revealed",
    )

    board = make_board(
        make_pokemon("active", "150 HP Active"),
        (make_pokemon("bench", "Bench survivor"),),
    )
    replay = replay_copy_attack_board(
        resolution,
        board,
        event_programs={
            TIMELESS_EVENT: BoardEventProgram(
                "active",
                DamageContext(attack=AttackDamage(150)),
            )
        },
        hp_by_object_id={"active": 150, "bench": 100},
    )

    assert replay.board.get("active").damage_counters == 15
    assert tuple(step.event for step in replay.event_trace) == (
        "reveal_top_10",
        TIMELESS_EVENT,
        "shuffle_revealed",
    )
    assert replay.event_trace[1].damage_counters == (
        ("active", 15),
        ("bench", 0),
    )
    assert replay.event_trace[2].damage_counters == (
        ("active", 15),
        ("bench", 0),
    )
    assert replay.knocked_out_ids == ("active",)
    assert resolution.state.pending_turn_boundary is not None

    blocked = close_copy_attack_if_no_knockouts(
        TurnScheduleState("P1", "P2"),
        fresh_turn_state(),
        replay,
    )
    assert blocked is None


def test_timeless_without_knockout_can_reach_extra_turn_scheduler() -> None:
    resolution = copy_resolution(TIMELESS)
    board = make_board(
        make_pokemon("active", "200 HP Active"),
        (make_pokemon("bench", "Bench survivor"),),
    )
    replay = replay_copy_attack_board(
        resolution,
        board,
        event_programs={
            TIMELESS_EVENT: BoardEventProgram(
                "active",
                DamageContext(attack=AttackDamage(150)),
            )
        },
        hp_by_object_id={"active": 200, "bench": 100},
    )
    assert replay.knocked_out_ids == ()

    closed = close_copy_attack_if_no_knockouts(
        TurnScheduleState("P1", "P2"),
        fresh_turn_state(),
        replay,
    )
    assert closed is not None
    schedule, p1_closed = closed
    advanced = advance_turn(schedule, p1_closed, fresh_turn_state())
    assert advanced is not None
    assert advanced.same_player_continues
    assert advanced.schedule.current_player == "P1"
    assert not advanced.pokemon_checkup_occurs


def test_phantom_double_knockout_waits_until_outer_cleanup_finishes() -> None:
    resolution = copy_resolution(PHANTOM)
    board = make_board(
        make_pokemon("active", "200 HP Active"),
        (make_pokemon("bench60", "60 HP Bench"),),
    )
    replay = replay_copy_attack_board(
        resolution,
        board,
        event_programs={
            PHANTOM_EVENT: BoardEventProgram(
                "active",
                DamageContext(attack=AttackDamage(200)),
                (EffectCounterPlacement("bench60", 6),),
            )
        },
        hp_by_object_id={"active": 200, "bench60": 60},
    )

    assert tuple(step.event for step in replay.event_trace) == (
        "reveal_top_10",
        PHANTOM_EVENT,
        "shuffle_revealed",
    )
    assert replay.event_trace[0].damage_counters == (
        ("active", 0),
        ("bench60", 0),
    )
    assert replay.event_trace[1].damage_counters == (
        ("active", 20),
        ("bench60", 6),
    )
    assert replay.event_trace[2].damage_counters == (
        ("active", 20),
        ("bench60", 6),
    )
    assert replay.knocked_out_ids == ("active", "bench60")

    blocked = close_copy_attack_if_no_knockouts(
        TurnScheduleState("P1", "P2"),
        fresh_turn_state(),
        replay,
    )
    assert blocked is None


def main() -> None:
    test_timeless_knockout_blocks_extra_turn_handoff()
    test_timeless_without_knockout_can_reach_extra_turn_scheduler()
    test_phantom_double_knockout_waits_until_outer_cleanup_finishes()
    print("attack-copy damage phase bridge regression: PASS")


if __name__ == "__main__":
    main()
