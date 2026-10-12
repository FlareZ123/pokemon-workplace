"""SFT: Item lock must block Poffin before its hidden deck-inspection event."""

from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from board_position_state import BoardPokemon, BoardState, PokemonCard
from card_action_metadata import card_action_metadata_by_id
from deck_search_shuffle_topology import SearchableDeckPhysicalState
from direct_bench_search_execution import DirectBenchPlacement, direct_bench_target_from_metadata
from direct_bench_trainer_transaction import DirectBenchTrainerExecutionState
from hp_bounded_direct_bench_transaction import compile_hp_bounded_direct_bench_profiles
from hp_bounded_hidden_direct_bench_bridge import selected_print_multiset_label
from identity_materialization import CardInstance, IdentityLedger, materialize
from locked_hp_hidden_direct_bench_bridge import execute_locked_hp_hidden_direct_bench_transaction
from multicopy_zone_state import ZoneCountState
from pokemon_board_metadata import pokemon_board_metadata_by_id
from pokemon_card_profile import build_pokemon_card_profile_index
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from source_scoped_action_restrictions import build_source_scoped_action_restrictions
from stack_knockout_conservation import StackBoardMaterialState
from top_prize_physical_bridge import actual_joint_groups, belief_truth_probability
from typed_search_target_allocator import enumerate_typed_target_profiles, make_demand

P = "sv5-144"       # Buddy-Buddy Poffin
L = "sm11-90"      # eligible Elgyem, 60 HP
H = "me55-93"      # ineligible Murkrow, 80 HP
F = "class:filler"
GROUPS = ("L", "H")
GROUP_OF = {L: "L", H: "H"}
POOL = (("L1", L), ("H1", H), ("F1", F), ("F2", F))


def rejects(fn, message):
    try:
        fn()
    except ValueError as exc:
        assert message in str(exc), str(exc)
    else:
        raise AssertionError(f"expected ValueError: {message!r}")


prior_states = defaultdict(float)
for (instance, card_class), in permutations(POOL, 1):
    prior_states[(GROUP_OF.get(card_class),)] += 1 / len(POOL)
prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(
        GROUPS, 1,
        tuple(sorted(prior_states.items(), key=lambda r: repr(r[0]))),
    )
)
metadata = pokemon_board_metadata_by_id(ROOT / "resources")
profiles = build_pokemon_card_profile_index(ROOT / "resources")
actions = card_action_metadata_by_id(ROOT / "resources")
restrict = build_source_scoped_action_restrictions(ROOT / "resources")
vileplume = next(
    r for r in restrict if r.card_id == "xy7-3" and "item" in r.dimensions
)
spiritomb = next(
    r for r in restrict if r.card_id == "bw11-87" and "ace_spec" in r.dimensions
)
profile = next(
    r for r in compile_hp_bounded_direct_bench_profiles(ROOT / "resources")
    if r.direct.card_id == P
)
target = direct_bench_target_from_metadata(metadata[L], copies=1)
demand = make_demand("L", "Basic Pokémon")
allocation = enumerate_typed_target_profiles(
    (profile.direct.output,), (target.search_target.group,), (demand,)
)
action = next(row for row in allocation.actions if row.target_cost == (1,))
label = selected_print_multiset_label((target,), action)
assert label == L
policy = {
    (1, 0): {"OTHER": 1.0},
    (0, 1): {label: 1.0},
    (0, 0): {label: 1.0},
}

ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (P, "hand"): 1,
        (L, "deck"): 1,
        (H, "prize"): 1,
        (F, "deck"): 2,
    }),
    (CardInstance(
        instance_id="active-card",
        card_class="class:active",
        card_name="Active",
        zone="in_play",
        board_object_id="active",
    ),),
)
ledger = materialize(
    ledger, card_class=H, card_name="Murkrow",
    source_zone="prize", instance_id="prize-h",
)
physical = SearchableDeckPhysicalState(ledger, ("prize-h",), (False,))
state = DirectBenchTrainerExecutionState(
    StackBoardMaterialState(
        ledger,
        BoardState(
            (BoardPokemon(
                "active", (PokemonCard("active-card", "Active"),),
                retreat_cost=1,
            ),),
            active_id="active",
        ),
    )
)


def execute(restrictions=(), *, search_policy=policy):
    return execute_locked_hp_hidden_direct_bench_transaction(
        physical,
        state,
        (("actor", prior), ("observer", prior)),
        actor_id="actor",
        profile=profile,
        action_card_class=P,
        active_restrictions=restrictions,
        action_metadata_by_id=actions,
        demands=(demand,),
        targets=(target,),
        search_action=action,
        placements=(DirectBenchPlacement(0, "card-l", "bench-l"),),
        target_probability_by_composition=search_policy,
        group_by_card_class=GROUP_OF,
        sampled_top_card_class=F,
        sampled_top_card_name="Filler",
        sampled_top_instance_id="sample-top",
        board_metadata_by_id=metadata,
        card_profiles_by_id=profiles,
    )


for restrictions in ((), (spiritomb,)):
    result = execute(restrictions)
    after = result.physical_after.ledger
    assert after.exchangeable.count(P, "discard") == 1
    assert after.instance("card-l").zone == "in_play"
    assert result.state_after.material.ledger == after
    assert state.material.ledger.totals() == after.totals()

    actor = result.beliefs_after.belief_for("actor")
    observer = result.beliefs_after.belief_for("observer")
    assert isclose(actor.top_probability("H"), 0.0, abs_tol=1e-12)
    assert isclose(observer.top_probability("H"), 1 / 3, abs_tol=1e-12)

    top_group, prize_groups = actual_joint_groups(result.physical_after, GROUP_OF)
    assert top_group is None and prize_groups == ("H",)
    for belief in (actor, observer):
        assert belief_truth_probability(
            belief, top_group=top_group, prize_groups=prize_groups
        ) > 0.0

# If source-scoped Item lock is live, policy must never be evaluated: even an
# invalid policy cannot turn a prohibited Item into a private K1 observation.
rejects(
    lambda: execute((vileplume,), search_policy={}),
    "prohibited by active restrictions",
)
rejects(
    lambda: execute((), search_policy={}),
    "target-selection policy",
)
assert state.material.ledger.exchangeable.count(P, "hand") == 1
assert state.material.ledger.exchangeable.count(L, "deck") == 1
assert state.material.ledger.exchangeable.count(H, "prize") == 0
assert ledger.instance("prize-h").zone == "prize"

print("Poffin Item-lock + printed HP + hidden K1 regression passed")
print("no lock / ACE SPEC-only lock: Poffin searches L directly to Bench")
print("actor K1 P(top=80HP H)=0; observer after public L P(top=H)=1/3")
print("active Item lock rejects before a malformed selection policy can be used")
print("rejected Item has no physical movement, no returned Prize or top beliefs")
