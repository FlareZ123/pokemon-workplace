from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, BoardState, PokemonCard
from direct_bench_search_execution import DirectBenchPlacement, direct_bench_target_from_metadata
from direct_bench_search_profile_compiler import compile_direct_bench_search_profiles, project_direct_bench_trainer_profile
from direct_bench_trainer_transaction import DIRECT_BENCH_SELECTED_ZONE, DirectBenchTrainerExecutionState, execute_direct_bench_trainer_transaction
from identity_materialization import CardInstance, IdentityLedger
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from stack_knockout_conservation import StackBoardMaterialState
from typed_search_target_allocator import enumerate_typed_target_profiles, make_demand


def make_material(bench_count):
    pokemon = []
    instances = []
    for i in range(bench_count + 1):
        pid = f"base-p{i}"
        iid = f"base-card-{i}"
        name = f"Base {i}"
        pokemon.append(BoardPokemon(pid, (PokemonCard(iid, name),), retreat_cost=1))
        instances.append(CardInstance(
            instance_id=iid,
            card_class=f"base-class-{i}",
            card_name=name,
            zone="in_play",
            board_object_id=pid,
        ))
    ledger = IdentityLedger(
        ZoneCountState.from_mapping({
            ("sv1-181", "hand"): 1,
            ("sm2-60", "deck"): 1,
        }),
        tuple(sorted(instances, key=lambda row: row.instance_id)),
    )
    return StackBoardMaterialState(
        ledger,
        BoardState(tuple(pokemon), active_id="base-p0"),
    )


profiles = compile_direct_bench_search_profiles(ROOT / "resources")
profile = next(row for row in profiles if row.card_id == "sv1-181")
metadata = pokemon_board_metadata_by_id(ROOT / "resources")["sm2-60"]
target = direct_bench_target_from_metadata(metadata, copies=1)
demand = make_demand("needed Basic", "Basic Pokémon")
shared = project_direct_bench_trainer_profile(profile)
allocation = enumerate_typed_target_profiles(
    shared.base_outputs,
    (target.search_target.group,),
    (demand,),
)
action = next(
    row for row in allocation.actions
    if row.output == (1,) and row.target_cost == (1,) and row.axis_usage == (1,)
)

before = DirectBenchTrainerExecutionState(make_material(3))
tx = execute_direct_bench_trainer_transaction(
    before,
    profile,
    action_card_class="sv1-181",
    demands=(demand,),
    targets=(target,),
    search_action=action,
    placements=(DirectBenchPlacement(0, "lele-nest", "bench-lele"),),
)

ledger = tx.after.material.ledger
assert tx.trainer_transaction.search_destination_zone == DIRECT_BENCH_SELECTED_ZONE
assert ledger.exchangeable.count("sv1-181", "discard") == 1
assert ledger.exchangeable.count("sm2-60", "deck") == 0
assert ledger.exchangeable.count("sm2-60", "hand") == 0
assert all(
    zone != DIRECT_BENCH_SELECTED_ZONE
    for _card_class, zone, _count in ledger.exchangeable.counts
)
assert ledger.instance("lele-nest").zone == "in_play"
assert ledger.instance("lele-nest").board_object_id == "bench-lele"
assert tx.after.material.board is not None
assert len(tx.after.material.board.bench_ids) == 4
assert tx.before.material.ledger.totals() == tx.after.material.ledger.totals()
assert tx.before.budget == tx.after.budget

full = DirectBenchTrainerExecutionState(make_material(5))
try:
    execute_direct_bench_trainer_transaction(
        full,
        profile,
        action_card_class="sv1-181",
        demands=(demand,),
        targets=(target,),
        search_action=action,
        placements=(DirectBenchPlacement(0, "full-copy", "full-pokemon"),),
    )
except ValueError as exc:
    assert "full Bench" in str(exc)
else:
    raise AssertionError("full-Bench direct Trainer should be rejected")

print("direct Bench Trainer transaction regression passed")
print("searched Basic uses private staging and becomes an in-play board object")
print("Nest Ball enters discard, target never enters hand, totals stay conserved")
print("full Bench is rejected before the Trainer transaction executes")
