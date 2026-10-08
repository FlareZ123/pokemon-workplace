"""Reproduce typed multi-target copied damage with Active-only Energy reactions."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef, CopySelector, PokemonRef, State, choose_exact, resolve_attack,
)
from attack_copy_physical_ko_bridge import (
    PhysicalBoardEventProgram, replay_copy_attack_physical_board,
)
from board_position_state import (
    AttachmentKind, BoardPokemon, PokemonCard, clear_for_bench, make_state,
)
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
from physical_damage_reaction_sources import eligible_spiky_energy_reactions
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand

HAUGHTY = "persian:haughty-order"
DUAL_BOLT = "electivire-ex:dual-bolt"
BODY = "body:dual-bolt"


def copied_dual_bolt():
    electivire = json.loads(
        (ROOT / "resources" / "cards" / "en" / "sv10.json")
        .read_text(encoding="utf-8")
    )
    print_row = next(card for card in electivire if card["id"] == "sv10-69")
    source = next(attack for attack in print_row["attacks"] if attack["name"] == "Dual Bolt")
    assert source["damage"] == ""
    assert source["text"].startswith("This attack does 50 damage to 2 of your opponent's Pokémon.")

    attacks = {
        HAUGHTY: AttackDef(
            HAUGHTY, "Haughty Order",
            copy_selector=CopySelector("opponent_revealed"),
            pre_event="reveal_top_10", post_event="shuffle_revealed",
        ),
        DUAL_BOLT: AttackDef(
            DUAL_BOLT, "Dual Bolt", effect_label=BODY,
        ),
    }
    return resolve_attack(
        actor_player="P1",
        actor_card_id="p1-copying-active",
        declared_attack_id=HAUGHTY,
        attacks=attacks,
        state=State(
            pokemon=(
                PokemonRef(
                    "p2-electivire-revealed", "Electivire ex",
                    "P2", "revealed", attacks=(DUAL_BOLT,),
                ),
            ),
        ),
        choose=choose_exact((DUAL_BOLT,)),
    )


def make_physical_player(prefix: str, *, two_spiky: bool):
    classes = {
        (f"{prefix}-active-class", "hand"): 1,
        (f"{prefix}-bench-class", "hand"): 1,
    }
    if two_spiky:
        classes[(f"{prefix}-spiky-class", "hand")] = 2

    initial = IdentityLedger(ZoneCountState.from_mapping(classes))
    ledger = initial
    for role in ("active", "bench"):
        instance = f"{prefix}-{role}-instance"
        ledger = materialize(
            ledger, card_class=f"{prefix}-{role}-class",
            card_name=f"{prefix} {role}", source_zone="hand",
            instance_id=instance,
        )
        ledger = put_in_play_instance(ledger, instance, f"{prefix}-{role}")

    state = StackBoardMaterialState(
        ledger,
        make_state(
            (
                BoardPokemon(
                    f"{prefix}-active",
                    (PokemonCard(f"{prefix}-active-instance", f"{prefix} active"),),
                    retreat_cost=1,
                    damage_counters=8 if prefix == "a" else 0,
                ),
                BoardPokemon(
                    f"{prefix}-bench",
                    (PokemonCard(f"{prefix}-bench-instance", f"{prefix} bench"),),
                    retreat_cost=1,
                ),
            ),
            active_id=f"{prefix}-active",
        ),
    )
    if two_spiky:
        for role in ("active", "bench"):
            state = attach_from_hand(
                state,
                pokemon_id=f"{prefix}-{role}",
                card_class=f"{prefix}-spiky-class",
                instance_id=f"{prefix}-{role}-spiky",
                card_name="Spiky Energy",
                kind=AttachmentKind.ENERGY,
                retreat_units=1,
            )
            assert state is not None
    assert_conserved(initial, state.ledger)
    return initial, state


def test_target_specific_reactions_and_conservation():
    initial_a, attacker = make_physical_player("a", two_spiky=False)
    initial_b, defender = make_physical_player("b", two_spiky=True)
    copy = copied_dual_bolt()
    replay = replay_copy_attack_physical_board(
        copy, defender,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active",
                DamageContext(attack=AttackDamage(50)),
                additional_damage=(
                    (
                        "b-bench",
                        DamageContext(
                            attack=AttackDamage(50),
                            ignore_weakness_resistance=True,
                        ),
                    ),
                ),
            ),
        },
        hp_by_pokemon_id={"b-active": 120, "b-bench": 40},
    )
    assert tuple(step.event for step in replay.event_trace) == (
        "reveal_top_10", BODY, "shuffle_revealed",
    )
    assert replay.damage_targets == (
        (BODY, "b-active"), (BODY, "b-bench"),
    )
    assert tuple(
        (row.event, row.target_index, row.target_id, row.result.final_damage)
        for row in replay.damage_records
    ) == (
        (BODY, 0, "b-active", 50),
        (BODY, 1, "b-bench", 50),
    )
    assert replay.knocked_out_ids == ("b-bench",)
    assert replay.state.board.get("b-active").damage_counters == 5
    assert replay.state.board.get("b-bench").damage_counters == 5
    assert_conserved(initial_b, replay.state.ledger)

    active_reaction = eligible_spiky_energy_reactions(
        replay, body_event=BODY, damaged_pokemon_id="b-active",
        from_opponents_pokemon=True,
    )
    bench_reaction = eligible_spiky_energy_reactions(
        replay, body_event=BODY, damaged_pokemon_id="b-bench",
        from_opponents_pokemon=True,
    )
    assert active_reaction == (
        DamageReaction(DamageReactionKind.FIXED_COUNTERS, 2),
    )
    assert bench_reaction == ()

    result = resolve_physical_copy_damage_reactions(
        replay, attacker,
        body_event=BODY, damaged_pokemon_id="b-active",
        attacking_pokemon_id="a-active",
        reactions=active_reaction,
        attacker_hp_by_pokemon_id={"a-active": 100, "a-bench": 100},
        defender_hp_by_pokemon_id={"b-active": 120, "b-bench": 40},
    )
    assert result.counters_placed_on_attacker == 2
    assert result.attacker_state.board.get("a-active").damage_counters == 10
    assert result.attacker_knocked_out_ids == ("a-active",)
    assert result.defender_knocked_out_ids == ("b-bench",)

    pending_a, pending_b = prepare_reacted_physical_knockouts(result)
    assert pending_a is not None and pending_b is not None
    assert pending_b.state.board.get("b-active").attachments[0].card_id == "b-active-spiky"
    assert pending_b.state.board.get("b-bench").attachments[0].card_id == "b-bench-spiky"

    context = CrossPlayerKnockOutContext(
        (("A", pending_a), ("B", pending_b)), next_player_id="B",
    )
    assert promotion_order(context) == ("A",)
    context = choose_promotion(
        context, player_id="A", pokemon_id="a-bench",
    )
    assert context is not None
    after = resolve_cross_player_knock_out(context)
    assert after is not None
    a = after.state_for("A")
    b = after.state_for("B")
    assert a.board.active_id == "a-bench"
    assert b.board.active_id == "b-active"
    assert b.ledger.exchangeable.count("b-spiky-class", "discard") == 1
    assert b.board.get("b-active").attachments[0].card_id == "b-active-spiky"
    assert_conserved(initial_a, a.ledger)
    assert_conserved(initial_b, b.ledger)


def test_multiple_same_target_records_need_disambiguation():
    _, attacker = make_physical_player("a", two_spiky=False)
    _, defender = make_physical_player("b", two_spiky=True)
    replay = replay_copy_attack_physical_board(
        copied_dual_bolt(), defender,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active", DamageContext(attack=AttackDamage(10)),
                additional_damage=(
                    ("b-active", DamageContext(attack=AttackDamage(10))),
                ),
            ),
        },
        hp_by_pokemon_id={"b-active": 120, "b-bench": 40},
    )
    assert len(replay.damage_records) == 2
    for callable_ in (
        lambda: eligible_spiky_energy_reactions(
            replay, body_event=BODY, damaged_pokemon_id="b-active",
            from_opponents_pokemon=True,
        ),
        lambda: resolve_physical_copy_damage_reactions(
            replay, attacker, body_event=BODY,
            damaged_pokemon_id="b-active", attacking_pokemon_id="a-active",
            reactions=(),
            attacker_hp_by_pokemon_id={"a-active": 100, "a-bench": 100},
            defender_hp_by_pokemon_id={"b-active": 120, "b-bench": 40},
        ),
    ):
        try:
            callable_()
        except ValueError:
            pass
        else:
            raise AssertionError("ambiguous repeated damage target was accepted")



def test_moved_attacker_keeps_reflection_target_identity():
    initial_a, attacker = make_physical_player("a", two_spiky=False)
    _, defender = make_physical_player("b", two_spiky=True)
    replay = replay_copy_attack_physical_board(
        copied_dual_bolt(), defender,
        event_programs={
            BODY: PhysicalBoardEventProgram(
                "b-active", DamageContext(attack=AttackDamage(50)),
            ),
        },
        hp_by_pokemon_id={"b-active": 120, "b-bench": 40},
    )
    reactions = eligible_spiky_energy_reactions(
        replay, body_event=BODY, damaged_pokemon_id="b-active",
        from_opponents_pokemon=True,
    )
    assert len(reactions) == 1

    # An upstream attack effect has switched the attacking Pokémon to the
    # Bench after damage; its identity persists through the reaction step.
    assert attacker.board is not None
    board = replace(
        attacker.board,
        active_id="a-bench",
        pokemon=(
            clear_for_bench(attacker.board.get("a-active")),
            attacker.board.get("a-bench"),
        ),
    )
    moved = StackBoardMaterialState(attacker.ledger, board)
    result = resolve_physical_copy_damage_reactions(
        replay, moved, body_event=BODY, damaged_pokemon_id="b-active",
        attacking_pokemon_id="a-active", reactions=reactions,
        attacker_hp_by_pokemon_id={"a-active": 100, "a-bench": 100},
        defender_hp_by_pokemon_id={"b-active": 120, "b-bench": 40},
    )
    assert result.attacker_knocked_out_ids == ("a-active",)
    assert result.attacker_state.board.active_id == "a-bench"
    assert result.attacker_state.board.get("a-active").damage_counters == 10
    assert result.attacker_state.board.get("a-bench").damage_counters == 0
    assert_conserved(initial_a, result.attacker_state.ledger)

    try:
        resolve_physical_copy_damage_reactions(
            replay, moved, body_event=BODY,
            damaged_pokemon_id="b-active",
            attacking_pokemon_id="missing",
            reactions=reactions,
            attacker_hp_by_pokemon_id={"a-active": 100, "a-bench": 100},
            defender_hp_by_pokemon_id={"b-active": 120, "b-bench": 40},
        )
    except ValueError:
        pass
    else:
        raise AssertionError("a missing attacking Pokémon identity was accepted")


def main():
    test_target_specific_reactions_and_conservation()
    test_multiple_same_target_records_need_disambiguation()
    test_moved_attacker_keeps_reflection_target_identity()
    print("physical multi-target damage reaction regression: PASS")


if __name__ == "__main__":
    main()
