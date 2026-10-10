from itertools import combinations


def choices(hand):
    return tuple(combinations(hand, 2))
