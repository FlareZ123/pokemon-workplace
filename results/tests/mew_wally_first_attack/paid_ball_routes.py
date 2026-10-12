"""Exact exclusive natural, VIP, Quick Ball and Ultra Ball Mew Wally routes."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.tests.mew_wally_first_attack.reproduce import (
    opening_counts, probability_all_prized,
)

# Mew V, Genesect V, Mew VMAX, Wally, DCE, VIP, Quick Ball, Ultra Ball, other.
POOL = (4, 4, 3, 1, 4, 3, 4, 4, 33)
ROUTES = ("genesect_in_hand", "vip_from_deck", "quick_from_deck", "ultra_from_deck")


def classify(held, deck):
    if not (held[0] and held[3] and held[4] and deck[2]):
        return None
    if held[1]:
        return 0
    if not deck[1]:
        return None
    if held[5]:
        return 1
    if held[6]:
        return 2
    if held[7]:
        return 3
    return None


def exact(pool, hand, prizes):
    n = sum(pool)
    probs = [Fraction(0)] * 4
    for h, ways in opening_counts(pool, hand):
        if not h[0]:  # Mew V must be the initial Active.
            continue
        for k, copies in enumerate(pool):
            remaining = copies - h[k]
            if not remaining:
                continue
            held = list(h)
            held[k] += 1
            if not (held[3] and held[4]):
                continue
            v = pool[2] - held[2]
            g = pool[1] - held[1]
            deck_n = n - hand - 1
            value = 1 - probability_all_prized(deck_n, prizes, v)
            if held[1]:
                route = 0
            elif held[5]:
                route = 1
            elif held[6]:
                route = 2
            elif held[7]:
                route = 3
            else:
                continue
            if route:
                value -= probability_all_prized(deck_n, prizes, g)
                value += probability_all_prized(deck_n, prizes, v + g)
            probs[route] += Fraction(ways * remaining, comb(n, hand) * (n - hand)) * value
    return probs


def oracle(pool, hand, prizes):
    physical = tuple(k for k, copies in enumerate(pool) for _ in range(copies))
    n = len(physical)
    hits = [0] * 4
    den = comb(n, hand) * comb(n - hand, prizes) * (n - hand - prizes)
    for opening in combinations(range(n), hand):
        hs = set(opening)
        if not any(physical[i] == 0 for i in hs):
            continue
        left = set(range(n)) - hs
        for ps in combinations(sorted(left), prizes):
            prize_set = set(ps)
            for drawn in left - prize_set:
                held = Counter(physical[i] for i in hs | {drawn})
                deck = Counter(physical[i] for i in left - prize_set - {drawn})
                k = classify(held, deck)
                if k is not None:
                    hits[k] += 1
    return [Fraction(x, den) for x in hits]


def main():
    for pool, hand, prizes in (
        ((1, 1, 1, 1, 1, 0, 1, 1, 4), 3, 2),
        ((2, 2, 2, 1, 1, 1, 1, 1, 1), 4, 2),
    ):
        assert exact(pool, hand, prizes) == oracle(pool, hand, prizes)
        print("Physical labeled independent oracle passed N =", sum(pool))
    rates = exact(POOL, 7, 6)
    expected = [
        Fraction(1826378549, 314141781525),
        Fraction(113315023076173, 34726489096899600),
        Fraction(4622073298441, 1446937045704150),
        Fraction(9415778482801, 4340811137112450),
    ]
    assert rates == expected
    for name, rate in zip(ROUTES, rates):
        print(f"{name}: {float(rate):.12%}; exact={rate}")
    total = sum(rates)
    assert total == Fraction(167155400140607, 11575496365633200)
    print(f"union: {float(total):.12%}; exact={total}")


if __name__ == "__main__":
    main()
