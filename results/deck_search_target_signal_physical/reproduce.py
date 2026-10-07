from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from deck_search_target_signal_physical import (
    resolve_physical_revealed_search_shuffle,
)
from identity_materialization import IdentityLedger, materialize
from multicopy_zone_state import ZoneCountState
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from top_prize_physical_bridge import (
    actual_joint_groups,
    belief_truth_probability,
)

A = "class:A"
X = "class:X"
Y = "class:Y"
F = "class:F"
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

transition = resolve_physical_revealed_search_shuffle(
    physical,
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    target_probability_by_composition=policy,
    observed_target="X",
    group_by_card_class={A: "A", X: "X", Y: "Y"},
    target_card_class=X,
    target_card_name="X",
    target_instance_id="searched-x",
    sampled_top_card_class=Y,
    sampled_top_card_name="Y",
    sampled_top_instance_id="top-y",
)

assert transition.actor_exact_prize_counts == (
    ("A", 1),
    ("X", 0),
    ("Y", 0),
)
assert transition.pre_search_group_pool_counts == (
    ("A", 1),
    ("X", 1),
    ("Y", 1),
)
assert transition.pre_search_pool_size == 6

searched = transition.physical_after.ledger.instance("searched-x")
assert searched.card_class == X
assert searched.zone == "hand"
top = transition.physical_after.ledger.instance("top-y")
assert top.card_class == Y
assert top.zone == "deck_top"

actor = transition.beliefs_after.belief_for("actor")
observer = transition.beliefs_after.belief_for("observer")
assert isclose(actor.top_probability("A"), 0.0, abs_tol=1e-12)
assert isclose(actor.top_probability("Y"), 1.0 / 3.0, abs_tol=1e-12)
assert isclose(observer.top_probability("A"), 1.0 / 7.0, abs_tol=1e-12)
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
    resolve_physical_revealed_search_shuffle(
        physical,
        (("actor", prior),),
        actor_id="actor",
        target_probability_by_composition=policy,
        observed_target="X",
        group_by_card_class={A: "A", X: "X", Y: "Y"},
        target_card_class=A,
        target_card_name="A",
        target_instance_id="impossible-search-a",
        sampled_top_card_class=Y,
        sampled_top_card_name="Y",
        sampled_top_instance_id="unused-top-y",
    )
except ValueError:
    pass
else:
    raise AssertionError("Prized singleton A cannot be searched from deck")

print("physical revealed-search signaling regressions passed")
print("searched X is materialized in hand and exact shuffled top is Y")
print("actor top Y=1/3; observer top Y=1/7")
print("both observer posteriors retain exact world top=Y, prizes=(A, filler)")
print("card-class totals remain conserved")
