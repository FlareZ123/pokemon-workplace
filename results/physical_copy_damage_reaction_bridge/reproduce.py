"""Reproduce physical copied-attack reflections into simultaneous Knock Outs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef, CopySelector, PokemonRef, State, TurnBoundaryEffect,
    choose_exact, resolve_attack,
)
from attack_copy_physical_ko_bridge import (
    PhysicalBoardEventProgram, replay_copy_attack_physical_board,
)
from board_position_state import AttachmentKind, BoardPokemon, PokemonCard, make_state
from cross_player_knockout_resolution import (
    CrossPlayerKnockOutContext, choose_promotion, promotion_order,
    resolve_cross_player_knock_out,
)
from damage_calculation_kernel import AttackDamage, DamageContext
from damage_reaction_kernel import DamageReaction, DamageReactionKind
from identity_materialization import (
    IdentityLedger, assert_conserved, materialize, put_in_play_instance,
)
from multicopy_zone_state import ZoneCountState
from physical_copy_damage_reaction_bridge import (
    prepare_reacted_physical_knockouts,
    resolve_physical_copy_damage_reactions,
)
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand

HAUGHTY = "persian:haughty-order"
TIMELESS = "dialga:timeless-gx"
BODY = "body:timeless-gx"


def copied_timeless():
    attacks = {
        HAUGHTY: AttackDef(
            HAUGHTY, "Haughty Order",
            copy_selector=CopySelector("opponent_revealed"),
            pre_event="reveal_top_10", post_event="shuffle_revealed",
        ),
        TIMELESS: AttackDef(
            TIMELESS, "Timeless-GX", is_gx=True, effect_label=BODY,
            turn_boundary_effect=TurnBoundaryEffect(
                take_another_turn=True, skip_pokemon_checkup=True,
            ),
        ),
    }
    return resolve_attack(
        actor_player="A", actor_card_id="a-active-card",
        declared_attack_id=HAUGHTY, attacks=attacks,
        state=State(pokemon=(
            PokemonRef(
                "b-dialga-revealed", "Dialga-GX", "B",
                "revealed", attacks=(TIMELESS,),
            ),
        )),
        choose=choose_exact((TIMELESS,)),
    )


def physical_player(prefix: str, attach: AttachmentKind):
    card_classes = {
        (f"{prefix}-active-class", "hand"): 1,
        (f"{prefix}-bench-class", "hand"): 1,
        (f"{prefix}-attachment-class", "hand"): 1,
    }
    initial = IdentityLedger(ZoneCountState.from_mapping(card_classes))
    ledger = initial
    for role in ("active", "bench"):
        identity = f"{prefix}-{role}-card"
        ledger = materialize(
            ledger, card_class=f"{prefix}-{role}-class",
            card_name=f"{prefix} {role}", source_zone="hand",
            instance_id=identity,
        )
        ledger = put_in_play_instance(ledger, identity, f"{prefix}-{role}")
    board = make_state(
        tuple(
            BoardPokemon(
                f"{prefix}-{role}",
                (PokemonCard(f"{prefix}-{role}-card", f"{prefix} {role}"),),
                retreat_cost=1,
            )
            for role in ("active", "bench")
        ),
        active_id=f"{prefix}-active",
    )
    state = StackBoardMaterialState(ledger, board)
    state = attach_from_hand(
        state, pokemon_id=f"{prefix}-active",
        card_class=f"{prefix}-attachment-class",
        instance_id=f"{prefix}-attached",
        card_name=("Muscle Band" if attach is AttachmentKind.TOOL else "Spiky Energy"),
        kind=attach,
        retreat_units=0,
    )
    assert state is not None
    assert_conserved(initial, state.ledger)
    return initial, state


def test_reflection_full_physical_batch():
    initial_a, a = physical_player("a", AttachmentKind.TOOL)
    initial_b, b = physical_player("b", AttachmentKind.ENERGY)
    copy = copied_timeless()
    replay = replay_copy_attack_physical_board(
        copy, b,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active", DamageContext(attack=AttackDamage(150)),
            ),
        },
        hp_by_pokemon_id={"b-active": 130, "b-bench": 100},
    )
    assert tuple(step.event for step in replay.event_trace) == (
        "reveal_top_10", BODY, "shuffle_revealed",
    )

    result = resolve_physical_copy_damage_reactions(
        replay, a, body_event=BODY,
        reactions=(
            DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),
            DamageReaction(DamageReactionKind.FIXED_COUNTERS, fixed_counters=2),
        ),
        attacker_hp_by_pokemon_id={"a-active": 170, "a-bench": 100},
        defender_hp_by_pokemon_id={"b-active": 130, "b-bench": 100},
    )
    assert result.triggered
    assert result.counters_placed_on_attacker == 17
    assert result.attacker_knocked_out_ids == ("a-active",)
    assert result.defender_knocked_out_ids == ("b-active",)
    assert result.attacker_state.board.get("a-active").damage_counters == 17
    assert result.defender_state.board.get("b-active").damage_counters == 15
    assert_conserved(initial_a, result.attacker_state.ledger)
    assert_conserved(initial_b, result.defender_state.ledger)

    pending_a, pending_b = prepare_reacted_physical_knockouts(result)
    assert pending_a is not None and pending_b is not None
    assert pending_a.state.board.get("a-active").attachments[0].card_id == "a-attached"
    assert pending_b.state.board.get("b-active").attachments[0].card_id == "b-attached"
    ctx = CrossPlayerKnockOutContext(
        (("A", pending_a), ("B", pending_b)),
        next_player_id="B",
    )
    assert promotion_order(ctx) == ("B", "A")
    assert choose_promotion(ctx, player_id="A", pokemon_id="a-bench") is None
    ctx = choose_promotion(ctx, player_id="B", pokemon_id="b-bench")
    assert ctx is not None
    ctx = choose_promotion(ctx, player_id="A", pokemon_id="a-bench")
    assert ctx is not None
    finished = resolve_cross_player_knock_out(ctx)
    assert finished is not None
    final_a = finished.state_for("A")
    final_b = finished.state_for("B")
    assert final_a.board.active_id == "a-bench"
    assert final_b.board.active_id == "b-bench"
    for prefix, original, final in (
        ("a", initial_a, final_a), ("b", initial_b, final_b)
    ):
        assert final.ledger.exchangeable.count(f"{prefix}-active-class", "discard") == 1
        assert final.ledger.exchangeable.count(f"{prefix}-attachment-class", "discard") == 1
        assert_conserved(original, final.ledger)


def test_prevented_damage_and_one_sided_ko():
    _, a = physical_player("a", AttachmentKind.TOOL)
    _, b = physical_player("b", AttachmentKind.ENERGY)
    copy = copied_timeless()
    prevented_replay = replay_copy_attack_physical_board(
        copy, b,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active", DamageContext(
                    attack=AttackDamage(150), prevent_all_damage=True,
                ),
            ),
        },
        hp_by_pokemon_id={"b-active": 130, "b-bench": 100},
    )
    prevented = resolve_physical_copy_damage_reactions(
        prevented_replay, a, body_event=BODY,
        reactions=(DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),),
        attacker_hp_by_pokemon_id={"a-active": 10, "a-bench": 100},
        defender_hp_by_pokemon_id={"b-active": 130, "b-bench": 100},
    )
    assert not prevented.triggered
    assert prevented.counters_placed_on_attacker == 0
    assert prepare_reacted_physical_knockouts(prevented) == (None, None)
    assert prevented.attacker_state is a

    unprevented_replay = replay_copy_attack_physical_board(
        copy, b,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active", DamageContext(attack=AttackDamage(150)),
            ),
        },
        hp_by_pokemon_id={"b-active": 130, "b-bench": 100},
    )
    one_sided = resolve_physical_copy_damage_reactions(
        unprevented_replay, a, body_event=BODY,
        reactions=(DamageReaction(DamageReactionKind.MIRROR_FINAL_DAMAGE),),
        attacker_hp_by_pokemon_id={"a-active": 160, "a-bench": 100},
        defender_hp_by_pokemon_id={"b-active": 130, "b-bench": 100},
    )
    pa, pb = prepare_reacted_physical_knockouts(one_sided)
    assert pa is None and pb is not None
    assert one_sided.attacker_state.board.get("a-active").damage_counters == 15
    try:
        resolve_physical_copy_damage_reactions(
            unprevented_replay, a, body_event="missing",
            reactions=(),
            attacker_hp_by_pokemon_id={"a-active": 160, "a-bench": 100},
            defender_hp_by_pokemon_id={"b-active": 130, "b-bench": 100},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("unknown damage events must be rejected")


def main():
    test_reflection_full_physical_batch()
    test_prevented_damage_and_one_sided_ko()
    print("physical copied-attack reaction/KO integration: PASS")


if __name__ == "__main__":
    main()
