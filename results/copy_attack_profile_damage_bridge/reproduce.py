from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import AttackDef, CopySelector, PokemonRef, State, choose_exact, resolve_attack
from attack_copy_physical_ko_bridge import replay_copy_attack_physical_board
from board_position_state import BoardPokemon, PokemonCard, make_state
from copy_attack_profile_damage_bridge import hp_by_stack_board, materialize_profiled_copy_program
from damage_calculation_kernel import calculate_damage
from identity_materialization import IdentityLedger, materialize, put_in_play_instance
from multicopy_zone_state import ZoneCountState
from pokemon_card_profile import build_pokemon_card_profile_index
from simple_attack_board_semantics import compile_legal_index
from stack_knockout_conservation import StackBoardMaterialState

HAUGHTY = "persian:haughty-order"


def target_board() -> StackBoardMaterialState:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("target-active-class", "hand"): 1,
                ("target-bench-class", "hand"): 1,
            }
        )
    )
    ledger = initial
    rows = []
    for card_class, pokemon_id, instance_id, name in (
        ("target-active-class", "target-active", "target-active-instance", "Dragon-weak Active"),
        ("target-bench-class", "target-bench", "target-bench-instance", "Bench target"),
    ):
        ledger = materialize(
            ledger,
            card_class=card_class,
            card_name=name,
            source_zone="hand",
            instance_id=instance_id,
        )
        ledger = put_in_play_instance(ledger, instance_id, pokemon_id)
        rows.append(
            BoardPokemon(
                pokemon_id,
                (PokemonCard(instance_id, name),),
                retreat_cost=1,
            )
        )
    return StackBoardMaterialState(
        ledger,
        make_state(rows, active_id="target-active"),
    )


def main() -> None:
    profiles = build_pokemon_card_profile_index(ROOT / "resources")
    attacks_index = compile_legal_index(ROOT / "resources")

    persian = profiles["sv10-150"]
    dragapult = profiles["sv6-130"]
    dratini = profiles["bw9-81"]
    assert persian.types == ("Colorless",)
    assert dragapult.types == ("Dragon",)
    assert dratini.weaknesses[0].energy_type == "Dragon"

    phantom = next(
        row for row in attacks_index["sv6-130"]
        if row.attack_name == "Phantom Dive"
    )
    phantom_def = phantom.to_leaf_attack_def()

    state = target_board()
    board = state.board
    assert board is not None
    print_bindings = {
        "target-active": "bw9-81",
        "target-bench": "bw9-82",
    }
    hp = hp_by_stack_board(board, profiles, print_bindings)
    assert hp == {"target-active": 50, "target-bench": 70}

    actor_typed = materialize_profiled_copy_program(
        phantom,
        board,
        actor_profile=persian,
        profiles=profiles,
        current_print_id_by_pokemon_id=print_bindings,
        counter_allocation=(("target-bench", 6),),
    )
    actor_damage = calculate_damage(actor_typed.damage_context)
    assert actor_damage.final_damage == 200

    source_typed = materialize_profiled_copy_program(
        phantom,
        board,
        actor_profile=persian,
        profiles=profiles,
        current_print_id_by_pokemon_id=print_bindings,
        counter_allocation=(("target-bench", 6),),
        attacker_types=dragapult.types,
    )
    source_damage = calculate_damage(source_typed.damage_context)
    assert source_damage.final_damage == 400

    haughty = AttackDef(
        HAUGHTY,
        "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    )
    copy = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks={HAUGHTY: haughty, phantom_def.attack_id: phantom_def},
        state=State(
            pokemon=(
                PokemonRef(
                    "p2-dragapult-revealed",
                    "Dragapult ex",
                    "P2",
                    "revealed",
                    attacks=(phantom_def.attack_id,),
                ),
            )
        ),
        choose=choose_exact((phantom_def.attack_id,)),
    )
    replay = replay_copy_attack_physical_board(
        copy,
        state,
        event_programs={phantom.event_label: actor_typed},
        hp_by_pokemon_id=hp,
    )
    assert replay.damage_results[0][1].final_damage == 200
    assert replay.state.board is not None
    assert replay.state.board.get("target-bench").damage_counters == 6
    assert replay.knocked_out_ids == ("target-active",)
    assert replay.event_trace[-1].event == "shuffle_revealed"

    live_dragon_type = materialize_profiled_copy_program(
        phantom,
        board,
        actor_profile=persian,
        profiles=profiles,
        current_print_id_by_pokemon_id=print_bindings,
        counter_allocation=(("target-bench", 6),),
        attacker_types=("Dragon",),
    )
    assert calculate_damage(live_dragon_type.damage_context).final_damage == 400

    mind_shock = next(
        row for row in attacks_index["sm8-94"]
        if row.attack_name == "Mind Shock"
    )
    assert mind_shock.ignore_weakness_resistance
    assert not mind_shock.ignore_defender_effects
    psychic_bindings = {
        "target-active": "sm8-94",
        "target-bench": "bw9-82",
    }
    mind_program = materialize_profiled_copy_program(
        mind_shock,
        board,
        actor_profile=profiles["sm8-94"],
        profiles=profiles,
        current_print_id_by_pokemon_id=psychic_bindings,
    )
    assert mind_program.damage_context.ignore_weakness_resistance
    assert calculate_damage(mind_program.damage_context).final_damage == 70

    mind_with_weakness = materialize_profiled_copy_program(
        mind_shock,
        board,
        actor_profile=profiles["sm8-94"],
        profiles=profiles,
        current_print_id_by_pokemon_id=psychic_bindings,
        ignore_weakness_resistance=False,
    )
    assert calculate_damage(mind_with_weakness.damage_context).final_damage == 140

    # Cramorant ignores Weakness, while Landorus independently ignores
    # Resistance. These dimensions cannot share a single global flag.
    cramorant = next(
        row for row in attacks_index["swsh11-50"]
        if row.attack_name == "Spit Innocently"
    )
    assert cramorant.ignore_weakness
    assert not cramorant.ignore_resistance
    assert not cramorant.ignore_weakness_resistance
    water_weak_bindings = {
        "target-active": "sv1-30",
        "target-bench": "bw9-82",
    }
    water_weak_program = materialize_profiled_copy_program(
        cramorant,
        board,
        actor_profile=profiles["swsh11-50"],
        profiles=profiles,
        current_print_id_by_pokemon_id=water_weak_bindings,
    )
    assert calculate_damage(water_weak_program.damage_context).final_damage == 110
    water_weak_control = materialize_profiled_copy_program(
        cramorant,
        board,
        actor_profile=profiles["swsh11-50"],
        profiles=profiles,
        current_print_id_by_pokemon_id=water_weak_bindings,
        ignore_weakness_resistance=False,
    )
    assert calculate_damage(water_weak_control.damage_context).final_damage == 220

    landorus = next(
        row for row in attacks_index["sv8-110"]
        if row.attack_name == "Buster Swing"
    )
    assert not landorus.ignore_weakness
    assert landorus.ignore_resistance
    assert not landorus.ignore_weakness_resistance
    fighting_resistant_bindings = {
        "target-active": "sv1-82",
        "target-bench": "bw9-82",
    }
    fighting_resistant_program = materialize_profiled_copy_program(
        landorus,
        board,
        actor_profile=profiles["sv8-110"],
        profiles=profiles,
        current_print_id_by_pokemon_id=fighting_resistant_bindings,
    )
    assert calculate_damage(fighting_resistant_program.damage_context).final_damage == 130
    fighting_resistant_control = materialize_profiled_copy_program(
        landorus,
        board,
        actor_profile=profiles["sv8-110"],
        profiles=profiles,
        current_print_id_by_pokemon_id=fighting_resistant_bindings,
        ignore_weakness_resistance=False,
    )
    assert calculate_damage(fighting_resistant_control.damage_context).final_damage == 100

    one_sided_rows = [
        row
        for attacks in attacks_index.values()
        for row in attacks
        if row.fixed_damage is not None
        and row.ignore_weakness != row.ignore_resistance
    ]
    assert any(row.attack_id == cramorant.attack_id for row in one_sided_rows)
    assert any(row.attack_id == landorus.attack_id for row in one_sided_rows)

    shred = next(
        row for row in attacks_index["sm5-100"]
        if row.attack_name == "Shred"
    )
    assert not shred.ignore_weakness_resistance
    assert shred.ignore_defender_effects
    shred_program = materialize_profiled_copy_program(
        shred,
        board,
        actor_profile=profiles["sm5-100"],
        profiles=profiles,
        current_print_id_by_pokemon_id=print_bindings,
    )
    assert not shred_program.damage_context.ignore_weakness_resistance
    assert shred_program.damage_context.ignore_defender_effects
    assert calculate_damage(shred_program.damage_context).final_damage == 160

    print(
        {
            "copying_pokemon": persian.name,
            "copying_types": persian.types,
            "source_pokemon": dragapult.name,
            "source_types": dragapult.types,
            "target": dratini.name,
            "target_weakness": dratini.weaknesses[0].energy_type,
            "actor_typed_damage": actor_damage.final_damage,
            "source_typed_damage": source_damage.final_damage,
            "physical_replay_kos": replay.knocked_out_ids,
            "one_sided_modifier_bypass_fixed_rows": len(one_sided_rows),
            "weakness_only_damage": 110,
            "resistance_only_damage": 130,
        }
    )


if __name__ == "__main__":
    main()
