from itertools import combinations, permutations
from fractions import Fraction
from math import factorial


def outcomes(hand, deck):
    result = set()
    for chosen in combinations(hand, 2):
        kept = tuple(c for c in hand if c not in chosen)
        pool = deck + chosen
        for shuffled in permutations(pool):
            result.add((chosen, shuffled[0], kept + shuffled[:1],
                        shuffled[1:], Fraction(1, factorial(len(pool)))))
    return result


def verify():
    states = paths = 0
    for h in range(5):
        hand = tuple(f"H{i}" for i in range(h))
        for d in range(4):
            deck = tuple(f"D{i}" for i in range(d))
            historical = {
                (
                    (hand[i], hand[j]),
                    ordering[0],
                    hand[:i] + hand[i+1:j] + hand[j+1:] + ordering[:1],
                    ordering[1:],
                    Fraction(1, factorial(d + 2)),
                )
                for i in range(h)
                for j in range(i + 1, h)
                for ordering in permutations(deck + (hand[i], hand[j]))
            }
            current = outcomes(hand, deck)
            assert historical == current
            assert bool(current) == (h >= 2)
            for choice in combinations(hand, 2):
                assert sum((x[-1] for x in current if x[0] == choice), Fraction()) == 1
            states += 1
            paths += len(current)
    return states, paths
