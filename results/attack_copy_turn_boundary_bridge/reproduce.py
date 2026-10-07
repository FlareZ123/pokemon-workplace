from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef,
    CopySelector,
    PokemonRef,
    State,
    TurnBoundaryEffect,
    choose_exact,
    resolve_attack,
)
from attack_copy_turn_boundary_bridge import close_declared_attack
from canonical_turn_sequence_owner import TurnScheduleState, advance_turn
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state

HAUGHTY = "persian:haughty-order"
TIMELESS = "dialga:timeless-gx"
PLAIN = "plain:attack"

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
        effect_label="take_another_turn",
        turn_boundary_effect=TurnBoundaryEffect(
            take_another_turn=True,
            skip_pokemon_checkup=True,
        ),
    ),
    PLAIN: AttackDef(PLAIN, "Plain Attack", effect_label="plain_body"),
}


def test_copied_timeless_defers_boundary_until_outer_continuation() -> None:
    copy_state = State(
        pokemon=(
            PokemonRef(
                "p2-dialga-revealed",
                "Dialga-GX",
                "P2",
                "revealed",
                attacks=(TIMELESS,),
            ),
        )
    )
    resolution = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=ATTACKS,
        state=copy_state,
        choose=choose_exact((TIMELESS,)),
    )

    assert resolution.body_chain == (HAUGHTY, TIMELESS)
    assert resolution.state.events == (
        "reveal_top_10",
        "take_another_turn",
        "shuffle_revealed",
    )
    assert resolution.state.pending_turn_boundary == TurnBoundaryEffect(
        take_another_turn=True,
        skip_pokemon_checkup=True,
    )

    schedule = TurnScheduleState("P1", "P2")
    p1 = make_state({}, turn_budget=TurnActionBudget())
    p2 = make_state({}, turn_budget=TurnActionBudget())

    closed = close_declared_attack(schedule, p1, resolution)
    assert closed is not None
    closed_schedule, p1_closed = closed
    assert p1_closed.turn_budget is not None
    assert p1_closed.turn_budget.turn_ended

    advanced = advance_turn(closed_schedule, p1_closed, p2)
    assert advanced is not None
    assert advanced.same_player_continues
    assert advanced.schedule.current_player == "P1"
    assert not advanced.pokemon_checkup_occurs
    assert advanced.current_state.turn_budget is not None
    assert not advanced.current_state.turn_budget.turn_ended


def test_copy_without_boundary_hands_turn_to_opponent() -> None:
    copy_state = State(
        pokemon=(
            PokemonRef(
                "p2-plain-revealed",
                "Plain Pokémon",
                "P2",
                "revealed",
                attacks=(PLAIN,),
            ),
        )
    )
    resolution = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=ATTACKS,
        state=copy_state,
        choose=choose_exact((PLAIN,)),
    )
    assert resolution.state.pending_turn_boundary is None
    assert resolution.state.events == (
        "reveal_top_10",
        "plain_body",
        "shuffle_revealed",
    )

    schedule = TurnScheduleState("P1", "P2")
    p1 = make_state({}, turn_budget=TurnActionBudget())
    p2 = make_state({}, turn_budget=TurnActionBudget())

    closed = close_declared_attack(schedule, p1, resolution)
    assert closed is not None
    closed_schedule, p1_closed = closed
    advanced = advance_turn(closed_schedule, p1_closed, p2)
    assert advanced is not None
    assert not advanced.same_player_continues
    assert advanced.schedule.current_player == "P2"
    assert advanced.pokemon_checkup_occurs


def main() -> None:
    test_copied_timeless_defers_boundary_until_outer_continuation()
    test_copy_without_boundary_hands_turn_to_opponent()
    print("attack-copy turn-boundary bridge regression: PASS")


if __name__ == "__main__":
    main()
