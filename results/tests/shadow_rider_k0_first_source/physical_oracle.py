"""Independent labeled-card oracle and paid source contractual gates."""
from collections import defaultdict
from fractions import Fraction
from itertools import combinations

from results.tests.shadow_rider_k0_first_source.reproduce import (
    ACTIONS, exact, first_success,
)
from results.tests.shadow_rider_paid_search_allocation.reproduce import feasible


def contract() -> None:
    op = [0] * 14
    hand = [0] * 14
    deck = [0] * 14
    deck[1] = 2
    op[0] = 1
    hand[0] = hand[3] = hand[9] = 1
    assert not first_success(tuple(op), tuple(hand), tuple(deck), "direct")
    op[7] = 1
    assert first_success(tuple(op), tuple(hand), tuple(deck), "direct")
    hand[2] = 1
    hand[0] = 0
    deck[0] = 1
    assert not first_success(tuple(op), tuple(hand), tuple(deck), "treasure")
    hand[10] = 1
    assert first_success(tuple(op), tuple(hand), tuple(deck), "treasure")
    print("PASS: direct Bench gating and mandatory paid-search cost")


def oracle() -> None:
    q = (1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1)
    cards = tuple(i for i, copies in enumerate(q) for _ in range(copies))
    groups = defaultdict(lambda: [0] * (len(ACTIONS) + 1))
    worlds = 0
    for chosen in combinations(range(len(cards)), 3):
        op = tuple(sum(cards[j] == i for j in chosen)
                   for i in range(len(q)))
        if not sum(op[i] for i in (0, 4, 6, 7, 8)):
            continue
        remainder = set(range(len(cards))) - set(chosen)
        for prize in remainder:
            for drawn in remainder - {prize}:
                hand = tuple(op[i] + int(cards[drawn] == i)
                             for i in range(len(q)))
                deck = tuple(sum(cards[j] == i for j in remainder
                                 if j not in (prize, drawn))
                             for i in range(len(q)))
                group = groups[(op, hand)]
                group[0] += int(feasible(op, hand, deck))
                for i, source in enumerate(ACTIONS):
                    group[i + 1] += int(
                        first_success(op, hand, deck, source)
                    )
                worlds += 1
    k1 = sum(group[0] for group in groups.values())
    k0 = sum(max(group[1:]) for group in groups.values())
    assert (worlds, k1, k0) == (83720, 2490, 2490)
    weighted_k1, weighted_k0, _ = exact(q, 3, 1)
    assert weighted_k1 == weighted_k0 == Fraction(2490, 83720)
    print("PASS: independent 83,720-world toy K0/K1 source equality")


if __name__ == "__main__":
    contract()
    oracle()
