"""SFT: typed Item/Trainer lock gating for HP-limited Poffin search."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, BoardState, PokemonCard
from card_action_metadata import card_action_metadata_by_id
from direct_bench_search_execution import (
    DirectBenchPlacement,
    direct_bench_target_from_metadata,
)
from direct_bench_trainer_transaction import DirectBenchTrainerExecutionState
from hp_bounded_direct_bench_transaction import compile_hp_bounded_direct_bench_profiles
from identity_materialization import CardInstance, IdentityLedger
from locked_hp_direct_bench_transaction import execute_locked_hp_direct_bench_trainer_transaction
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from pokemon_card_profile import build_pokemon_card_profile_index
from source_scoped_action_restrictions import build_source_scoped_action_restrictions
from stack_knockout_conservation import StackBoardMaterialState
from typed_search_target_allocator import enumerate_typed_target_profiles, make_demand


POFFIN = "sv5-144"
ELGYEM = "sm11-90"


def make_state(bench_count=2):
    residents = []
    instances = []
    for i in range(bench_count + 1):
        pid, iid = f"starter-{i}", f"starter-card-{i}"
        name = f"Starter {i}"
        residents.append(
            BoardPokemon(pid, (PokemonCard(iid, name),), retreat_cost=1)
        )
        instances.append(
            CardInstance(iid, f"starter-class-{i}", name,
                         zone="in_play", board_object_id=pid)
        )
    ledger = IdentityLedger(
        ZoneCountState.from_mapping({
            (POFFIN, "hand"): 1,
            (ELGYEM, "deck"): 1,
        }),
        tuple(instances),
    )
    return DirectBenchTrainerExecutionState(
        StackBoardMaterialState(
            ledger, BoardState(tuple(residents), active_id="starter-0")
        )
    )


def rejects(fn, text):
    try:
        fn()
    except ValueError as exc:
        assert text in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {text!r}")


profile = next(
    p for p in compile_hp_bounded_direct_bench_profiles(ROOT / "resources")
    if p.direct.card_id == POFFIN
)
metadata = pokemon_board_metadata_by_id(ROOT / "resources")
card_profiles = build_pokemon_card_profile_index(ROOT / "resources")
actions = card_action_metadata_by_id(ROOT / "resources")
restrict = build_source_scoped_action_restrictions(ROOT / "resources")
assert actions[POFFIN].card_kind == "item"
assert "ace_spec" not in actions[POFFIN].tags

vileplume = next(
    x for x in restrict
    if x.card_id == "xy7-3" and "item" in x.dimensions
)
spiritomb = next(
    x for x in restrict
    if x.card_id == "bw11-87" and "ace_spec" in x.dimensions
)
dark_moon = next(
    x for x in restrict
    if x.card_id == "sm11-125" and "trainer" in x.dimensions
)
assert vileplume.prohibited_source_zone == "hand"
assert spiritomb.prohibited_source_zone == "hand"
assert dark_moon.prohibited_source_zone == "hand"

target = direct_bench_target_from_metadata(metadata[ELGYEM], copies=1)
demand = make_demand("one Basic", "Basic Pokémon")
allocation = enumerate_typed_target_profiles(
    (profile.direct.output,), (target.search_target.group,), (demand,)
)
search = next(row for row in allocation.actions if row.target_cost == (1,))
placement = (DirectBenchPlacement(0, "searched-elgyem", "bench-elgyem"),)


def execute(state, restrictions=()):
    return execute_locked_hp_direct_bench_trainer_transaction(
        state,
        profile,
        action_card_class=POFFIN,
        active_restrictions=restrictions,
        action_metadata_by_id=actions,
        demands=(demand,),
        targets=(target,),
        search_action=search,
        placements=placement,
        board_metadata_by_id=metadata,
        card_profiles_by_id=card_profiles,
    )


before = make_state()
plain = execute(before)
ace_only = execute(before, (spiritomb,))
for transaction in (plain, ace_only):
    assert transaction.after.material.ledger.exchangeable.count(POFFIN, "discard") == 1
    assert transaction.after.material.ledger.instance("searched-elgyem").zone == "in_play"
    assert transaction.before.material.ledger.totals() == transaction.after.material.ledger.totals()
    assert transaction.after.channels == before.channels
    assert transaction.after.budget == before.budget

rejects(
    lambda: execute(before, (vileplume,)),
    "prohibited by active restrictions",
)
rejects(
    lambda: execute(before, (dark_moon,)),
    "prohibited by active restrictions",
)
rejects(
    lambda: execute(before, (spiritomb, vileplume)),
    "prohibited by active restrictions",
)
rejects(
    lambda: execute(make_state(5)),
    "full Bench",
)

# The Item lock is a permission check, not a state mutation: a rejected
# attempt leaves the original physical card, board and action quota untouched.
assert before.material.ledger.exchangeable.count(POFFIN, "hand") == 1
assert before.material.ledger.exchangeable.count(ELGYEM, "deck") == 1
assert "bench-elgyem" not in before.material.board.bench_ids

print("source-scoped locked Poffin Bench transaction regression passed")
print("no lock and ACE SPEC-only Spiritomb lock both permit ordinary Poffin")
print("Vileplume Item lock and Dark Moon Trainer lock each prohibit hand Item play")
print("rejections preserve physical state; legal search conserves cards and channels")
