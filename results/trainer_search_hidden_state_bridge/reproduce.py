from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from discard_cost_witness import (
    DiscardCandidate,
    enumerate_discard_selections,
)
from identity_materialization import IdentityLedger, materialize
from lock_state_kernel import PlayerChannels
from multicopy_zone_state import ZoneCountState
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from search_zone_transition import SearchZoneTarget
from top_prize_physical_bridge import (
    actual_joint_groups,
    belief_truth_probability,
)
from trainer_search_hidden_state_bridge import (
    execute_hidden_trainer_search_transaction,
)
from trainer_search_profile_compiler import (
    CompiledTrainerSearchProfile,
    SearchOutput,
)
from trainer_search_transaction import TrainerSearchExecutionState
from typed_search_target_allocator import (
    BASIC_POKEMON,
    TargetGroup,
    enumerate_typed_target_profiles,
    make_demand,
)

A = "class:A"
X = "class:X"
Y = "class:Y"
F = "class:F"
QUICK_BALL = "trainer:quick_ball"
FODDER = "card:fodder"
CARDS = (
    ("A1", A),
    ("X1", X),
    ("Y1", Y),
    ("F1", F),
    ("F2", F),
    ("F3", F),
)
GROUPS = ("A", "X", "Y")


def group(card_class):
    if card_class == A:
        return "A"
    if card_class == X:
        return "X"
    if card_class == Y:
        return "Y"
    return None


def composition_from_cards(prizes):
    return tuple(
        sum(group(card_class) == current for _name, card_class in prizes)
        for current in GROUPS
    )


def chosen_target(prize_composition):
    a_prized, x_prized, y_prized = prize_composition
    if x_prized == 0 and a_prized > 0:
        return "X"
    if y_prized == 0 and a_prized == 0:
        return "Y"
    if x_prized == 0:
        return "X"
    if y_prized == 0:
        return "Y"
    return "PASS"


ordered_prizes = tuple(permutations(CARDS, 2))
prior_masses = defaultdict(float)
for prizes in ordered_prizes:
    prior_masses[tuple(group(card_class) for _name, card_class in prizes)] += (
        1.0 / len(ordered_prizes)
    )

prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(
        GROUPS,
        2,
        tuple(sorted(prior_masses.items(), key=lambda row: repr(row[0]))),
    )
)
supported_compositions = {
    composition_from_cards(prizes)
    for prizes in ordered_prizes
}
policy = {
    current: {chosen_target(current): 1.0}
    for current in supported_compositions
}

ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (A, "prize"): 1,
        (X, "deck"): 1,
        (Y, "deck"): 1,
        (F, "prize"): 1,
        (F, "deck"): 2,
        (QUICK_BALL, "hand"): 1,
        (FODDER, "hand"): 1,
    })
)
ledger = materialize(
    ledger,
    card_class=A,
    card_name="A",
    source_zone="prize",
    instance_id="prize-a",
)
ledger = materialize(
    ledger,
    card_class=F,
    card_name="F",
    source_zone="prize",
    instance_id="prize-f",
)
physical = SearchableDeckPhysicalState(
    ledger,
    ("prize-a", "prize-f"),
    (False, False),
)

quick_ball = CompiledTrainerSearchProfile(
    card_id="swsh1-179",
    name="Quick Ball",
    action_class="Item",
    base_outputs=(SearchOutput("Basic Pokémon", 1),),
    required_discard_other_cards=1,
    play_condition=(
        "You can play this card only if you discard another card from your hand."
    ),
)
targets = (
    SearchZoneTarget(
        X,
        TargetGroup("X Basic", 1, frozenset({BASIC_POKEMON})),
    ),
    SearchZoneTarget(
        Y,
        TargetGroup("Y Basic", 1, frozenset({BASIC_POKEMON})),
    ),
)
demands = (make_demand("basic", "Basic Pokémon"),)
allocation = enumerate_typed_target_profiles(
    quick_ball.base_outputs,
    tuple(target.group for target in targets),
    demands,
)
search_x = next(
    action
    for action in allocation.actions
    if action.target_cost == (1, 0)
)

execution_state = TrainerSearchExecutionState(
    zones=physical.ledger.exchangeable
)
discard_candidates = (DiscardCandidate(FODDER),)
discard_selection = enumerate_discard_selections(
    execution_state.zones,
    discard_candidates,
    1,
)[0]

transition = execute_hidden_trainer_search_transaction(
    physical,
    execution_state,
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    profile=quick_ball,
    action_card_class=QUICK_BALL,
    demands=demands,
    targets=targets,
    search_action=search_x,
    target_probability_by_composition=policy,
    observed_target="X",
    group_by_card_class={A: "A", X: "X", Y: "Y"},
    target_card_name="X",
    target_instance_id="searched-x",
    sampled_top_card_class=Y,
    sampled_top_card_name="Y",
    sampled_top_instance_id="top-y",
    discard_candidates=discard_candidates,
    discard_selection=discard_selection,
    play_condition_met=True,
)

tx = transition.trainer_transaction
assert tx.discard_cost == 1
assert tx.after.zones.count(QUICK_BALL, "discard") == 1
assert tx.after.zones.count(FODDER, "discard") == 1
assert not tx.after.budget.supporter_used
assert transition.selected_target_index == 0

searched = transition.physical_after.ledger.instance("searched-x")
assert searched.card_class == X
assert searched.zone == "hand"
top = transition.physical_after.ledger.instance("top-y")
assert top.card_class == Y
assert top.zone == "deck_top"

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

assert transition.physical_before.ledger.totals() == (
    transition.physical_after.ledger.totals()
)

try:
    execute_hidden_trainer_search_transaction(
        physical,
        TrainerSearchExecutionState(
            zones=physical.ledger.exchangeable,
            channels=PlayerChannels(item_play=False),
        ),
        (("actor", prior), ("observer", prior)),
        actor_id="actor",
        profile=quick_ball,
        action_card_class=QUICK_BALL,
        demands=demands,
        targets=targets,
        search_action=search_x,
        target_probability_by_composition=policy,
        observed_target="X",
        group_by_card_class={A: "A", X: "X", Y: "Y"},
        target_card_name="X",
        target_instance_id="locked-search-x",
        sampled_top_card_class=Y,
        sampled_top_card_name="Y",
        sampled_top_instance_id="locked-top-y",
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=True,
    )
except ValueError:
    pass
else:
    raise AssertionError("Item lock must reject the atomic Quick Ball transaction")

print("hidden Trainer search bridge regressions passed")
print("Quick Ball and one exact fodder copy enter discard")
print("searched X is public/materialized in hand; exact shuffled top is Y")
print("actor top Y=1/3; opponent top Y=1/7")
print("Item lock rejects the transaction and card totals remain conserved")
