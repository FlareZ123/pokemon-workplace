from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from quick_ball_allocation_frontier import (
    additive_expected_utility,
    allocation_frontier_distribution,
)
from quick_ball_connector_contention import (
    joint_attacker_and_gladion_probability,
)


def pareto(outcomes):
    return tuple(sorted(
        outcome
        for outcome in outcomes
        if not any(
            other != outcome
            and other[0] >= outcome[0]
            and other[1] >= outcome[1]
            for other in outcomes
        )
    ))


def labeled_small_distribution():
    kinds = {
        "C1": "critical", "C2": "critical", "R": "rescue",
        "L": "support", "A": "attacker", "Q": "quick",
        "D": "disposable", "S": "starter", "F1": "filler",
        "F2": "filler",
    }
    cards = tuple(kinds)
    counts = {}
    total = 0

    for hand_tuple in combinations(cards, 3):
        hand = set(hand_tuple)
        if not any(kinds[card] in {"support", "attacker", "starter"} for card in hand):
            continue
        remaining = [card for card in cards if card not in hand]

        for prize_tuple in combinations(remaining, 2):
            prizes = set(prize_tuple)
            if not any(kinds[card] == "critical" for card in prizes):
                continue
            total += 1

            attacker_now = "A" in hand
            attacker_deck = "A" in remaining and "A" not in prizes
            rescue_hand = "R" in hand
            rescue_deck = "R" in remaining and "R" not in prizes
            support_preserved = (
                "L" in hand
                and ("A" in hand or "S" in hand)
            )
            support_deck = "L" in remaining and "L" not in prizes
            gladion_now = rescue_hand or (support_preserved and rescue_deck)
            searches = int("Q" in hand and "D" in hand)

            outcomes = {(int(attacker_now), int(gladion_now))}
            if searches and not attacker_now and attacker_deck:
                outcomes.add((1, int(gladion_now)))
            if searches and not gladion_now and support_deck and rescue_deck:
                outcomes.add((int(attacker_now), 1))

            frontier = pareto(outcomes)
            counts[frontier] = counts.get(frontier, 0) + 1

    return {frontier: count / total for frontier, count in counts.items()}


small = allocation_frontier_distribution(
    10,
    2,
    other_starters=1,
    attacker_starter_copies=1,
    critical_nonstarter=2,
    rescue_nonstarter=1,
    quick_ball_copies=1,
    disposable_nonstarter=1,
    opening_hand_size=3,
)
labeled = labeled_small_distribution()
assert set(small) == set(labeled)
for frontier in labeled:
    assert abs(small[frontier] - labeled[frontier]) < 1e-12

base = dict(
    deck_size=60,
    prize_count=6,
    other_starters=10,
    attacker_starter_copies=1,
    critical_nonstarter=4,
    rescue_nonstarter=2,
    quick_ball_copies=4,
    disposable_nonstarter=12,
    opening_hand_size=7,
)
distribution = allocation_frontier_distribution(**base)
assert abs(sum(distribution.values()) - 1.0) < 1e-10

both = ((1, 1),)
choice = ((0, 1), (1, 0))
physical = joint_attacker_and_gladion_probability(
    **base,
    reusable_connector_counterfactual=False,
)
reusable = joint_attacker_and_gladion_probability(
    **base,
    reusable_connector_counterfactual=True,
)
assert abs(distribution[both] - physical) < 1e-12
assert abs(distribution[both] + distribution[choice] - reusable) < 1e-12
assert abs(
    distribution[choice] - (reusable - physical)
) < 1e-12

for disposable in (4, 8, 12, 16, 20, 24):
    row = {**base, "disposable_nonstarter": disposable}
    result = allocation_frontier_distribution(**row)
    p_both = result.get(both, 0.0)
    p_choice = result.get(choice, 0.0)
    print(
        disposable,
        f"both={p_both:.9%}",
        f"choice={p_choice:.9%}",
        f"attacker_only={result.get(((1, 0),), 0.0):.9%}",
        f"gladion_only={result.get(((0, 1),), 0.0):.9%}",
        f"neither={result.get(((0, 0),), 0.0):.9%}",
    )

print(
    "equal_weight_completed_channels=",
    additive_expected_utility(
        distribution,
        attacker_value=1,
        gladion_value=1,
    ),
)
print("validation passed")
