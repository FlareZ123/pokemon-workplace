"""Single-file regression for exact print-HP-constrained direct Bench Items."""

from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, BoardState, PokemonCard
from direct_bench_search_execution import (
    DirectBenchPlacement,
    direct_bench_target_from_metadata,
)
from direct_bench_trainer_transaction import (
    DIRECT_BENCH_SELECTED_ZONE,
    DirectBenchTrainerExecutionState,
)
from hp_bounded_direct_bench_transaction import (
    compile_hp_bounded_direct_bench_profiles,
    execute_hp_bounded_direct_bench_trainer_transaction,
)
from identity_materialization import CardInstance, IdentityLedger
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from pokemon_card_profile import build_pokemon_card_profile_index
from stack_knockout_conservation import StackBoardMaterialState
from typed_search_target_allocator import (
    enumerate_typed_target_profiles,
    make_demand,
)

POFFIN = "sv5-144"
ELGYEM = "sm11-90"  # 60 printed HP
SPRIGATITO = "sv1-13"  # 70 printed HP, exact inclusive boundary
MURKROW = "me55-93"  # 80 printed HP, ineligible


def make_state(bench_count: int, deck_counts: dict[str, int]):
    residents = []
    instances = []
    for i in range(bench_count + 1):
        board_id = f"starting-{i}"
        instance_id = f"starting-card-{i}"
        name = f"Starting {i}"
        residents.append(
            BoardPokemon(
                board_id,
                (PokemonCard(instance_id, name),),
                retreat_cost=1,
            )
        )
        instances.append(
            CardInstance(
                instance_id=instance_id,
                card_class=f"starting-class-{i}",
                card_name=name,
                zone="in_play",
                board_object_id=board_id,
            )
        )

    mapping = {(POFFIN, "hand"): 1}
    for card_id, count in deck_counts.items():
        mapping[(card_id, "deck")] = count
    ledger = IdentityLedger(
        ZoneCountState.from_mapping(mapping),
        tuple(instances),
    )
    material = StackBoardMaterialState(
        ledger,
        BoardState(tuple(residents), active_id="starting-0"),
    )
    return DirectBenchTrainerExecutionState(material)


def rejects(fn, fragment: str):
    try:
        fn()
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {fragment!r}")


profiles = compile_hp_bounded_direct_bench_profiles(ROOT / "resources")
found = {row.direct.card_id for row in profiles}
assert found == {
    "sv5-144", "sv6-223", "sv8pt5-101", "me1-167", "me2pt5-184"
}, found
profile = next(row for row in profiles if row.direct.card_id == POFFIN)
assert profile.max_hp == 70
assert profile.direct.output.max_units == 2
assert profile.direct.output.label == "Basic Pokémon"
assert profile.direct.explicit_up_to

metadata = pokemon_board_metadata_by_id(ROOT / "resources")
card_profiles = build_pokemon_card_profile_index(ROOT / "resources")
assert [card_profiles[c].hp for c in (ELGYEM, SPRIGATITO, MURKROW)] == [60, 70, 80]
targets = tuple(
    direct_bench_target_from_metadata(metadata[c], copies=1)
    for c in (ELGYEM, SPRIGATITO)
)
high_hp = direct_bench_target_from_metadata(metadata[MURKROW], copies=1)
demand = make_demand("needed Basics", "Basic Pokémon", copies=2)
allocation = enumerate_typed_target_profiles(
    (profile.direct.output,),
    tuple(row.search_target.group for row in targets),
    (demand,),
)
both_action = next(row for row in allocation.actions if row.target_cost == (1, 1))
one_action = next(row for row in allocation.actions if row.target_cost == (1, 0))
both_placements = (
    DirectBenchPlacement(0, "poffin-elgyem", "bench-elgyem"),
    DirectBenchPlacement(1, "poffin-sprigatito", "bench-sprigatito"),
)

def execute(state, *, selected_targets=targets, action=both_action,
            placements=both_placements, item=POFFIN):
    return execute_hp_bounded_direct_bench_trainer_transaction(
        state,
        profile,
        action_card_class=item,
        demands=(demand,),
        targets=selected_targets,
        search_action=action,
        placements=placements,
        board_metadata_by_id=metadata,
        card_profiles_by_id=card_profiles,
    )


before = make_state(3, {ELGYEM: 1, SPRIGATITO: 1})
transaction = execute(before)
ledger = transaction.after.material.ledger
assert ledger.exchangeable.count(POFFIN, "discard") == 1
assert ledger.exchangeable.count(ELGYEM, "deck") == 0
assert ledger.exchangeable.count(SPRIGATITO, "deck") == 0
for print_id, instance_id, board_id in (
    (ELGYEM, "poffin-elgyem", "bench-elgyem"),
    (SPRIGATITO, "poffin-sprigatito", "bench-sprigatito"),
):
    assert ledger.exchangeable.count(print_id, "hand") == 0
    assert ledger.instance(instance_id).zone == "in_play"
    assert ledger.instance(instance_id).board_object_id == board_id
assert transaction.after.material.board is not None
assert len(transaction.after.material.board.bench_ids) == 5
assert all(
    not row.evolution_eligible
    for row in transaction.after.material.board.pokemon
    if row.pokemon_id in {"bench-elgyem", "bench-sprigatito"}
)
assert all(
    zone != DIRECT_BENCH_SELECTED_ZONE
    for _card_id, zone, _count in ledger.exchangeable.counts
)
assert transaction.before.material.ledger.totals() == ledger.totals()
assert transaction.before.budget == transaction.after.budget

one_slot = make_state(4, {ELGYEM: 1, SPRIGATITO: 1})
one = execute(
    one_slot,
    action=one_action,
    placements=(DirectBenchPlacement(0, "single-elgyem", "single-bench"),),
)
assert one.after.material.board is not None
assert len(one.after.material.board.bench_ids) == 5
assert one.after.material.ledger.exchangeable.count(SPRIGATITO, "deck") == 1

rejects(
    lambda: execute(make_state(5, {ELGYEM: 1, SPRIGATITO: 1})),
    "full Bench",
)
rejects(
    lambda: execute(make_state(3, {ELGYEM: 1, SPRIGATITO: 1}),
                    selected_targets=(targets[0], high_hp)),
    "exceeding search limit 70",
)
rejects(
    lambda: execute(make_state(3, {ELGYEM: 1, SPRIGATITO: 1}),
                    selected_targets=(targets[0],
                                      replace(targets[1], card_name="False Sprigatito"))),
    "metadata disagrees with exact print",
)
rejects(
    lambda: execute(make_state(3, {ELGYEM: 1, SPRIGATITO: 0})),
    "stale direct-Bench target capacity",
)
rejects(
    lambda: execute(make_state(3, {ELGYEM: 1, SPRIGATITO: 1}), item="me1-167"),
    "played Item print disagrees",
)

print("HP-bounded direct-Bench Item regression passed")
print(f"compiled {len(profiles)} legal Buddy-Buddy Poffin prints, maximum 2, HP ceiling 70")
print("60 HP + 70 HP accepted, 80 HP excluded from the target universe")
print("both-target and one-open-slot physical transactions conserve all cards")
print("played Item discarded, no searched target enters hand or persists in staging")
print("full Bench, stale counts, forged target metadata, wrong Item print rejected")
