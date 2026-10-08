"""One-file live card corpus regression for literal damage target geometry."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from attack_damage_target_geometry import catalog, plan_literal_damage_targets
from board_position_state import BoardPokemon, PokemonCard, make_state
from simple_attack_board_semantics import compile_legal_index


def main() -> None:
    index = compile_legal_index(ROOT / "resources")
    result = catalog(ROOT / "resources")
    rows = {r.attack_id: r for r in result["rows"]}

    witnesses = (
        ("bw10-19", "Sharpshooting", 0, 30, "opponent_any", 1, None),
        ("bw11-43", "Glaciate", 0, 30, "opponent_all", None, None),
        ("bw11-19", "Split Bomb", 0, 40, "opponent_any", 2, None),
        ("bw5-63", "Night Spear", 90, 30, "opponent_bench", 1, None),
        ("bw7-89", "Hammerhead", 30, 30, "opponent_bench", 1, None),
        ("me1-81", "Stony Kick", 20, 20, "opponent_bench", 1, None),
        ("me55-64", "Photon Bullets", 0, 50, "opponent_all", None, "ex"),
        ("sm8-121", "Dusty Ruckus", 130, 30, "opponent_bench", None, "Basic"),
    )
    for card_id, attack_name, active, text_damage, scope, count, filter_name in witnesses:
        matched = [r for r in result["rows"] if r.card_id == card_id and r.attack_name == attack_name]
        assert len(matched) == 1, (card_id, attack_name, matched)
        row = matched[0]
        assert (
            row.printed_active_damage, row.text_damage, row.target_scope,
            row.target_count, row.target_filter,
        ) == (active, text_damage, scope, count, filter_name), row
        assert index[card_id][row.attack_index].has_uncompiled_damage_text

    excluded = (
        ("sv6-130", "Phantom Dive"),
        ("sm12-165", "Puffy Smashers-GX"),
    )
    for card_id, name in excluded:
        attack_ids = {
            f"{card_id}:attack:{i}"
            for i, row in enumerate(index[card_id])
            if row.attack_name == name
        }
        assert not attack_ids.intersection(rows), (card_id, name)

    board = make_state(
        (
            BoardPokemon("active", (PokemonCard("a1", "A"),), retreat_cost=1),
            BoardPokemon("bench-basic", (PokemonCard("b1", "B"),), retreat_cost=1),
            BoardPokemon("bench-ex", (PokemonCard("c1", "C"),), retreat_cost=1),
        ),
        active_id="active",
    )
    tags = {
        "active": frozenset(("Basic", "ex")),
        "bench-basic": frozenset(("Basic",)),
        "bench-ex": frozenset(("Evolution", "ex")),
    }

    def by_name(card_id: str, name: str):
        matching = [
            row for row in result["rows"]
            if row.card_id == card_id and row.attack_name == name
        ]
        assert len(matching) == 1
        return matching[0]

    glaciate = plan_literal_damage_targets(by_name("bw11-43", "Glaciate"), board)
    assert glaciate.selected_text_targets == (
        "active", "bench-basic", "bench-ex",
    )
    assert tuple((r.amount, r.ignore_weakness_resistance) for r in glaciate.instructions) == (
        (30, False), (30, True), (30, True),
    )

    night_spear = plan_literal_damage_targets(
        by_name("bw5-63", "Night Spear"), board,
        selected_target_ids=("bench-ex",),
    )
    assert tuple((r.target_id, r.amount, r.source) for r in night_spear.instructions) == (
        ("active", 90, "printed"),
        ("bench-ex", 30, "attack_text"),
    )

    split = plan_literal_damage_targets(
        by_name("bw11-19", "Split Bomb"), board,
        selected_target_ids=("active", "bench-basic"),
    )
    assert len(split.instructions) == 2
    assert split.instructions[0].ignore_weakness_resistance is False
    assert split.instructions[1].ignore_weakness_resistance is True

    tyranitar = plan_literal_damage_targets(
        by_name("sm8-121", "Dusty Ruckus"),
        board, target_tags_by_id=tags,
    )
    assert tyranitar.selected_text_targets == ("bench-basic",)
    assert tuple(r.amount for r in tyranitar.instructions) == (130, 30)

    photon = plan_literal_damage_targets(
        by_name("me55-64", "Photon Bullets"),
        board, target_tags_by_id=tags,
    )
    assert photon.selected_text_targets == ("active", "bench-ex")
    assert all(r.amount == 50 for r in photon.instructions)

    failures = (
        (by_name("bw11-19", "Split Bomb"), ("active",)),
        (by_name("bw11-19", "Split Bomb"), ("active", "active")),
        (by_name("bw5-63", "Night Spear"), ("active",)),
        (by_name("bw11-43", "Glaciate"), ("active",)),
    )
    for geometry, selected in failures:
        try:
            plan_literal_damage_targets(
                geometry, board, selected_target_ids=selected
            )
        except ValueError:
            pass
        else:
            raise AssertionError((geometry.attack_id, selected))

    try:
        plan_literal_damage_targets(
            by_name("me55-64", "Photon Bullets"), board
        )
    except ValueError as exc:
        assert "subtype eligibility" in str(exc)
    else:
        raise AssertionError("missing target tags must be rejected")

    # Check complete selection semantics for every compiled live card row.
    for geometry in result["rows"]:
        candidates = (
            ("active", "bench-basic", "bench-ex")
            if geometry.target_scope in {"opponent_any", "opponent_all"}
            else ("bench-basic", "bench-ex")
        )
        eligible = tuple(
            target for target in candidates
            if geometry.target_filter is None
            or geometry.target_filter in tags[target]
        )
        selected = (
            eligible[:geometry.target_count]
            if geometry.target_count is not None else ()
        )
        plan = plan_literal_damage_targets(
            geometry, board, selected_target_ids=selected,
            target_tags_by_id=tags,
        )
        assert len(plan.selected_text_targets) == (
            min(geometry.target_count, len(eligible))
            if geometry.target_count is not None else len(eligible)
        )
        assert len(plan.instructions) == (
            len(plan.selected_text_targets) + int(geometry.printed_active_damage > 0)
        )
        assert all(
            instruction.ignore_weakness_resistance == (
                instruction.target_id != "active"
            )
            for instruction in plan.instructions
        )

    # The rulebook's "choose as many as you can" semantics when a 2-Bench
    # attack has only one eligible Benched Pokémon.
    small_board = make_state(
        (board.get("active"), board.get("bench-basic")),
        active_id="active",
    )
    flame_burst = plan_literal_damage_targets(
        by_name("bw1-22", "Flame Burst"), small_board,
        selected_target_ids=("bench-basic",),
    )
    assert tuple(i.amount for i in flame_burst.instructions) == (20, 20)

    assert result["total_rows"] > 100
    assert result["total_rows"] == result["effect_only_rows"] + result["supplemental_rows"]
    assert all(row.text_damage > 0 for row in result["rows"])
    assert all(
        (row.target_count is None or 1 <= row.target_count <= 6)
        for row in result["rows"]
    )
    print({
        "exact_full_text_rows": result["total_rows"],
        "effect_only_rows": result["effect_only_rows"],
        "supplemental_rows": result["supplemental_rows"],
        "shape_counts": result["shapes"],
        "witnesses_verified": len(witnesses),
        "excluded_conditional_or_counter_witnesses": len(excluded),
        "allocation_planner_rows_verified": len(result["rows"]),
        "selection_failure_controls": len(failures) + 1,
    })


if __name__ == "__main__":
    main()
