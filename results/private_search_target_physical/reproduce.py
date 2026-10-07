from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from identity_materialization import IdentityLedger, materialize
from multicopy_zone_state import ZoneCountState
from private_search_target_physical import resolve_physical_private_search_shuffle
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief
from top_prize_physical_bridge import actual_joint_groups, belief_truth_probability

A = "class:A"
X = "class:X"
Y = "class:Y"
F = "class:F"
CARDS = (("A1", A), ("X1", X), ("Y1", Y), ("F1", F), ("F2", F), ("F3", F))
GROUPS = ("A", "X", "Y")


def group(card_class):
    if card_class == A:
        return "A"
    if card_class == X:
        return "X"
    if card_class == Y:
        return "Y"
    return None


def composition(prizes):
    return tuple(sum(group(card_class) == current for _name, card_class in prizes) for current in GROUPS)


ordered_prizes = tuple(permutations(CARDS, 2))
prior_masses = defaultdict(float)
for prizes in ordered_prizes:
    prior_masses[tuple(group(card_class) for _name, card_class in prizes)] += 1.0 / len(ordered_prizes)
prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(GROUPS, 2, tuple(sorted(prior_masses.items(), key=lambda row: repr(row[0]))))
)

policy = {}
for current in {composition(prizes) for prizes in ordered_prizes}:
    a_prized, x_prized, y_prized = current
    filler_prized = 2 - sum(current)
    counts = {
        "A": 1 - a_prized,
        "X": 1 - x_prized,
        "Y": 1 - y_prized,
        None: 3 - filler_prized,
    }
    policy[current] = {target: count / 4.0 for target, count in counts.items() if count}

ledger = IdentityLedger(
    ZoneCountState.from_mapping({
        (A, "prize"): 1,
        (X, "deck"): 1,
        (Y, "deck"): 1,
        (F, "prize"): 1,
        (F, "deck"): 2,
    })
)
ledger = materialize(ledger, card_class=A, card_name="A", source_zone="prize", instance_id="prize-a")
ledger = materialize(ledger, card_class=F, card_name="F", source_zone="prize", instance_id="prize-f")
physical = SearchableDeckPhysicalState(ledger, ("prize-a", "prize-f"), (False, False))

transition = resolve_physical_private_search_shuffle(
    physical,
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    target_probability_by_composition=policy,
    group_by_card_class={A: "A", X: "X", Y: "Y"},
    target_card_class=X,
    target_card_name="X",
    target_instance_id="private-x",
    sampled_top_card_class=Y,
    sampled_top_card_name="Y",
    sampled_top_instance_id="top-y",
)

assert transition.actor_exact_prize_counts == (("A", 1), ("X", 0), ("Y", 0))
assert transition.pre_search_group_pool_counts == (("A", 1), ("X", 1), ("Y", 1))
assert transition.pre_search_pool_size == 6
assert transition.physical_after.ledger.instance("private-x").zone == "hand"
assert transition.physical_after.ledger.instance("top-y").zone == "deck_top"

actor = transition.beliefs_after.belief_for("actor")
observer = transition.beliefs_after.belief_for("observer")
assert isclose(actor.top_probability("A"), 0.0, abs_tol=1e-12)
assert isclose(actor.top_probability("X"), 0.0, abs_tol=1e-12)
assert isclose(actor.top_probability("Y"), 1.0 / 3.0, abs_tol=1e-12)
assert isclose(observer.top_probability("A"), 1.0 / 6.0, abs_tol=1e-12)
assert isclose(observer.top_probability("X"), 1.0 / 6.0, abs_tol=1e-12)
assert isclose(observer.top_probability("Y"), 1.0 / 6.0, abs_tol=1e-12)

top_group, prize_groups = actual_joint_groups(transition.physical_after, {A: "A", X: "X", Y: "Y"})
assert top_group == "Y"
assert prize_groups == ("A", None)
for belief in (actor, observer):
    assert belief_truth_probability(belief, top_group=top_group, prize_groups=prize_groups) > 0.0

assert transition.physical_before.ledger.totals() == transition.physical_after.ledger.totals()

try:
    resolve_physical_private_search_shuffle(
        physical,
        (("actor", prior),),
        actor_id="actor",
        target_probability_by_composition=policy,
        group_by_card_class={A: "A", X: "X", Y: "Y"},
        target_card_class=A,
        target_card_name="A",
        target_instance_id="impossible-private-a",
        sampled_top_card_class=Y,
        sampled_top_card_name="Y",
        sampled_top_instance_id="unused-top-y",
    )
except ValueError:
    pass
else:
    raise AssertionError("Prized singleton A cannot be the actor's private searched target")

print("physical private-search belief bridge regressions passed")
print("exact truth: private X in hand, top=Y, prizes=(A, filler)")
print("actor top Y=1/3; observer top Y=1/6 under uniform private target")
print("both observers retain positive support on exact truth and totals are conserved")
