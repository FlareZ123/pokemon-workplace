from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_target_signal import resolve_revealed_search_target_shuffle
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief

CARDS = ("A1", "X1", "Y1", "F1", "F2", "F3")
GROUPS = ("A", "X", "Y")


def group(card):
    if card.startswith("A"):
        return "A"
    if card.startswith("X"):
        return "X"
    if card.startswith("Y"):
        return "Y"
    return None


def composition(prizes):
    return tuple(
        sum(group(card) == current for card in prizes)
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


prior_masses = defaultdict(float)
ordered_prizes = tuple(permutations(CARDS, 2))
for prizes in ordered_prizes:
    prior_masses[tuple(group(card) for card in prizes)] += (
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
    composition(prizes)
    for prizes in ordered_prizes
}
policy = {
    current: {chosen_target(current): 1.0}
    for current in supported_compositions
}

beliefs = resolve_revealed_search_target_shuffle(
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    actor_exact_prize_counts={"A": 1, "X": 0, "Y": 0},
    target_probability_by_composition=policy,
    observed_target="X",
    observed_target_group="X",
    pre_search_group_pool_counts={"A": 1, "X": 1, "Y": 1},
    pre_search_pool_size=6,
)

actor = beliefs.belief_for("actor")
observer = beliefs.belief_for("observer")

assert isclose(actor.top_probability("A"), 0.0, abs_tol=1e-12)
assert isclose(actor.top_probability("X"), 0.0, abs_tol=1e-12)
assert isclose(actor.top_probability("Y"), 1.0 / 3.0, abs_tol=1e-12)
assert isclose(actor.top_probability(None), 2.0 / 3.0, abs_tol=1e-12)

assert isclose(observer.top_probability("A"), 1.0 / 7.0, abs_tol=1e-12)
assert isclose(observer.top_probability("X"), 0.0, abs_tol=1e-12)
assert isclose(observer.top_probability("Y"), 1.0 / 7.0, abs_tol=1e-12)
assert isclose(observer.top_probability(None), 5.0 / 7.0, abs_tol=1e-12)

composition_mass = observer.project_prizes().positions.composition_distribution()
assert isclose(composition_mass[(1, 0, 1)], 1.0 / 7.0, abs_tol=1e-12)
assert isclose(composition_mass[(1, 0, 0)], 3.0 / 7.0, abs_tol=1e-12)
assert isclose(composition_mass[(0, 0, 1)], 3.0 / 7.0, abs_tol=1e-12)

assert isclose(
    observer.joint_probability(
        top_group="A",
        prize_position=0,
        prize_group="A",
    ),
    0.0,
    abs_tol=1e-12,
)

expected_observer = defaultdict(float)
observer_branches = []
for prizes in ordered_prizes:
    current_composition = composition(prizes)
    if chosen_target(current_composition) != "X":
        continue
    remaining = [
        card
        for card in CARDS
        if card not in prizes and card != "X1"
    ]
    assert len(remaining) == 3
    for top_card in remaining:
        observer_branches.append(
            (
                group(top_card),
                tuple(group(card) for card in prizes),
            )
        )

for state in observer_branches:
    expected_observer[state] += 1.0 / len(observer_branches)

assert len(observer_branches) == 42
actual_observer = dict(observer.masses)
assert set(actual_observer) == set(expected_observer)
for state, probability in expected_observer.items():
    assert isclose(
        actual_observer[state],
        probability,
        rel_tol=0.0,
        abs_tol=1e-12,
    )

expected_actor = defaultdict(float)
actor_branches = []
for prizes in ordered_prizes:
    if composition(prizes) != (1, 0, 0):
        continue
    remaining = [
        card
        for card in CARDS
        if card not in prizes and card != "X1"
    ]
    for top_card in remaining:
        actor_branches.append(
            (
                group(top_card),
                tuple(group(card) for card in prizes),
            )
        )

for state in actor_branches:
    expected_actor[state] += 1.0 / len(actor_branches)

actual_actor = dict(actor.masses)
assert set(actual_actor) == set(expected_actor)
for state, probability in expected_actor.items():
    assert isclose(
        actual_actor[state],
        probability,
        rel_tol=0.0,
        abs_tol=1e-12,
    )

incoherent_policy = {
    current: {"X": 1.0}
    for current in supported_compositions
}
try:
    resolve_revealed_search_target_shuffle(
        (("actor", prior), ("observer", prior)),
        actor_id="actor",
        actor_exact_prize_counts={"A": 1, "X": 0, "Y": 0},
        target_probability_by_composition=incoherent_policy,
        observed_target="X",
        observed_target_group="X",
        pre_search_group_pool_counts={"A": 1, "X": 1, "Y": 1},
        pre_search_pool_size=6,
    )
except ValueError:
    pass
else:
    raise AssertionError(
        "policy cannot reveal a searched singleton from states where it is Prized"
    )

print("revealed search-target signaling regressions passed")
print("observed target X leaves 42 exhaustive opponent branches")
print("observer post-signal top: A=1/7, Y=1/7, filler=5/7")
print("actor exact state top: Y=1/3, filler=2/3")
