from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from quick_ball_allocation_draw_frontier import (
    allocation_draw_frontier_distribution,
)
from quick_ball_allocation_frontier import allocation_frontier_distribution
from quick_ball_lele_draw_access import draw_window_gladion_access_probability


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
            deck = [card for card in remaining if card not in prizes]

            for draw_tuple in combinations(deck, 2):
                draws = set(draw_tuple)
                total += 1
                seen = hand | draws

                attacker_now = "A" in seen
                attacker_deck = "A" in deck and "A" not in draws
                rescue_hand = "R" in seen
                rescue_deck = "R" in deck and "R" not in draws
                support_preserved = (
                    "L" in hand
                    and ("A" in hand or "S" in hand)
                )
                support_drawn = "L" in draws
                support_deck = "L" in deck and "L" not in draws
                gladion_now = rescue_hand or (
                    (support_preserved or support_drawn)
                    and rescue_deck
                )
                searches = min(
                    int("Q" in seen),
                    int("D" in seen),
                )

                outcomes = {(int(attacker_now), int(gladion_now))}
                if searches and not attacker_now and attacker_deck:
                    outcomes.add((1, int(gladion_now)))
                if searches and not gladion_now and support_deck and rescue_deck:
                    outcomes.add((int(attacker_now), 1))

                frontier = pareto(outcomes)
                counts[frontier] = counts.get(frontier, 0) + 1

    return {
        frontier: count / total
        for frontier, count in counts.items()
    }


small = allocation_draw_frontier_distribution(
    10, 2,
    other_starters=1,
    attacker_starter_copies=1,
    critical_nonstarter=2,
    rescue_nonstarter=1,
    quick_ball_copies=1,
    disposable_nonstarter=1,
    later_random_draws=2,
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
zero = allocation_draw_frontier_distribution(**base, later_random_draws=0)
opening_only = allocation_frontier_distribution(**base)
assert set(zero) == set(opening_only)
for frontier in zero:
    assert abs(zero[frontier] - opening_only[frontier]) < 1e-12

both = ((1, 1),)
choice = ((0, 1), (1, 0))
for draws in (0, 1, 2, 3, 5, 8, 12):
    result = allocation_draw_frontier_distribution(
        **base,
        later_random_draws=draws,
    )
    gladion_marginal = (
        result.get(both, 0.0)
        + result.get(choice, 0.0)
        + result.get(((0, 1),), 0.0)
    )
    direct = draw_window_gladion_access_probability(
        60, 6,
        other_starters=11,
        critical_nonstarter=4,
        rescue_nonstarter=2,
        quick_ball_copies=4,
        disposable_nonstarter=12,
        later_random_draws=draws,
        opening_hand_size=7,
        mode="strict",
    )
    assert abs(gladion_marginal - direct) < 1e-12
    print(
        draws,
        f"both={result.get(both, 0.0):.9%}",
        f"choice={result.get(choice, 0.0):.9%}",
        f"attacker_only={result.get(((1, 0),), 0.0):.9%}",
        f"gladion_only={result.get(((0, 1),), 0.0):.9%}",
        f"neither={result.get(((0, 0),), 0.0):.9%}",
    )

print("validation passed")
