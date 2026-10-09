from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from card_class_namespace import CardClassNamespace
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
from single_output_search_profile_compiler import (
    compile_single_output_revealed_search_profiles,
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

quick_ball = next(
    profile
    for profile in compile_single_output_revealed_search_profiles(
        ROOT / "resources"
    )
    if profile.card_id == "swsh1-179"
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

# An alternative policy can assign the literal observation "Y" to exactly
# the same Prize states that would choose physical X. Without binding the
# public observation to the materialized card, this contradiction survives
# both posterior-support and conservation checks.
renamed_policy = {
    composition: {
        ("Y" if chosen_target(composition) == "X" else "OTHER"): 1.0
    }
    for composition in supported_compositions
}
try:
    execute_hidden_trainer_search_transaction(
        physical,
        execution_state,
        (("actor", prior), ("observer", prior)),
        actor_id="actor",
        profile=quick_ball,
        action_card_class=QUICK_BALL,
        demands=demands,
        targets=targets,
        search_action=search_x,
        target_probability_by_composition=renamed_policy,
        observed_target="Y",
        group_by_card_class={A: "A", X: "X", Y: "Y"},
        target_card_name="X",
        target_instance_id="incorrect-reveal-x",
        sampled_top_card_class=Y,
        sampled_top_card_name="Y",
        sampled_top_instance_id="incorrect-reveal-top",
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=True,
    )
except ValueError as exc:
    assert "public revealed target" in str(exc)
else:
    raise AssertionError("public observation Y cannot describe physically searched X")


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

# The exact-print namespace can describe a public reveal more precisely
# than the card's deck-building name. Both legal prints here say Pikachu,
# while the Bayesian signal must identify which printing was actually shown.
OLD_PRINT = "xy1-42"
NEW_PRINT = "swsh7-49"
PRINT_X = f"exact_print:{OLD_PRINT}"
PRINT_Y = f"exact_print:{NEW_PRINT}"
print_classes = {X: PRINT_X, Y: PRINT_Y}
print_zones = ZoneCountState.from_mapping({
    (print_classes.get(card_class, card_class), zone): count
    for card_class, zone, count in physical.ledger.exchangeable.counts
})
print_physical = SearchableDeckPhysicalState(
    IdentityLedger(print_zones, physical.ledger.instances),
    physical.prize_instance_ids,
    physical.face_up,
)
print_targets = (
    SearchZoneTarget(PRINT_X, targets[0].group),
    SearchZoneTarget(PRINT_Y, targets[1].group),
)
print_signal_policy = {
    composition: {
        {"X": OLD_PRINT, "Y": NEW_PRINT, "PASS": "PASS"}[
            chosen_target(composition)
        ]: 1.0
    }
    for composition in supported_compositions
}
printed = execute_hidden_trainer_search_transaction(
    print_physical,
    TrainerSearchExecutionState(zones=print_physical.ledger.exchangeable),
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    profile=quick_ball,
    action_card_class=QUICK_BALL,
    demands=demands,
    targets=print_targets,
    search_action=search_x,
    target_probability_by_composition=print_signal_policy,
    observed_target=OLD_PRINT,
    observation_namespace=CardClassNamespace.EXACT_PRINT,
    group_by_card_class={A: "A", PRINT_X: "X", PRINT_Y: "Y"},
    target_card_name="Pikachu",
    target_instance_id="searched-print-x",
    sampled_top_card_class=PRINT_Y,
    sampled_top_card_name="Pikachu",
    sampled_top_instance_id="sampled-print-y",
    discard_candidates=discard_candidates,
    discard_selection=discard_selection,
    play_condition_met=True,
)
selected_print = printed.physical_after.ledger.instance("searched-print-x")
assert selected_print.card_class == PRINT_X
assert selected_print.card_name == "Pikachu"
assert selected_print.zone == "hand"
assert printed.physical_after.ledger.instance("sampled-print-y").card_class == PRINT_Y
assert isclose(
    printed.beliefs_after.belief_for("actor").top_probability("Y"),
    1.0 / 3.0,
    abs_tol=1e-12,
)
assert isclose(
    printed.beliefs_after.belief_for("observer").top_probability("Y"),
    1.0 / 7.0,
    abs_tol=1e-12,
)
assert print_physical.ledger.totals() == printed.physical_after.ledger.totals()

# Renaming the policy's X observation to the other print makes a coherent
# numeric posterior, but contradicts the physically materialized Pikachu.
false_print_policy = {
    composition: {
        (NEW_PRINT if chosen_target(composition) == "X" else "OTHER"): 1.0
    }
    for composition in supported_compositions
}
try:
    execute_hidden_trainer_search_transaction(
        print_physical,
        TrainerSearchExecutionState(zones=print_physical.ledger.exchangeable),
        (("actor", prior), ("observer", prior)),
        actor_id="actor",
        profile=quick_ball,
        action_card_class=QUICK_BALL,
        demands=demands,
        targets=print_targets,
        search_action=search_x,
        target_probability_by_composition=false_print_policy,
        observed_target=NEW_PRINT,
        observation_namespace=CardClassNamespace.EXACT_PRINT,
        group_by_card_class={A: "A", PRINT_X: "X", PRINT_Y: "Y"},
        target_card_name="Pikachu",
        target_instance_id="mismatched-print-x",
        sampled_top_card_class=PRINT_Y,
        sampled_top_card_name="Pikachu",
        sampled_top_instance_id="mismatched-print-top",
        discard_candidates=discard_candidates,
        discard_selection=discard_selection,
        play_condition_met=True,
    )
except ValueError as exc:
    assert "materialized card identity" in str(exc)
else:
    raise AssertionError("revealed print must equal the selected material print")


print("hidden Trainer search bridge regressions passed")
print("contradictory name and print-level signals both rejected")
print("exact-print Pikachu search preserves both hidden-state posteriors")
print("Quick Ball and one exact fodder copy enter discard")
print("searched X is public/materialized in hand; exact shuffled top is Y")
print("actor top Y=1/3; opponent top Y=1/7")
print("Item lock rejects the transaction and card totals remain conserved")
