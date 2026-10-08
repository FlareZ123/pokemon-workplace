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

    supported_damage_rows = sum(row.fixed_damage is not None for row in semantics)
    extra_turn_rows = sum(row.take_another_turn for row in semantics)

    counter_rows = tuple(row for row in semantics if row.counter_effect is not None)
    counter_shapes = Counter(
        (row.counter_effect.scope, row.counter_effect.distribution)
        for row in counter_rows
        if row.counter_effect is not None
    )
    assert len(semantics) == 19992
    assert supported_damage_rows == 16128
    assert extra_turn_rows == 13
    assert len(counter_rows) == 91
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

    # Blank printed damage may still deal direct effect-text damage.
    # Numeric printed damage can also be followed by additional Bench damage.
    # Until these clauses have executable semantics, full board programs
    # must fail closed rather than silently dropping them.
    sharpshooting = next(
        row for row in index["bw10-19"]
        if row.attack_name == "Sharpshooting"
    )
    night_spear = next(
        row for row in index["bw5-63"]
        if row.attack_name == "Night Spear"
    )
    assert sharpshooting.fixed_damage == 0
    assert sharpshooting.has_uncompiled_damage_text
    assert night_spear.fixed_damage == 90
    assert night_spear.has_uncompiled_damage_text
    assert not phantom.has_uncompiled_damage_text
    assert not cursed_drop.has_uncompiled_damage_text
    for incomplete in (sharpshooting, night_spear):
        try:
            materialize_opponent_board_program(incomplete, board)
        except ValueError as error:
            assert "uncompiled damage text" in str(error)
        else:
            raise AssertionError(f"silently materialized {incomplete.attack_id}")

    bring_down = next(
        row for row in index["me1-41"]
        if row.attack_name == "Bring Down"
    )
    terminal_period = next(
        row for row in index["me1-86"]
        if row.attack_name == "Terminal Period"
    )
    for incomplete in (bring_down, terminal_period):
        assert incomplete.fixed_damage == 0
        assert incomplete.has_uncompiled_knockout_text
        try:
            materialize_opponent_board_program(incomplete, board)
        except ValueError as error:
            assert "uncompiled Knock Out text" in str(error)
        else:
            raise AssertionError(f"silently materialized {incomplete.attack_id}")

    uncompiled_knockout_rows = sum(
        row.has_uncompiled_knockout_text for row in semantics
        if row.fixed_damage is not None
    )
    uncompiled_blank_knockout_rows = sum(
        row.has_uncompiled_knockout_text and row.raw_damage == ""
        for row in semantics
    )

    uncompiled_damage_rows = sum(
        row.has_uncompiled_damage_text for row in semantics
        if row.fixed_damage is not None
    )
    uncompiled_blank_damage_rows = sum(
        row.has_uncompiled_damage_text and row.raw_damage == ""
        for row in semantics
    )

    print(
        {
            "legal_attack_rows": len(semantics),
            "supported_fixed_or_effect_only_damage": supported_damage_rows,
            "uncompiled_damage_text_rows_with_numeric_or_blank_field": uncompiled_damage_rows,
            "uncompiled_blank_damage_rows": uncompiled_blank_damage_rows,
            "uncompiled_knockout_text_rows": uncompiled_knockout_rows,
            "uncompiled_blank_knockout_rows": uncompiled_blank_knockout_rows,
            "extra_turn_rows": extra_turn_rows,
            "exact_counter_rows": len(counter_rows),
            "counter_shapes": dict(sorted(counter_shapes.items())),
            "phantom_copy_kos": replay.knocked_out_ids,
        }
    )


if __name__ == "__main__":
    main()
