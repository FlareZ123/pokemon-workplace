"""SFT: Poffin two-target public print observation, K1 and exact top state."""

from collections import defaultdict
from dataclasses import replace
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, BoardState, PokemonCard
from deck_search_shuffle_topology import SearchableDeckPhysicalState
from direct_bench_search_execution import DirectBenchPlacement, direct_bench_target_from_metadata
from direct_bench_trainer_transaction import DirectBenchTrainerExecutionState
from hp_bounded_direct_bench_transaction import compile_hp_bounded_direct_bench_profiles
from hp_bounded_hidden_direct_bench_bridge import (
    execute_hp_bounded_hidden_direct_bench_trainer_transaction,
    selected_print_multiset_label,
)
from identity_materialization import CardInstance, IdentityLedger, materialize
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from pokemon_card_profile import build_pokemon_card_profile_index
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from stack_knockout_conservation import StackBoardMaterialState
from top_prize_physical_bridge import actual_joint_groups, belief_truth_probability
from typed_search_target_allocator import enumerate_typed_target_profiles, make_demand


POFFIN = "sv5-144"
L = "sm11-90"  # Elgyem, 60 HP
S = "sv1-13"  # Sprigatito, 70 HP
H = "me55-93"  # Murkrow, 80 HP
F = "class:filler"
GROUPS = ("L", "S", "H")
GROUP_OF = {L: "L", S: "S", H: "H"}
HIDDEN_POOL = (("L1", L), ("S1", S), ("H1", H),
               ("F1", F), ("F2", F), ("F3", F))


def rejects(fn, fragment: str):
    try:
        fn()
    except ValueError as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError containing {fragment!r}")


def composition(prize_objects):
    return tuple(
        sum(GROUP_OF.get(card_class) == group
            for _iid, card_class in prize_objects)
        for group in GROUPS
    )


ordered = tuple(permutations(HIDDEN_POOL, 2))
masses = defaultdict(float)
for prize_objects in ordered:
    state = tuple(GROUP_OF.get(card_class) for _iid, card_class in prize_objects)
    masses[state] += 1.0 / len(ordered)
prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(
        GROUPS,
        2,
        tuple(sorted(masses.items(), key=lambda row: repr(row[0]))),
    )
)

metadata = pokemon_board_metadata_by_id(ROOT / "resources")
card_profiles = build_pokemon_card_profile_index(ROOT / "resources")
profile = next(
    row for row in compile_hp_bounded_direct_bench_profiles(ROOT / "resources")
    if row.direct.card_id == POFFIN
)
targets = tuple(
    direct_bench_target_from_metadata(metadata[print_id], copies=1)
    for print_id in (L, S)
)
demand = make_demand("two Basics", "Basic Pokémon", copies=2)
allocation = enumerate_typed_target_profiles(
    (profile.direct.output,),
    tuple(row.search_target.group for row in targets),
    (demand,),
)
action = next(
    row for row in allocation.actions
    if row.target_cost == (1, 1) and row.axis_usage == (2,)
)
public_label = selected_print_multiset_label(targets, action)
assert public_label == "sm11-90|sv1-13"
assert selected_print_multiset_label(targets[::-1], action) == public_label

policy = {}
for prize_objects in ordered:
    key = composition(prize_objects)
    both_available = key[0] == key[1] == 0
    policy[key] = {public_label if both_available else "OTHER": 1.0}

ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (POFFIN, "hand"): 1,
        (L, "deck"): 1,
        (S, "deck"): 1,
        (H, "prize"): 1,
        (F, "prize"): 1,
        (F, "deck"): 2,
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
ledger = materialize(
    ledger, card_class=H, card_name="Murkrow",
    source_zone="prize", instance_id="prize-h",
)
ledger = materialize(
    ledger, card_class=F, card_name="Filler",
    source_zone="prize", instance_id="prize-f",
)
physical = SearchableDeckPhysicalState(
    ledger, ("prize-h", "prize-f"), (False, False)
)
board = BoardState(
    (BoardPokemon("active", (PokemonCard("active-card", "Active"),),
                  retreat_cost=1),),
    active_id="active",
)
state = DirectBenchTrainerExecutionState(StackBoardMaterialState(ledger, board))


def execute(*, candidate_targets=targets, selection_policy=policy):
    return execute_hp_bounded_hidden_direct_bench_trainer_transaction(
        physical,
        state,
        (("actor", prior), ("observer", prior)),
        actor_id="actor",
        profile=profile,
        action_card_class=POFFIN,
        demands=(demand,),
        targets=candidate_targets,
        search_action=action,
        placements=(
            DirectBenchPlacement(0, "bench-card-l", "bench-l"),
            DirectBenchPlacement(1, "bench-card-s", "bench-s"),
        ),
        target_probability_by_composition=selection_policy,
        group_by_card_class=GROUP_OF,
        sampled_top_card_class=F,
        sampled_top_card_name="Filler",
        sampled_top_instance_id="sampled-filler-top",
        board_metadata_by_id=metadata,
        card_profiles_by_id=card_profiles,
    )


result = execute()
after = result.physical_after.ledger
assert result.selected_target_indices == (0, 1)
assert result.state_after.material.ledger == after
assert after.exchangeable.count(POFFIN, "discard") == 1
assert after.exchangeable.count(L, "hand") == 0
assert after.exchangeable.count(S, "hand") == 0
assert after.instance("bench-card-l").zone == "in_play"
assert after.instance("bench-card-s").zone == "in_play"
assert after.instance("sampled-filler-top").zone == "deck_top"
assert result.state_after.material.board is not None
assert {"bench-l", "bench-s"} <= set(result.state_after.material.board.bench_ids)
assert physical.ledger.totals() == after.totals()
assert not any(zone == "direct_bench_selected"
               for _card_class, zone, _count in after.exchangeable.counts)

actor = result.beliefs_after.belief_for("actor")
observer = result.beliefs_after.belief_for("observer")
assert isclose(actor.top_probability("H"), 0.0, abs_tol=1e-12)
assert isclose(observer.top_probability("H"), 1.0 / 4.0, abs_tol=1e-12)
assert isclose(actor.top_probability(None), 1.0, abs_tol=1e-12)
assert isclose(observer.top_probability(None), 3.0 / 4.0, abs_tol=1e-12)

top_group, prize_groups = actual_joint_groups(result.physical_after, GROUP_OF)
assert top_group is None
assert prize_groups == ("H", None)
for belief in (actor, observer):
    assert belief_truth_probability(
        belief, top_group=top_group, prize_groups=prize_groups
    ) > 0.0

rejected_targets = (
    targets[0],
    direct_bench_target_from_metadata(metadata[H], copies=1),
)
rejects(
    lambda: execute(candidate_targets=rejected_targets),
    "exceeding search limit 70",
)
rejects(
    lambda: execute(candidate_targets=(
        targets[0], replace(targets[1], card_name="Faked 70HP Pokémon")
    )),
    "metadata disagrees with exact print",
)
wrong_policy = {key: {"OTHER": 1.0} for key in policy}
rejects(
    lambda: execute(selection_policy=wrong_policy),
    "zero policy probability",
)

print("HP-bounded two-target hidden Bench search bridge regression passed")
print(f"public observation is the actual sorted print multiset {public_label}")
print("both selected Pokémon in play; exact Poffin discarded, no hand/staging leaks")
print("actor K1: P(top=80HP Murkrow)=0")
print("observer after two public eligible targets: P(top=Murkrow)=1/4")
print("physical Prize identities and both observer beliefs retain truth support")
print("forged HP universe, spoofed card metadata, impossible public signal rejected")
