"""Exhaustive labeled-card verification of shuffled Ticket recovery."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.prize_ticket_shuffle_intervention import analyze_shuffled_tickets
from tools.prize_ticket_reinspection import analyze_tickets


def independent_labeled_solver(deck, prizes, required, max_resets=3):
    if set(required).issubset(deck):
        return (Fraction(1),) * (max_resets+1), (Fraction(0),) * (max_resets+1)
    alive = {(tuple(sorted(deck)), tuple(sorted(prizes))): Fraction(1)}
    success = [Fraction(0)]
    uses = [Fraction(0)]
    for _ in range(max_resets):
        uses.append(uses[-1] + sum(alive.values(), Fraction(0)))
        after_failures = {}
        for (current_deck, old_prizes), probability in alive.items():
            for indices in combinations(range(len(current_deck)), len(old_prizes)):
                selected = tuple(current_deck[i] for i in indices)
                left = [x for i, x in enumerate(current_deck) if i not in indices]
                updated_deck = tuple(sorted(left + list(old_prizes)))
                if set(required).issubset(updated_deck):
                    continue
                key = (updated_deck, tuple(sorted(selected)))
                after_failures[key] = (
                    after_failures.get(key, Fraction(0))
                    + probability / comb(len(current_deck), len(old_prizes))
                )
        alive = after_failures
        success.append(Fraction(1)-sum(alive.values(), Fraction(0)))
    return tuple(success), tuple(uses)


def main():
    original_deck = ("B", "C", "F0", "F1", "F2", "F3")
    original_prizes = ("A", "X")
    expected_s, expected_uses = independent_labeled_solver(
        original_deck, original_prizes, ("A", "B", "C"),
    )
    actual = analyze_shuffled_tickets(
        (0, 1, 1), (1, 0, 0), (1, 1, 1),
        deck_size=6, prize_count=2, max_resets=3,
    )
    assert actual.success_by_limit == expected_s
    assert actual.expected_uses_by_limit == expected_uses

    large_params = dict(deck_targets=(0, 1, 1), old_prize_targets=(1, 0, 0),
                        required_in_deck=(1, 1, 1), deck_size=47, prize_count=6,
                        max_resets=3)
    shuffle = analyze_shuffled_tickets(**large_params)
    no_shuffle = analyze_tickets(**large_params)
    assert shuffle.success_by_limit[1] == no_shuffle.success_by_limit[1]
    assert shuffle.success_by_limit[2] < no_shuffle.success_by_limit[2]
    assert shuffle.success_by_limit[3] < no_shuffle.success_by_limit[3] == 1
    assert shuffle.success_by_limit == tuple(sorted(shuffle.success_by_limit))
    assert shuffle.expected_uses_by_limit[-1] >= no_shuffle.expected_uses_by_limit[-1]

    print("PASS: labeled physical deck-vs-Prize subset branching agrees exactly with grouped shuffle Markov DP")
    for n, (p, q) in enumerate(zip(no_shuffle.success_by_limit, shuffle.success_by_limit)):
        print(f"{n} resets: no-shuffle={float(p):.12%} shuffled={float(q):.12%} "
              f"gap={100*float(p-q):.9f} pp")
    print(f"3-reset expected uses: no-shuffle={float(no_shuffle.expected_uses_by_limit[-1]):.9f}, "
          f"shuffled={float(shuffle.expected_uses_by_limit[-1]):.9f}")


if __name__ == "__main__":
    main()
