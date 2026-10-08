"""Card-grounded physical replay of supplemental and all-target damage."""
from __future__ import annotations

from dataclasses import replace
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import (
    AttackDef, CopySelector, PokemonRef, State, choose_exact, resolve_attack,
)
from attack_copy_physical_ko_bridge import replay_copy_attack_physical_board
from attack_damage_target_geometry import (
    catalog, plan_literal_damage_targets,
)
from board_position_state import AttachmentKind, BoardPokemon, PokemonCard, make_state
from damage_calculation_kernel import calculate_damage
from identity_materialization import IdentityLedger, materialize, put_in_play_instance
from literal_damage_profiled_copy_bridge import materialize_profiled_literal_damage_program
from multicopy_zone_state import ZoneCountState
from pokemon_card_profile import build_pokemon_card_profile_index
from simple_attack_board_semantics import compile_legal_index
from stack_knockout_conservation import StackBoardMaterialState, attach_from_hand
from physical_damage_reaction_sources import eligible_spiky_energy_reactions
from damage_reaction_kernel import DamageReaction, DamageReactionKind
from stack_board_profile_binding import hp_by_stack_board


def defender_board(*, with_spiky: bool = False) -> StackBoardMaterialState:
    classes = {
        ("a-class", "hand"): 1,
        ("b-class", "hand"): 1,
    }
    if with_spiky:
        classes[("spiky-energy", "hand")] = 2
    original = IdentityLedger(ZoneCountState.from_mapping(classes))
    ledger = original
    rows: list[BoardPokemon] = []
    for pokemon_id, card_class in (("active", "a-class"), ("bench", "b-class")):
        instance = f"{pokemon_id}-instance"
        ledger = materialize(
            ledger, card_class=card_class, card_name="Dratini",
            source_zone="hand", instance_id=instance,
        )
        ledger = put_in_play_instance(ledger, instance, pokemon_id)
        rows.append(BoardPokemon(
            pokemon_id,
            (PokemonCard(instance, "Dratini"),),
            retreat_cost=1,
        ))
    state = StackBoardMaterialState(ledger, make_state(rows, active_id="active"))
    if with_spiky:
        for pokemon_id in ("active", "bench"):
            state = attach_from_hand(
                state, pokemon_id=pokemon_id, card_class="spiky-energy",
                instance_id=f"{pokemon_id}-spiky",
                card_name="Spiky Energy",
                kind=AttachmentKind.ENERGY,
                retreat_units=1,
            )
            assert state is not None
    return state


def copy_source(source, source_def):
    outer = AttackDef(
        "persian:haughty-order", "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    )
    return resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=outer.attack_id,
        attacks={outer.attack_id: outer, source_def.attack_id: source_def},
        state=State(pokemon=(
            PokemonRef(
                "p2-revealed-source", source.card_name, "P2",
                "revealed", attacks=(source_def.attack_id,),
            ),
        )),
        choose=choose_exact((source_def.attack_id,)),
    )


def by_name(rows, card_id: str, name: str):
    matches = [
        row for row in rows
        if row.card_id == card_id and row.attack_name == name
    ]
    assert len(matches) == 1
    return matches[0]


def main() -> None:
    target_state = defender_board()
    board = target_state.board
    assert board is not None

    attack_index = compile_legal_index(ROOT / "resources")
    all_rows = catalog(ROOT / "resources")["rows"]
    profiles = build_pokemon_card_profile_index(ROOT / "resources")
    persian = profiles["sv10-150"]
    print_bindings = {"active": "bw9-81", "bench": "bw9-81"}
    hp = hp_by_stack_board(board, profiles, print_bindings)
    assert persian.types == ("Colorless",)
    assert hp == {"active": 50, "bench": 50}

    night = by_name(all_rows, "bw5-63", "Night Spear")
    night_attack = attack_index[night.card_id][night.attack_index]
    night_plan = plan_literal_damage_targets(
        night, board, selected_target_ids=("bench",),
    )
    night_program = materialize_profiled_literal_damage_program(
        night_plan, board, actor_profile=persian, profiles=profiles,
        current_print_id_by_pokemon_id=print_bindings,
    )
    assert night_program.damage_target_id == "active"
    assert len(night_program.additional_damage) == 1
    assert calculate_damage(night_program.damage_context).final_damage == 90
    assert calculate_damage(night_program.additional_damage[0][1]).final_damage == 30
    night_copy = copy_source(night, night_attack.to_leaf_attack_def())
    night_replay = replay_copy_attack_physical_board(
        night_copy, target_state,
        event_programs={night_attack.event_label: night_program},
        hp_by_pokemon_id=hp,
    )
    assert tuple(
        (r.target_index, r.target_id, r.result.final_damage)
        for r in night_replay.damage_records
    ) == ((0, "active", 90), (1, "bench", 30))
    assert night_replay.knocked_out_ids == ("active",)
    assert night_replay.state.board.get("bench").damage_counters == 3
    assert night_replay.event_trace[-1].event == "shuffle_revealed"

    glaciate = by_name(all_rows, "bw11-43", "Glaciate")
    glacier_attack = attack_index[glaciate.card_id][glaciate.attack_index]
    glaciate_plan = plan_literal_damage_targets(glaciate, board)
    glaciate_program = materialize_profiled_literal_damage_program(
        glaciate_plan, board, actor_profile=persian, profiles=profiles,
        current_print_id_by_pokemon_id=print_bindings,
        attacker_types=("Dragon",),
    )
    assert glaciate_program.damage_target_id == "active"
    assert glaciate_program.damage_context.weakness_multiplier == 2
    assert glaciate_program.additional_damage[0][1].ignore_weakness_resistance
    assert tuple(
        calculate_damage(ctx).final_damage
        for _target, ctx in (
            (glaciate_program.damage_target_id, glaciate_program.damage_context),
            *glaciate_program.additional_damage,
        )
    ) == (60, 30)
    glaciate_copy = copy_source(glaciate, glacier_attack.to_leaf_attack_def())
    glaciate_replay = replay_copy_attack_physical_board(
        glaciate_copy, target_state,
        event_programs={glacier_attack.event_label: glaciate_program},
        hp_by_pokemon_id=hp,
    )
    assert glaciate_replay.knocked_out_ids == ("active",)
    assert glaciate_replay.state.board.get("active").damage_counters == 6
    assert glaciate_replay.state.board.get("bench").damage_counters == 3

    # Repeated event-recipient pairs currently lack reaction disambiguation.
    double_active = replace(night, target_scope="opponent_any")
    double_plan = plan_literal_damage_targets(
        double_active, board, selected_target_ids=("active",),
    )
    try:
        materialize_profiled_literal_damage_program(
            double_plan, board, actor_profile=persian, profiles=profiles,
            current_print_id_by_pokemon_id=print_bindings,
        )
    except ValueError as error:
        assert "more than once" in str(error)
    else:
        raise AssertionError("duplicated body/target pair was accepted")

    # A copied attack can trigger an attached Spiky Energy despite the
    # defender being Knocked Out. The Benched copy of the same Energy has no
    # such Active-Spot reaction, even if its holder took damage.
    spiky_state = defender_board(with_spiky=True)
    assert spiky_state.board is not None
    spiky_replay = replay_copy_attack_physical_board(
        night_copy, spiky_state,
        event_programs={night_attack.event_label: night_program},
        hp_by_pokemon_id=hp,
    )
    active_reaction = eligible_spiky_energy_reactions(
        spiky_replay,
        body_event=night_attack.event_label,
        damaged_pokemon_id="active",
        from_opponents_pokemon=True,
    )
    bench_reaction = eligible_spiky_energy_reactions(
        spiky_replay,
        body_event=night_attack.event_label,
        damaged_pokemon_id="bench",
        from_opponents_pokemon=True,
    )
    assert active_reaction == (
        DamageReaction(DamageReactionKind.FIXED_COUNTERS, 2),
    )
    assert bench_reaction == ()
    assert eligible_spiky_energy_reactions(
        spiky_replay,
        body_event=night_attack.event_label,
        damaged_pokemon_id="active",
        from_opponents_pokemon=False,
    ) == ()
    assert spiky_replay.knocked_out_ids == ("active",)
    assert len(spiky_replay.state.board.get("active").attachments) == 1

    print({
        "card_grounded_copy_programs": 2,
        "night_spear_damage_sites": tuple(
            (r.target_id, r.result.final_damage)
            for r in night_replay.damage_records
        ),
        "glaciate_damage_sites": tuple(
            (r.target_id, r.result.final_damage)
            for r in glaciate_replay.damage_records
        ),
        "printed_vs_text_damage_distinguished": True,
        "repeated_site_rejected": True,
        "card_grounded_spiky_active_vs_bench": (len(active_reaction), len(bench_reaction)),
    })


if __name__ == "__main__":
    main()
