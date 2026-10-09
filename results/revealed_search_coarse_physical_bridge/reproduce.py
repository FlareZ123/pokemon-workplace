"""End-to-end physically exact Quick Ball with coarse print-latent opponent beliefs."""

from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from discard_cost_witness import DiscardCandidate, enumerate_discard_selections
from identity_materialization import IdentityLedger, materialize
from multicopy_zone_state import ZoneCountState
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from revealed_search_coarse_physical_bridge import execute_coarse_revealed_trainer_search
from search_zone_transition import SearchZoneTarget
from single_output_search_profile_compiler import compile_single_output_revealed_search_profiles
from trainer_search_transaction import TrainerSearchExecutionState
from typed_search_target_allocator import BASIC_POKEMON, TargetGroup, enumerate_typed_target_profiles, make_demand

OLD = "xy1-42"
NEW = "swsh7-49"
P_A = "class:A"
P_OLD = f"exact_print:{OLD}"
P_NEW = f"exact_print:{NEW}"
F = "class:F"
QUICK = "trainer:quick_ball"
FODDER = "card:fodder"
GROUPS = ("A", OLD, NEW)
POOL = (
    ("A1", P_A, "A"),
    ("old", P_OLD, OLD),
    ("new", P_NEW, NEW),
    ("F1", F, None),
    ("F2", F, None),
    ("F3", F, None),
)


def choose(composition: tuple[int, ...]) -> str:
    a_prized, old_prized, new_prized = composition
    if a_prized and not old_prized:
        return OLD
    if not new_prized:
        return NEW
    if not old_prized:
        return OLD
    return "PASS"


counts = defaultdict(float)
for left, right in permutations(POOL, 2):
    counts[(left[2], right[2])] += 1.0 / 30.0
prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(
        GROUPS,
        2,
        tuple(sorted(counts.items(), key=lambda x: repr(x[0]))),
    )
)
policy = {
    composition: {choose(composition): 1.0}
    for composition in prior.positions.composition_distribution()
}
public = {OLD: "Pikachu", NEW: "Pikachu", "PASS": "NO_SEARCH"}

physical_ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (P_A, "prize"): 1,
        (P_OLD, "deck"): 1,
        (P_NEW, "deck"): 1,
        (F, "prize"): 1,
        (F, "deck"): 2,
        (QUICK, "hand"): 1,
        (FODDER, "hand"): 1,
    })
)
physical_ledger = materialize(
    physical_ledger,
    card_class=P_A,
    card_name="A",
    source_zone="prize",
    instance_id="prize-a",
)
physical_ledger = materialize(
    physical_ledger,
    card_class=F,
    card_name="Filler",
    source_zone="prize",
    instance_id="prize-f",
)
physical = SearchableDeckPhysicalState(
    physical_ledger,
    ("prize-a", "prize-f"),
    (False, False),
)
profile = next(
    row for row in compile_single_output_revealed_search_profiles(
        ROOT / "resources"
    ) if row.card_id == "swsh1-179"
)
targets = (
    SearchZoneTarget(P_OLD, TargetGroup("Old Pikachu", 1, frozenset({BASIC_POKEMON}))),
    SearchZoneTarget(P_NEW, TargetGroup("New Pikachu", 1, frozenset({BASIC_POKEMON}))),
)
demands = (make_demand("basic", "Basic Pokémon"),)
allocation = enumerate_typed_target_profiles(
    profile.base_outputs,
    tuple(row.group for row in targets),
    demands,
)
take_old = next(
    action for action in allocation.actions if action.target_cost == (1, 0)
)
candidates = (DiscardCandidate(FODDER),)
payment = enumerate_discard_selections(
    physical.ledger.exchangeable, candidates, 1
)[0]


def run(observed: str, *, print_identity_index=None, material_name="Pikachu"):
    return execute_coarse_revealed_trainer_search(
        physical,
        TrainerSearchExecutionState(zones=physical.ledger.exchangeable),
        (("actor", prior), ("opponent", prior)),
        actor_id="actor",
        profile=profile,
        action_card_class=QUICK,
        demands=demands,
        targets=targets,
        search_action=take_old,
        target_probability_by_composition=policy,
        public_label_by_target=public,
        observed_public_label=observed,
        group_by_card_class={P_A: "A", P_OLD: OLD, P_NEW: NEW},
        target_card_name=material_name,
        target_instance_id="searched-old-print",
        sampled_top_card_class=P_NEW,
        sampled_top_card_name="Pikachu",
        sampled_top_instance_id="sampled-new-print",
        discard_candidates=candidates,
        discard_selection=payment,
        play_condition_met=True,
        print_identity_index=print_identity_index,
    )


result = run("Pikachu")
exact = result.exact_transaction
assert result.exact_target_group == OLD
assert exact.selected_target_index == 0
assert exact.trainer_transaction.discard_cost == 1
assert exact.trainer_transaction.after.zones.count(QUICK, "discard") == 1
assert exact.trainer_transaction.after.zones.count(FODDER, "discard") == 1
assert exact.physical_after.ledger.instance("searched-old-print").card_class == P_OLD
assert exact.physical_after.ledger.instance("searched-old-print").card_name == "Pikachu"
assert exact.physical_after.ledger.instance("sampled-new-print").card_class == P_NEW
assert exact.physical_before.ledger.totals() == exact.physical_after.ledger.totals()


def check(left: float, right: float) -> None:
    assert isclose(left, right, rel_tol=0.0, abs_tol=1e-12), (left, right)


actor = result.observer_beliefs.belief_for("actor")
opponent = result.observer_beliefs.belief_for("opponent")
check(actor.top_probability("A"), 0.0)
check(actor.top_probability(NEW), 1.0 / 3)
check(actor.target_probability(OLD), 1.0)
check(opponent.target_probability(OLD), 0.5)
check(opponent.target_probability(NEW), 0.5)
check(opponent.top_probability("A"), 3.0 / 14)
check(
    sum(weight for (_, prizes, _), weight in opponent.masses if "A" in prizes),
    5.0 / 14,
)
posterior_old = opponent.condition_target(OLD)
posterior_new = opponent.condition_target(NEW)
check(
    sum(weight for (_, prizes, _), weight in posterior_old.masses if "A" in prizes),
    4.0 / 7,
)
check(
    sum(weight for (_, prizes, _), weight in posterior_new.masses if "A" in prizes),
    1.0 / 7,
)
check(posterior_old.top_probability("A"), 1.0 / 7)
check(posterior_new.top_probability("A"), 2.0 / 7)

# Coarse label must still agree with what the physically selected card shows.
try:
    run("Porygon")
except ValueError as exc:
    assert "public observation" in str(exc)
else:
    raise AssertionError("mismatched public label should reject physical transaction")

print("coarse physical Quick Ball search retains exact-card conservation")
print("actor sees old print and K1; opponent sees name Pikachu and latent print")
print("opponent P(A Prized)=5/14; P(top A)=3/14")
print("latent print observation restores old=4/7, new=1/7 Prize posteriors")
