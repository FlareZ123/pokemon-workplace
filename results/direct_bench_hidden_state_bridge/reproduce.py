from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, BoardState, PokemonCard
from deck_search_shuffle_topology import SearchableDeckPhysicalState
from direct_bench_hidden_state_bridge import execute_hidden_direct_bench_trainer_transaction
from direct_bench_search_execution import DirectBenchPlacement, DirectBenchTarget
from direct_bench_search_profile_compiler import compile_direct_bench_search_profiles
from direct_bench_trainer_transaction import DirectBenchTrainerExecutionState
from identity_materialization import CardInstance, IdentityLedger, materialize
from multicopy_zone_state import ZoneCountState
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from search_zone_transition import SearchZoneTarget
from stack_knockout_conservation import StackBoardMaterialState
from top_prize_physical_bridge import actual_joint_groups, belief_truth_probability
from typed_search_target_allocator import BASIC_POKEMON, TargetGroup, enumerate_typed_target_profiles, make_demand

A = "class:A"
X = "class:X"
Y = "class:Y"
F = "class:F"
NEST = "sv1-181"
GROUPS = ("A", "X", "Y")
CARDS = (("A1", A), ("X1", X), ("Y1", Y), ("F1", F), ("F2", F), ("F3", F))


def group(card_class):
    return {"class:A": "A", "class:X": "X", "class:Y": "Y"}.get(card_class)


def composition(prizes):
    return tuple(
        sum(group(card_class) == current for _name, card_class in prizes)
        for current in GROUPS
    )


def choose_target(current):
    a_prized, x_prized, y_prized = current
    if x_prized == 0 and a_prized > 0:
        return "X"
    if y_prized == 0 and a_prized == 0:
        return "Y"
    if x_prized == 0:
        return "X"
    if y_prized == 0:
        return "Y"
    return "PASS"


ordered = tuple(permutations(CARDS, 2))
masses = defaultdict(float)
for prizes in ordered:
    masses[tuple(group(card_class) for _name, card_class in prizes)] += 1.0 / len(ordered)

prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(
        GROUPS,
        2,
        tuple(sorted(masses.items(), key=lambda row: repr(row[0]))),
    )
)
policy = {
    current: {choose_target(current): 1.0}
    for current in {composition(prizes) for prizes in ordered}
}

ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (A, "prize"): 1,
        (X, "deck"): 1,
        (Y, "deck"): 1,
        (F, "prize"): 1,
        (F, "deck"): 2,
        (NEST, "hand"): 1,
    }),
    (
        CardInstance(
            instance_id="active-card",
            card_class="class:active",
            card_name="Active",
            zone="in_play",
            board_object_id="active",
        ),
    ),
)
ledger = materialize(ledger, card_class=A, card_name="A", source_zone="prize", instance_id="prize-a")
ledger = materialize(ledger, card_class=F, card_name="F", source_zone="prize", instance_id="prize-f")
physical = SearchableDeckPhysicalState(ledger, ("prize-a", "prize-f"), (False, False))
board = BoardState(
    (BoardPokemon("active", (PokemonCard("active-card", "Active"),), retreat_cost=1),),
    active_id="active",
)
state = DirectBenchTrainerExecutionState(StackBoardMaterialState(ledger, board))

profile = next(
    row
    for row in compile_direct_bench_search_profiles(ROOT / "resources")
    if row.card_id == NEST
)
targets = (
    DirectBenchTarget(
        SearchZoneTarget(X, TargetGroup("X Basic", 1, frozenset({BASIC_POKEMON}))),
        "X Basic",
        retreat_cost=1,
    ),
    DirectBenchTarget(
        SearchZoneTarget(Y, TargetGroup("Y Basic", 1, frozenset({BASIC_POKEMON}))),
        "Y Basic",
        retreat_cost=1,
    ),
)
demands = (make_demand("basic", "Basic Pokémon"),)
allocation = enumerate_typed_target_profiles(
    (profile.output,),
    tuple(row.search_target.group for row in targets),
    demands,
)
search_x = next(row for row in allocation.actions if row.target_cost == (1, 0))

transition = execute_hidden_direct_bench_trainer_transaction(
    physical,
    state,
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    profile=profile,
    action_card_class=NEST,
    demands=demands,
    targets=targets,
    search_action=search_x,
    placements=(DirectBenchPlacement(0, "searched-x", "bench-x"),),
    target_probability_by_composition=policy,
    observed_target="X",
    group_by_card_class={A: "A", X: "X", Y: "Y"},
    sampled_top_card_class=Y,
    sampled_top_card_name="Y",
    sampled_top_instance_id="top-y",
)

ledger_after = transition.physical_after.ledger
assert transition.selected_target_index == 0
assert ledger_after.exchangeable.count(NEST, "discard") == 1
assert ledger_after.exchangeable.count(X, "hand") == 0
assert ledger_after.instance("searched-x").zone == "in_play"
assert ledger_after.instance("searched-x").board_object_id == "bench-x"
assert ledger_after.instance("top-y").zone == "deck_top"
assert transition.state_after.material.ledger == transition.physical_after.ledger
assert transition.state_after.material.board is not None
assert "bench-x" in transition.state_after.material.board.bench_ids

actor = transition.beliefs_after.belief_for("actor")
observer = transition.beliefs_after.belief_for("observer")
assert isclose(actor.top_probability("Y"), 1.0 / 3.0, abs_tol=1e-12)
assert isclose(observer.top_probability("Y"), 1.0 / 7.0, abs_tol=1e-12)

top_group, prize_groups = actual_joint_groups(
    transition.physical_after,
    {A: "A", X: "X", Y: "Y"},
)
assert top_group == "Y"
assert prize_groups == ("A", None)
for belief in (actor, observer):
    assert belief_truth_probability(
        belief,
        top_group=top_group,
        prize_groups=prize_groups,
    ) > 0.0

assert transition.physical_before.ledger.totals() == transition.physical_after.ledger.totals()

print("hidden direct-Bench Trainer regression passed")
print("Nest Ball places X in play, never in hand, then shuffles to exact top Y")
print("actor top Y=1/3; observer top Y=1/7 after public target X")
print("board, hidden physical state, and observer truth support remain synchronized")
