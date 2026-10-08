"""One-file regression for conservative whole-text coverage classification."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_text_coverage_inventory import (
    build_coverage, classify_attack_text, materialize_damage_only_verified,
)
from board_position_state import BoardPokemon, PokemonCard, make_state
from simple_attack_board_semantics import compile_legal_index


def main() -> None:
    index = compile_legal_index(ROOT / "resources")
    inventory = build_coverage(ROOT / "resources")
    by_id = {
        row.attack_id: row
        for row in inventory["rows"]
    }
    assert len(by_id) == inventory["total"] == 19992
    assert sum(inventory["counts"].values()) == inventory["total"]

    witnesses = (
        ("sv6-130", "Jet Headbutt", "plain_fixed_or_gx_rule"),
        ("sv6-130", "Phantom Dive", "exact_damage_counter_clause"),
        ("sm8-96", "Cursed Drop", "exact_damage_counter_clause"),
        ("sm8-94", "Mind Shock", "exact_type_modifier_bypass"),
        ("sm5-100", "Shred", "exact_defender_effect_bypass"),
        ("sm5-100", "Timeless-GX", "exact_extra_turn"),
        ("bw1-3", "Wrap", "exact_special_condition"),
        ("bw1-5", "Leaf Storm", "uncompiled_effect_text"),
        ("bw1-39", "Water Pulse", "exact_special_condition"),
        ("bw1-53", "Poison Sting", "exact_special_condition"),
        ("bw1-24", "Singe", "exact_special_condition"),
        ("bw1-17", "Flame Charge", "uncompiled_effect_text"),
        ("bw1-37", "Aqua Ring", "uncompiled_effect_text"),
        ("bw1-81", "Collect", "uncompiled_effect_text"),
    )
    for card_id, attack_name, expected in witnesses:
        matches = [
            row for row in index[card_id]
            if row.attack_name == attack_name
        ]
        assert len(matches) == 1
        classified = classify_attack_text(matches[0])
        assert classified.kind == expected, (card_id, attack_name, classified)
        assert classified == by_id[matches[0].attack_id]

    all_unguarded = tuple(
        source for entries in index.values() for source in entries
        if source.fixed_damage is not None
        and classify_attack_text(source).kind == "uncompiled_effect_text"
        and not (
            source.has_uncompiled_damage_text
            or source.has_uncompiled_knockout_text
            or source.has_uncompiled_attack_gate
        )
    )
    assert len(all_unguarded) == inventory["uncompiled_unguarded"]
    assert inventory["uncompiled_unguarded"] > 1000
    assert inventory["guarded_uncompiled"] > 500

    board = make_state(
        (
            BoardPokemon("active", (PokemonCard("a", "A"),), retreat_cost=1),
            BoardPokemon("bench", (PokemonCard("b", "B"),), retreat_cost=1),
        ),
        active_id="active",
    )
    safe_plain = next(
        r for r in index["sv6-130"] if r.attack_name == "Jet Headbutt"
    )
    safe_counter = next(
        r for r in index["sv6-130"] if r.attack_name == "Phantom Dive"
    )
    plain_program = materialize_damage_only_verified(safe_plain, board)
    assert plain_program.damage_context.attack.base == 70
    counter_program = materialize_damage_only_verified(
        safe_counter, board, counter_allocation=(("bench", 6),),
    )
    assert counter_program.damage_context.attack.base == 200
    assert counter_program.counter_placements[0].count == 6

    should_refuse = (
        ("bw1-5", "Leaf Storm"),
        ("bw1-17", "Flame Charge"),
        ("bw1-37", "Aqua Ring"),
        ("bw1-81", "Collect"),
        ("sm5-100", "Timeless-GX"),
        ("sm5-100", "Shred"),
        ("sm8-94", "Mind Shock"),
    )
    for card_id, name in should_refuse:
        row = next(r for r in index[card_id] if r.attack_name == name)
        try:
            materialize_damage_only_verified(row, board)
        except ValueError as error:
            assert "additional semantic handlers" in str(error)
        else:
            raise AssertionError((card_id, name))

    verified_damage_only_rows = sum(
        row.kind in ("plain_fixed_or_gx_rule", "exact_damage_counter_clause")
        and "gx_budget" not in row.requires_handlers
        for row in inventory["rows"]
    )

    print({
        "legal_attack_rows": inventory["total"],
        "kinds": inventory["counts"],
        "uncompiled_effect_text_not_caught_by_specific_guards":
            inventory["uncompiled_unguarded"],
        "guarded_uncompiled_effect_text": inventory["guarded_uncompiled"],
        "real_card_witnesses": len(witnesses),
        "verified_damage_only_source_rows": verified_damage_only_rows,
        "verified_materializer_rejection_witnesses": len(should_refuse),
    })


if __name__ == "__main__":
    main()
