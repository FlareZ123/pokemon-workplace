from collections import defaultdict
from itertools import permutations
from math import isclose
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from deck_search_target_signal import resolve_revealed_search_targets_shuffle
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief

A = "A"
X = "X"
Y = "Y"
Z = "Z"
F = None
GROUPS = (A, X, Y, Z)
CARDS = (("A1", A), ("X1", X), ("Y1", Y), ("Z1", Z), ("F1", F), ("F2", F), ("F3", F))


def composition(state):
    return tuple(sum(value == group for value in state) for group in GROUPS)


def public_selection(current):
    a_prized, x_prized, y_prized, z_prized = current
    if a_prized and not x_prized and not y_prized:
        return "XY"
    if not x_prized and not z_prized:
        return "XZ"
    return "PASS"


ordered = tuple(permutations(CARDS, 2))
masses = defaultdict(float)
for prizes in ordered:
    masses[tuple(group for _name, group in prizes)] += 1.0 / len(ordered)

prior = PrizeSlotVisibilityBelief.all_face_down(
    PrizePositionBelief(
        GROUPS,
        2,
        tuple(sorted(masses.items(), key=lambda row: repr(row[0]))),
    )
)
supported = {composition(tuple(group for _name, group in prizes)) for prizes in ordered}
policy = {current: {public_selection(current): 1.0} for current in supported}

beliefs = resolve_revealed_search_targets_shuffle(
    (("actor", prior), ("observer", prior)),
    actor_id="actor",
    actor_exact_prize_counts={A: 1, X: 0, Y: 0, Z: 0},
    target_probability_by_composition=policy,
    observed_target="XY",
    removed_target_groups=(X, Y),
    pre_search_group_pool_counts={A: 1, X: 1, Y: 1, Z: 1},
    pre_search_pool_size=7,
)

actor = beliefs.belief_for("actor")
observer = beliefs.belief_for("observer")
assert isclose(actor.top_probability(Z), 1.0 / 3.0, abs_tol=1e-12)
assert isclose(observer.top_probability(Z), 1.0 / 4.0, abs_tol=1e-12)
assert isclose(actor.top_probability(X), 0.0, abs_tol=1e-12)
assert isclose(actor.top_probability(Y), 0.0, abs_tol=1e-12)
assert isclose(observer.top_probability(X), 0.0, abs_tol=1e-12)
assert isclose(observer.top_probability(Y), 0.0, abs_tol=1e-12)

try:
    resolve_revealed_search_targets_shuffle(
        (("actor", prior),),
        actor_id="actor",
        actor_exact_prize_counts={A: 1, X: 0, Y: 0, Z: 0},
        target_probability_by_composition=policy,
        observed_target="XY",
        removed_target_groups=(X, X),
        pre_search_group_pool_counts={A: 1, X: 1, Y: 1, Z: 1},
        pre_search_pool_size=7,
    )
except ValueError as exc:
    assert "absent from the pool" in str(exc)
else:
    raise AssertionError("removing two X targets from a one-X pool must fail")

print("multi-target search signaling regression passed")
print("observed XY implies A Prized and X/Y unprized under the policy")
print("after removing X and Y: actor top Z=1/3, observer top Z=1/4")
print("over-removing a modeled target group is rejected")
