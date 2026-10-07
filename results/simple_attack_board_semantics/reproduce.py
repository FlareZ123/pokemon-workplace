from __future__ import annotations

from collections import Counter
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_copy_kernel import AttackDef, CopySelector, PokemonRef, State, choose_exact, resolve_attack
from attack_copy_physical_ko_bridge import replay_copy_attack_physical_board
from board_position_state import BoardPokemon, PokemonCard, make_state
from identity_materialization import IdentityLedger, materialize, put_in_play_instance
from multicopy_zone_state import ZoneCountState
from simple_attack_board_semantics import (
    compile_legal_index,
    materialize_opponent_board_program,
)
from stack_knockout_conservation import StackBoardMaterialState

HAUGHTY = "persian:haughty-order"


def physical_board() -> StackBoardMaterialState:
    initial = IdentityLedger(
        ZoneCountState.from_mapping(
            {
                ("active", "hand"): 1,
                ("bench-a", "hand"): 1,
                ("bench-b", "hand"): 1,
            }
        )
    )
    ledger = initial
    rows = []
    for card_class, pokemon_id, name in (
        ("active", "active", "200 HP Active"),
        ("bench-a", "bench-a", "40 HP Bench"),
        ("bench-b", "bench-b", "20 HP Bench"),
    ):
        instance_id = f"{pokemon_id}-copy"
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
        make_state(rows, active_id="active"),
    )


def main() -> None:
    index = compile_legal_index(ROOT / "resources")
    semantics = tuple(row for rows in index.values() for row in rows)

    assert len(semantics) == 20003
    assert sum(row.fixed_damage is not None for row in semantics) == 16139
    assert sum(row.take_another_turn for row in semantics) == 13

    counter_rows = tuple(row for row in semantics if row.counter_effect is not None)
    assert len(counter_rows) == 91
    counter_shapes = Counter(
        (row.counter_effect.scope, row.counter_effect.distribution)
        for row in counter_rows
        if row.counter_effect is not None
    )
    assert counter_shapes == Counter(
        {
            ("opponent_any", "distributed"): 35,
            ("opponent_bench", "distributed"): 20,
            ("opponent_active", "fixed"): 13,
            ("opponent_any", "single"): 8,
            ("opponent_bench", "single"): 7,
            ("own_any", "single"): 7,
            ("self", "fixed"): 1,
        }
    )

    timeless = next(
        row
        for row in index["sm5-100"]
        if row.attack_name == "Timeless-GX"
    )
    assert timeless.fixed_damage == 150
    assert timeless.take_another_turn
    assert timeless.skip_pokemon_checkup
    assert timeless.is_gx_attack
    timeless_def = timeless.to_leaf_attack_def()
    assert timeless_def.turn_boundary_effect is not None
    assert timeless_def.turn_boundary_effect.take_another_turn
    assert timeless_def.turn_boundary_effect.skip_pokemon_checkup

    phantom = next(
        row
        for row in index["sv6-130"]
        if row.attack_name == "Phantom Dive"
    )
    assert phantom.fixed_damage == 200
    assert phantom.counter_effect is not None
    assert phantom.counter_effect.scope == "opponent_bench"
    assert phantom.counter_effect.distribution == "distributed"
    assert phantom.counter_effect.total_counters == 6

    board_state = physical_board()
    board = board_state.board
    assert board is not None
    program = materialize_opponent_board_program(
        phantom,
        board,
        counter_allocation=(("bench-a", 4), ("bench-b", 2)),
    )

    haughty = AttackDef(
        HAUGHTY,
        "Haughty Order",
        copy_selector=CopySelector("opponent_revealed"),
        pre_event="reveal_top_10",
        post_event="shuffle_revealed",
    )
    phantom_def = phantom.to_leaf_attack_def()
    attacks = {
        HAUGHTY: haughty,
        phantom_def.attack_id: phantom_def,
    }
    copy = resolve_attack(
        actor_player="P1",
        actor_card_id="p1-persian",
        declared_attack_id=HAUGHTY,
        attacks=attacks,
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
        board_state,
        event_programs={phantom.event_label: program},
        hp_by_pokemon_id={
            "active": 200,
            "bench-a": 40,
            "bench-b": 20,
        },
    )
    assert replay.event_trace[-1].event == "shuffle_revealed"
    assert replay.knocked_out_ids == ("active", "bench-a", "bench-b")

    cursed_drop = next(
        row
        for row in index["sm8-96"]
        if row.attack_name == "Cursed Drop"
    )
    assert cursed_drop.fixed_damage == 0
    assert cursed_drop.counter_effect is not None
    assert cursed_drop.counter_effect.scope == "opponent_any"

    print(
        {
            "legal_attack_rows": len(semantics),
            "supported_fixed_or_effect_only_damage": sum(
                row.fixed_damage is not None for row in semantics
            ),
            "extra_turn_rows": sum(row.take_another_turn for row in semantics),
            "exact_counter_rows": len(counter_rows),
            "counter_shapes": dict(sorted(counter_shapes.items())),
            "phantom_copy_kos": replay.knocked_out_ids,
        }
    )


if __name__ == "__main__":
    main()
