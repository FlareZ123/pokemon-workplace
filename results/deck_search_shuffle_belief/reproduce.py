from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_shuffle_belief import resolve_full_search_shuffle_for_observers
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief

CARDS = ("A1", "B1", "B2", "F1", "F2")
GROUPS = ("A", "B")


def group(card):
    if card.startswith("A"):
        return "A"
    if card.startswith("B"):
        return "B"
    return None


def collapsed_prize_prior():
    masses = defaultdict(float)
    denominator = len(CARDS) * (len(CARDS) - 1)
    for first, second in permutations(CARDS, 2):
        masses[(group(first), group(second))] += 1.0 / denominator
    return PrizePositionBelief(
        GROUPS,
        2,
        tuple(sorted(masses.items(), key=lambda row: repr(row[0]))),
    )


def exhaustive_joint(*, exact_composition=None):
    rows = []
    for first, second, top in permutations(CARDS, 3):
        prizes = (group(first), group(second))
        if exact_composition is not None:
            counts = {
                current: sum(value == current for value in prizes)
                for current in GROUPS
            }
            if counts != exact_composition:
                continue
        rows.append((group(top), prizes))

    masses = defaultdict(float)
    for row in rows:
        masses[row] += 1.0 / len(rows)
    return masses


prior = PrizeSlotVisibilityBelief.all_face_down(collapsed_prize_prior())
beliefs = resolve_full_search_shuffle_for_observers(
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    actor_exact_prize_counts={"A": 1, "B": 0},
    group_pool_counts={"A": 1, "B": 2},
    pool_size=5,
)

actor = beliefs.belief_for("actor")
observer = beliefs.belief_for("observer")

assert isclose(actor.top_probability("A"), 0.0, abs_tol=1e-12)
assert isclose(actor.top_probability("B"), 2.0 / 3.0, abs_tol=1e-12)
assert isclose(actor.top_probability(None), 1.0 / 3.0, abs_tol=1e-12)

assert isclose(observer.top_probability("A"), 1.0 / 5.0, abs_tol=1e-12)
assert isclose(observer.top_probability("B"), 2.0 / 5.0, abs_tol=1e-12)
assert isclose(observer.top_probability(None), 2.0 / 5.0, abs_tol=1e-12)

assert isclose(
    observer.joint_probability(
        top_group="A",
        prize_position=0,
        prize_group="A",
    ),
    0.0,
    abs_tol=1e-12,
)
assert (
    observer.top_probability("A")
    * observer.prize_probability_at(0, "A")
    > 0.0
)

expected_observer = exhaustive_joint()
actual_observer = dict(observer.masses)
assert set(actual_observer) == set(expected_observer)
for state, probability in expected_observer.items():
    assert isclose(
        actual_observer[state],
        probability,
        rel_tol=0.0,
        abs_tol=1e-12,
    )

expected_actor = exhaustive_joint(exact_composition={"A": 1, "B": 0})
actual_actor = dict(actor.masses)
assert set(actual_actor) == set(expected_actor)
for state, probability in expected_actor.items():
    assert isclose(
        actual_actor[state],
        probability,
        rel_tol=0.0,
        abs_tol=1e-12,
    )

try:
    resolve_full_search_shuffle_for_observers(
        (("actor", prior),),
        actor_id="actor",
        actor_exact_prize_counts={"A": 0, "B": 3},
        group_pool_counts={"A": 1, "B": 2},
        pool_size=5,
    )
except ValueError:
    pass
else:
    raise AssertionError("impossible exact Prize composition must be rejected")

print("deck search shuffle belief regressions passed")
print("actor top: A=0, B=2/3, filler=1/3")
print("observer top: A=1/5, B=2/5, filler=2/5")
print("singleton A cannot be both Prized at slot 0 and the post-shuffle top")
