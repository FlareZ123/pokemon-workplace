"""Independently test blind reshuffled Ticket transitions and rational bounds."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.prize_ticket_shuffle_blind import analyze_blind_shuffled_tickets
from tools.prize_ticket_shuffle_intervention import analyze_shuffled_tickets


def brute_physical(deck, prizes, required, steps):
    states = {(tuple(sorted(deck)), tuple(sorted(prizes))): Fraction(1)}
    result = [Fraction(int(set(required).issubset(deck)))]
    for _ in range(steps):
        follow = {}
        for (old_deck, old_prizes), prior in states.items():
            for inds in combinations(range(len(old_deck)), len(old_prizes)):
                selected = tuple(sorted(old_deck[i] for i in inds))
                remaining = tuple(old_deck[i] for i in range(len(old_deck)) if i not in inds)
                revised = tuple(sorted(remaining + old_prizes))
                key = (revised, selected)
                follow[key] = follow.get(key, Fraction(0)) + prior / comb(len(old_deck), len(old_prizes))
        states = follow
        result.append(sum(
            (mass for (current, _), mass in states.items() if set(required).issubset(current)),
            Fraction(0),
        ))
    return tuple(result)


def main():
    settings = dict(deck_targets=(0, 1, 1), old_prize_targets=(1, 0, 0),
                    required_in_deck=(1, 1, 1), deck_size=6,
                    prize_count=2, resets=4)
    model = analyze_blind_shuffled_tickets(**settings)
    brute = brute_physical(
        ("B", "C", "F0", "F1", "F2", "F3"),
        ("A", "X"), ("A", "B", "C"), 4,
    )
    assert model.success_by_fixed_count == brute
    assert model.best_fixed_success == max(brute)

    large = analyze_blind_shuffled_tickets(
        (0, 1, 1), (1, 0, 0), (1, 1, 1),
        deck_size=47, prize_count=6, resets=10,
    )
    informed = analyze_shuffled_tickets(
        (0, 1, 1), (1, 0, 0), (1, 1, 1),
        deck_size=47, prize_count=6, max_resets=3,
    )
    assert large.success_by_fixed_count[1] == informed.success_by_limit[1]
    assert all(large.success_by_fixed_count[i] <= informed.success_by_limit[i] for i in range(4))
    assert large.best_fixed_count == 1
    assert large.success_by_fixed_count[2] < large.success_by_fixed_count[1]
    assert large.success_by_fixed_count[3] < large.success_by_fixed_count[1]
    print("PASS: full labeled-card blind-transition tree equals grouped physical Markov model")
    for i, p in enumerate(large.success_by_fixed_count):
        print(f"fixed blind use count {i}: {float(p):.12%}")
    print("optimal fixed blind count", large.best_fixed_count,
          f"success={float(large.best_fixed_success):.12%}")


if __name__ == "__main__":
    main()
