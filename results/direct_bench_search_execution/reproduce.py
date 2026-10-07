from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, BoardState, PokemonCard
from direct_bench_search_execution import (
    DirectBenchPlacement,
    DirectBenchTarget,
    direct_bench_target_from_metadata,
    execute_direct_bench_search,
)
from direct_bench_search_profile_compiler import compile_direct_bench_search_profiles
from identity_materialization import CardInstance, IdentityLedger
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from search_zone_transition import SearchZoneTarget
from stack_knockout_conservation import StackBoardMaterialState
from typed_search_target_allocator import EVOLUTION_POKEMON, TargetGroup


def make_state(bench_count, deck_counts):
    pokemon = []
    instances = []
    for index in range(bench_count + 1):
        pid = f"base-p{index}"
        iid = f"base-card-{index}"
        name = f"Base {index}"
        pokemon.append(BoardPokemon(pid, (PokemonCard(iid, name),), retreat_cost=1))
        instances.append(CardInstance(
            instance_id=iid,
            card_class=f"base-class-{index}",
            card_name=name,
            zone="in_play",
            board_object_id=pid,
        ))
    ledger = IdentityLedger(
        ZoneCountState.from_mapping({
            (card_class, "deck"): count
            for card_class, count in deck_counts.items()
        }),
        tuple(sorted(instances, key=lambda row: row.instance_id)),
    )
    return StackBoardMaterialState(
        ledger,
        BoardState(tuple(pokemon), active_id="base-p0"),
    )


def rejects(fn, text):
    try:
        fn()
    except ValueError as exc:
        assert text in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {text!r}")


profiles = compile_direct_bench_search_profiles(ROOT / "resources")
nest = next(row for row in profiles if row.card_id == "sv1-181")
vip = next(row for row in profiles if row.card_id == "swsh8-225")
call = next(
    row for row in profiles
    if row.card_id == "sv3pt5-16" and row.source_name == "Call for Family"
)

metadata = pokemon_board_metadata_by_id(ROOT / "resources")["sm2-60"]
target_two = direct_bench_target_from_metadata(metadata, copies=2)

base = make_state(3, {"sm2-60": 2})
placed = execute_direct_bench_search(
    base,
    nest,
    targets=(target_two,),
    placements=(DirectBenchPlacement(0, "lele-1", "bench-lele-1"),),
)
assert placed.search_performed
assert placed.after.ledger.exchangeable.count("sm2-60", "deck") == 1
assert placed.after.ledger.instance("lele-1").zone == "in_play"
assert placed.after.ledger.instance("lele-1").board_object_id == "bench-lele-1"
assert placed.after.board is not None
assert len(placed.after.board.bench_ids) == 4
resident = next(row for row in placed.after.board.pokemon if row.pokemon_id == "bench-lele-1")
assert resident.name == "Tapu Lele-GX"
assert not resident.evolution_eligible
assert placed.before.ledger.totals() == placed.after.ledger.totals()

vip_base = make_state(3, {"sm2-60": 2})
vip_two = execute_direct_bench_search(
    vip_base,
    vip,
    targets=(target_two,),
    placements=(
        DirectBenchPlacement(0, "vip-1", "vip-p1"),
        DirectBenchPlacement(0, "vip-2", "vip-p2"),
    ),
)
assert vip_two.after.board is not None
assert len(vip_two.after.board.bench_ids) == 5
assert vip_two.after.ledger.exchangeable.count("sm2-60", "deck") == 0

one_slot = make_state(4, {"sm2-60": 2})
vip_one = execute_direct_bench_search(
    one_slot,
    vip,
    targets=(target_two,),
    placements=(DirectBenchPlacement(0, "one-1", "one-p1"),),
)
assert vip_one.after.board is not None
assert len(vip_one.after.board.bench_ids) == 5
rejects(
    lambda: execute_direct_bench_search(
        one_slot,
        vip,
        targets=(target_two,),
        placements=(
            DirectBenchPlacement(0, "over-1", "over-p1"),
            DirectBenchPlacement(0, "over-2", "over-p2"),
        ),
    ),
    "only 1 Bench slots are open",
)

full = make_state(5, {"sm2-60": 2})
rejects(
    lambda: execute_direct_bench_search(
        full,
        nest,
        targets=(target_two,),
        placements=(),
    ),
    "Trainer direct-Bench search cannot be used with a full Bench",
)
full_call = execute_direct_bench_search(
    full,
    call,
    targets=(target_two,),
    placements=(),
)
assert not full_call.search_performed
assert full_call.skipped_full_bench_attack
assert full_call.before is full_call.after

stale = make_state(3, {"sm2-60": 1})
rejects(
    lambda: execute_direct_bench_search(
        stale,
        nest,
        targets=(target_two,),
        placements=(),
    ),
    "stale direct Bench target capacity",
)

evolution_target = DirectBenchTarget(
    SearchZoneTarget(
        "synthetic-evolution",
        TargetGroup("Synthetic Evolution", 1, frozenset({EVOLUTION_POKEMON})),
    ),
    "Synthetic Evolution",
    retreat_cost=1,
    evolves_from="Synthetic Basic",
)
evolution_state = make_state(3, {"synthetic-evolution": 1})
rejects(
    lambda: execute_direct_bench_search(
        evolution_state,
        nest,
        targets=(evolution_target,),
        placements=(DirectBenchPlacement(0, "evo-1", "evo-p1"),),
    ),
    "does not match",
)

print("direct Bench physical execution regression passed")
print("Nest Ball conserves one exact deck-to-Bench placement")
print("Battle VIP Pass respects output and remaining Bench capacity")
print("full Bench rejects Trainer use and skips the search body of the attack")
print("stale target capacity and Evolution targets are rejected")
