from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_damage_bridge import BoardEventProgram, replay_copy_attack_board
from attack_copy_kernel import (
    AttackDef,
    CopySelector,
    PokemonRef,
    State,
    TurnBoundaryEffect,
    choose_exact,
    resolve_attack,
)
from attack_copy_reaction_bridge import (
    close_copy_attack_after_reactions_if_no_knockouts,
    resolve_copy_damage_reactions,
)
from board_object_kernel import make_board, make_pokemon
from canonical_turn_sequence_owner import TurnScheduleState, advance_turn
from damage_calculation_kernel import AttackDamage, DamageContext
from damage_reaction_kernel import DamageReaction, DamageReactionKind
from turn_action_budget import TurnActionBudget
from unified_state_kernel import make_state

HAUGHTY = "persian:haughty-order"
TIMELESS = "dialga:timeless-gx"
TIMELESS_EVENT = "body:timeless-gx"

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
}


def timeless_resolution():
    return resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=ATTACKS,
        state=State(
            pokemon=(
                PokemonRef(
                    "p2-dialga-revealed",
                    "Dialga-GX",
                    "P2",
                    "revealed",
                    attacks=(TIMELESS,),
                ),
            )
        ),
        choose=choose_exact((TIMELESS,)),
    )


def fresh_turn_state():
    return make_state({}, turn_budget=TurnActionBudget())


def test_reflected_damage_creates_cross_side_ko_barrier() -> None:
    resolution = timeless_resolution()
    defender = make_board(make_pokemon("defender", "Strong Bash defender"))
    board_resolution = replay_copy_attack_board(
        resolution,
        defender,
        event_programs={
            TIMELESS_EVENT: BoardEventProgram(
                "defender",
                DamageContext(attack=AttackDamage(150)),
            )
        },
        hp_by_object_id={"defender": 130},
    )
    assert tuple(step.event for step in board_resolution.event_trace) == (
        "reveal_top_10",
        TIMELESS_EVENT,
        "shuffle_revealed",
    )
    assert board_resolution.knocked_out_ids == ("defender",)

    attacker = make_board(make_pokemon("attacker", "Haughty Order attacker"))
    reacted = resolve_copy_damage_reactions(
        board_resolution,
        attacker,
        body_event=TIMELESS_EVENT,
        reactions=(
            DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),
        ),
        attacker_hp_by_object_id={"attacker": 150},
        defender_hp_by_object_id={"defender": 130},
    )

    assert reacted.reaction_result.triggered
    assert reacted.reaction_result.counters_placed_on_attacker == 15
    assert reacted.reaction_result.attacker_knocked_out_ids == ("attacker",)
    assert reacted.reaction_result.defender_knocked_out_ids == ("defender",)

    blocked = close_copy_attack_after_reactions_if_no_knockouts(
        TurnScheduleState("P1", "P2"),
        fresh_turn_state(),
        reacted,
    )
    assert blocked is None


def test_surviving_reaction_state_can_reach_extra_turn_scheduler() -> None:
    resolution = timeless_resolution()
    defender = make_board(make_pokemon("defender", "Strong Bash defender"))
    board_resolution = replay_copy_attack_board(
        resolution,
        defender,
        event_programs={
            TIMELESS_EVENT: BoardEventProgram(
                "defender",
                DamageContext(attack=AttackDamage(150)),
            )
        },
        hp_by_object_id={"defender": 200},
    )
    assert board_resolution.knocked_out_ids == ()

    attacker = make_board(make_pokemon("attacker", "Haughty Order attacker"))
    reacted = resolve_copy_damage_reactions(
        board_resolution,
        attacker,
        body_event=TIMELESS_EVENT,
        reactions=(
            DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),
        ),
        attacker_hp_by_object_id={"attacker": 160},
        defender_hp_by_object_id={"defender": 200},
    )
    assert reacted.reaction_result.attacker_knocked_out_ids == ()
    assert reacted.reaction_result.defender_knocked_out_ids == ()
    assert reacted.reaction_result.attacker_board.get("attacker").damage_counters == 15

    closed = close_copy_attack_after_reactions_if_no_knockouts(
        TurnScheduleState("P1", "P2"),
        fresh_turn_state(),
        reacted,
    )
    assert closed is not None
    schedule, p1_closed = closed
    advanced = advance_turn(schedule, p1_closed, fresh_turn_state())
    assert advanced is not None
    assert advanced.same_player_continues
    assert advanced.schedule.current_player == "P1"
    assert not advanced.pokemon_checkup_occurs


def test_prevented_damage_does_not_trigger_reaction() -> None:
    resolution = timeless_resolution()
    defender = make_board(make_pokemon("defender", "Protected defender"))
    board_resolution = replay_copy_attack_board(
        resolution,
        defender,
        event_programs={
            TIMELESS_EVENT: BoardEventProgram(
                "defender",
                DamageContext(
                    attack=AttackDamage(150),
                    prevent_all_damage=True,
                ),
            )
        },
        hp_by_object_id={"defender": 10},
    )
    reacted = resolve_copy_damage_reactions(
        board_resolution,
        make_board(make_pokemon("attacker", "Attacker")),
        body_event=TIMELESS_EVENT,
        reactions=(
            DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),
        ),
        attacker_hp_by_object_id={"attacker": 10},
        defender_hp_by_object_id={"defender": 10},
    )
    assert not reacted.reaction_result.triggered
    assert reacted.reaction_result.counters_placed_on_attacker == 0
    assert reacted.reaction_result.attacker_knocked_out_ids == ()
    assert reacted.reaction_result.defender_knocked_out_ids == ()


def main() -> None:
    test_reflected_damage_creates_cross_side_ko_barrier()
    test_surviving_reaction_state_can_reach_extra_turn_scheduler()
    test_prevented_damage_does_not_trigger_reaction()
    print("attack-copy damage reaction bridge regression: PASS")


if __name__ == "__main__":
    main()
