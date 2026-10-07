"""Reproduce per-Pokemon board-object movement regressions."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_object_kernel import (  # noqa: E402
    EnergyAttachment,
    ToolAttachment,
    contract_bench,
    evolve,
    legal_retreat_energy_choices,
    make_board,
    make_pokemon,
    next_turn,
    retreat,
    switch_active,
)


def main() -> None:
    dce = EnergyAttachment("energy-dce", "Double Colorless Energy", ("C", "C"))
    lightning = EnergyAttachment("energy-lightning", "Lightning Energy", ("L",))
    fire = EnergyAttachment("energy-fire", "Fire Energy", ("R",))
    hood = ToolAttachment("tool-hood", "Stealthy Hood")

    # Physical instance identity is distinct from database print identity.
    # Two copies of one print must remain legal simultaneous attachments.
    same_print_a = EnergyAttachment(
        "same-print-copy-a",
        "Double Colorless Energy",
        ("C", "C"),
        print_id="same-print",
    )
    same_print_b = EnergyAttachment(
        "same-print-copy-b",
        "Double Colorless Energy",
        ("C", "C"),
        print_id="same-print",
    )
    same_print_active = make_pokemon(
        "same-print-active",
        "Same Print Active",
        energy=(same_print_a, same_print_b),
    )
    same_print_board = make_board(same_print_active)
    same_print_board.validate()
    assert same_print_a.instance_id != same_print_b.instance_id
    assert same_print_a.print_id == same_print_b.print_id

    locked_active = make_pokemon(
        "active-a",
        "Active A",
        energy=(dce, lightning),
        tool=hood,
        temporary_attack_lock=True,
        temporary_retreat_lock=True,
        damage_counters=3,
        special_conditions=("Poisoned",),
        retention_value=20.0,
    )
    bench_b = make_pokemon("bench-b", "Bench B", retention_value=30.0)
    locked_board = make_board(locked_active, (bench_b,))

    assert retreat(
        locked_board,
        "bench-b",
        retreat_cost=1,
        discard_energy_ids=("energy-dce",),
    ) is None

    switched = switch_active(locked_board, "bench-b")
    assert switched is not None
    moved_a = switched.get("active-a")
    assert switched.active_id == "bench-b"
    assert switched.bench_ids == ("active-a",)
    assert moved_a.energy == (dce, lightning)
    assert moved_a.tool == hood
    assert moved_a.damage_counters == 3
    assert not moved_a.pokemon_state.temporary_attack_lock
    assert not moved_a.pokemon_state.temporary_retreat_lock
    assert not moved_a.special_conditions

    retreat_source = make_pokemon(
        "retreat-source",
        "Retreat Source",
        energy=(dce, lightning, fire),
        tool=hood,
        damage_counters=4,
        special_conditions=("Poisoned",),
        temporary_attack_lock=True,
    )
    retreat_target = make_pokemon("retreat-target", "Retreat Target")
    board = make_board(retreat_source, (retreat_target,))

    cost1 = {
        frozenset(choice)
        for choice in legal_retreat_energy_choices(retreat_source, 1)
    }
    assert cost1 == {
        frozenset({"energy-dce"}),
        frozenset({"energy-lightning"}),
        frozenset({"energy-fire"}),
    }

    cost2 = {
        frozenset(choice)
        for choice in legal_retreat_energy_choices(retreat_source, 2)
    }
    assert cost2 == {
        frozenset({"energy-dce"}),
        frozenset({"energy-lightning", "energy-fire"}),
    }

    retreated = retreat(
        board,
        "retreat-target",
        retreat_cost=1,
        discard_energy_ids=("energy-dce",),
    )
    assert retreated is not None
    after_retreat, discarded = retreated
    assert discarded == (dce,)
    assert after_retreat.active_id == "retreat-target"
    assert after_retreat.bench_ids == ("retreat-source",)
    assert after_retreat.retreat_used

    moved_source = after_retreat.get("retreat-source")
    assert moved_source.energy == (lightning, fire)
    assert moved_source.tool == hood
    assert moved_source.damage_counters == 4
    assert not moved_source.pokemon_state.temporary_attack_lock
    assert not moved_source.special_conditions

    switched_back = switch_active(after_retreat, "retreat-source")
    assert switched_back is not None
    assert retreat(
        switched_back,
        "retreat-target",
        retreat_cost=1,
        discard_energy_ids=("energy-lightning",),
    ) is None
    fresh_turn = next_turn(switched_back)
    assert retreat(
        fresh_turn,
        "retreat-target",
        retreat_cost=1,
        discard_energy_ids=("energy-lightning",),
    ) is not None

    asleep = make_pokemon(
        "asleep",
        "Asleep Active",
        energy=(lightning,),
        special_conditions=("Asleep",),
    )
    asleep_board = make_board(asleep, (retreat_target,))
    assert retreat(
        asleep_board,
        "retreat-target",
        retreat_cost=1,
        discard_energy_ids=("energy-lightning",),
    ) is None
    assert switch_active(asleep_board, "retreat-target") is not None

    evolve_source = make_pokemon(
        "evolving",
        "Basic Form",
        tags=("Basic",),
        energy=(dce,),
        tool=hood,
        damage_counters=5,
        special_conditions=("Poisoned",),
        temporary_attack_lock=True,
        temporary_retreat_lock=True,
    )
    evolve_board = make_board(evolve_source, (bench_b,))
    evolved = evolve(
        evolve_board,
        "evolving",
        new_card_name="Stage 1 Form",
        new_tags=("Stage1",),
    )
    assert evolved is not None
    evolved_object = evolved.get("evolving")
    assert evolved_object.card_name == "Stage 1 Form"
    assert evolved_object.tags == frozenset({"Stage1"})
    assert evolved_object.energy == (dce,)
    assert evolved_object.tool == hood
    assert evolved_object.damage_counters == 5
    assert not evolved_object.special_conditions
    assert not evolved_object.pokemon_state.temporary_attack_lock
    assert not evolved_object.pokemon_state.temporary_retreat_lock

    stable_active = make_pokemon("stable-active", "Stable Active")
    core = make_pokemon("core", "Core Bench", retention_value=20.0)
    expendable = make_pokemon(
        "support",
        "Support Bench",
        energy=(dce,),
        tool=hood,
        damage_counters=2,
        retention_value=1.0,
    )
    contraction_board = make_board(
        stable_active,
        (core, expendable),
        bench_capacity=2,
    )
    contracted, removed = contract_bench(contraction_board, new_capacity=1)
    assert [pokemon.object_id for pokemon in removed] == ["support"]
    assert removed[0].energy == (dce,)
    assert removed[0].tool == hood
    assert contracted.active_id == "stable-active"
    assert contracted.bench_ids == ("core",)
    assert {pokemon.object_id for pokemon in contracted.objects} == {
        "stable-active",
        "core",
    }

    print("board-object movement regressions passed")


if __name__ == "__main__":
    main()
