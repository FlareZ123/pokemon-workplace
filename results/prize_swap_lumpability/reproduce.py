"""Exact Markov lumpability audit for Prize position/top abstractions.

The toy sample space contains all 24 ordered placements of three distinct
physical cards selected from A, B, X, Y: two Prize slots and a deck top.
Fraction probabilities make every reported equivalence exact.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import permutations
from math import factorial

CARDS = ("A", "B", "X", "Y")
STATES = tuple(permutations(CARDS, 3))


def count_prizes(state):
    return tuple(state[:2].count(card) for card in CARDS)


def project_count_top(state):
    return count_prizes(state), state[2]


def project_count(state):
    return count_prizes(state)


def swap_at(state, position):
    successor = list(state)
    successor[position], successor[2] = successor[2], successor[position]
    return tuple(successor)


def chosen_slot(state):
    return ((swap_at(state, 0), Fraction(1)),)


def uniform_random_slot(state):
    return tuple((swap_at(state, i), Fraction(1, 2)) for i in (0, 1))


def shuffled_positions(state):
    return tuple(
        (tuple((*order, state[2])), Fraction(1, factorial(2)))
        for order in permutations(state[:2])
    )


def projected_distribution(action, projection, state):
    distribution = defaultdict(Fraction)
    for successor, probability in action(state):
        distribution[projection(successor)] += probability
    return dict(distribution)


def witness_nonlumpability(action, projection):
    """Return two states in one abstract class with unequal successor laws."""
    seen = {}
    for state in STATES:
        key = projection(state)
        distribution = projected_distribution(action, projection, state)
        if key in seen:
            previous_state, previous_distribution = seen[key]
            if previous_distribution != distribution:
                return previous_state, state
        else:
            seen[key] = state, distribution
    return None


def main():
    assert len(STATES) == 24
    cases = (
        ("chosen slot", chosen_slot, project_count_top),
        ("uniform slot", uniform_random_slot, project_count_top),
        ("shuffle only", shuffled_positions, project_count_top),
        ("chosen slot", chosen_slot, project_count),
        ("uniform slot", uniform_random_slot, project_count),
        ("shuffle only", shuffled_positions, project_count),
    )
    expected = (True, False, False, True, True, False)
    for (label, action, projection), should_fail in zip(cases, expected):
        witness = witness_nonlumpability(action, projection)
        assert (witness is not None) == should_fail, (label, projection, witness)

    # Same Prize counts and top X, different selected Prize position identity.
    p = ("A", "B", "X")
    q = ("B", "A", "X")
    assert project_count_top(p) == project_count_top(q)
    assert projected_distribution(chosen_slot, project_count_top, p) != (
        projected_distribution(chosen_slot, project_count_top, q)
    )
    assert projected_distribution(uniform_random_slot, project_count_top, p) == (
        projected_distribution(uniform_random_slot, project_count_top, q)
    )

    # Same Prize counts, different top cards; random-slot swaps also diverge.
    r = ("A", "B", "Y")
    assert project_count(p) == project_count(r)
    assert projected_distribution(uniform_random_slot, project_count, p) != (
        projected_distribution(uniform_random_slot, project_count, r)
    )

    # All stochastic kernels carry exact probability one.
    for action in (chosen_slot, uniform_random_slot, shuffled_positions):
        for state in STATES:
            assert sum(prob for _, prob in action(state)) == 1

    print("24 physical states; six exact Markov lumpability audits passed")
    for (label, _, projection), failed in zip(cases, expected):
        print(f"{label:15s} / {projection.__name__:20s}: {'FAIL' if failed else 'PASS'}")


if __name__ == "__main__":
    main()
