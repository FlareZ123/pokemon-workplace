from __future__ import annotations

from collections import defaultdict
from itertools import permutations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from private_search_target_belief import (
    post_private_search_top_prize_belief,
    resolve_private_search_target_shuffle_for_observers,
)
from prize_position_belief import PrizePositionBelief
from prize_slot_visibility import PrizeSlotVisibilityBelief


def close(a: float, b: float) -> None:
    if abs(a - b) > 1e-12:
        raise AssertionError((a, b))


def collapsed(card: str):
    if card == "A":
        return "A"
    if card == "B":
        return "B"
    return None


positions = PrizePositionBelief(
    ("A", "B"),
    1,
    ((("A",), 0.2), (("B",), 0.2), ((None,), 0.6)),
)
prior = PrizeSlotVisibilityBelief.all_face_down(positions)
pool = {"A": 1, "B": 1}

uniform_policy = {
    (1, 0): {"B": 0.25, None: 0.75},
    (0, 1): {"A": 0.25, None: 0.75},
    (0, 0): {"A": 0.25, "B": 0.25, None: 0.50},
}

opponent = post_private_search_top_prize_belief(
    prior,
    pre_search_group_pool_counts=pool,
    pre_search_pool_size=5,
    target_probability_by_composition=uniform_policy,
)
close(opponent.top_probability("A"), 0.2)
close(opponent.top_probability("B"), 0.2)
close(opponent.top_probability(None), 0.6)

cards = ("A", "B", "F1", "F2", "F3")
exhaustive = defaultdict(float)
for prize, target, top in permutations(cards, 3):
    exhaustive[(collapsed(top), (collapsed(prize),))] += 1.0 / 60.0
analytic = dict(opponent.masses)
assert set(analytic) == set(exhaustive)
for key, probability in exhaustive.items():
    close(analytic[key], probability)

projected_map = dict(opponent.project_prizes().positions.masses)
close(projected_map[("A",)], 0.2)
close(projected_map[("B",)], 0.2)
close(projected_map[(None,)], 0.6)

resolved = resolve_private_search_target_shuffle_for_observers(
    (("actor", prior), ("opponent", prior)),
    actor_id="actor",
    actor_exact_prize_counts={"A": 0, "B": 0},
    actor_selected_target_group="A",
    pre_search_group_pool_counts=pool,
    pre_search_pool_size=5,
    target_probability_by_composition=uniform_policy,
)
actor = resolved.belief_for("actor")
other = resolved.belief_for("opponent")
close(actor.top_probability("A"), 0.0)
close(actor.top_probability("B"), 1.0 / 3.0)
close(actor.top_probability(None), 2.0 / 3.0)
close(other.top_probability("A"), 0.2)
close(other.top_probability("B"), 0.2)
close(other.top_probability(None), 0.6)

prefer_a = {
    (1, 0): {"B": 1.0},
    (0, 1): {"A": 1.0},
    (0, 0): {"A": 1.0},
}
biased = post_private_search_top_prize_belief(
    prior,
    pre_search_group_pool_counts=pool,
    pre_search_pool_size=5,
    target_probability_by_composition=prefer_a,
)
close(biased.top_probability("A"), 0.0)
close(biased.top_probability("B"), 0.2)
close(biased.top_probability(None), 0.8)
biased_prizes = dict(biased.project_prizes().positions.masses)
close(biased_prizes[("A",)], 0.2)
close(biased_prizes[("B",)], 0.2)
close(biased_prizes[(None,)], 0.6)

print({
    "uniform_top": {"A": opponent.top_probability("A"), "B": opponent.top_probability("B"), "filler": opponent.top_probability(None)},
    "actor_given_filler_prize_private_A": {"A": actor.top_probability("A"), "B": actor.top_probability("B"), "filler": actor.top_probability(None)},
    "prefer_A_opponent_top": {"A": biased.top_probability("A"), "B": biased.top_probability("B"), "filler": biased.top_probability(None)},
})
