"""Generalize double-trigger joint access to N distinct singleton Bench supports."""
from __future__ import annotations

from fractions import Fraction
from itertools import product
from math import comb

from bench_double_trigger_access import JointAccess, _vectors, _ways


def analyze_many(*, targets: int = 3, deck_size: int = 60,
                 opening_size: int = 7, prize_count: int = 6,
                 draws: int = 4, other_basics: int = 4,
                 hand_connectors: int = 4, direct_connectors: int = 4,
                 certain_pickups: int = 0, coin_pickups: int = 4,
                 bench_slack: int = 1) -> JointAccess:
    """Exact N-support joint access with the minimum required pickup successes.

    The target copies are distinct singleton Basics, searches into hand
    are single-use and cost-free, and pickup attempts resolve independently.
    The output is a mechanical upper bound before actual Ability effects.
    """
    if targets < 2 or targets > 5:
        raise ValueError("supported target count: 2..5")
    groups = (1,) * targets + (other_basics, hand_connectors,
                              direct_connectors, certain_pickups, coin_pickups)
    if min(groups) < 0 or sum(groups) > deck_size:
        raise ValueError("invalid deck-class counts")
    if opening_size < 1 or opening_size > deck_size:
        raise ValueError("invalid opening_size")
    if draws < 0 or prize_count < 0 or opening_size + draws + prize_count > deck_size:
        raise ValueError("invalid draws/prizes")
    if bench_slack < 0 or bench_slack > 5:
        raise ValueError("invalid bench_slack")
    capacities = groups + (deck_size - sum(groups),)
    U = deck_size - opening_size - draws
    cp = comb(U, prize_count)
    coin_scale = 1 << coin_pickups
    open_ways = 0
    nominal_ways = role_ways = typed_ways = exact_scaled_ways = 0
    for opening in _vectors(capacities, opening_size):
        ow = _ways(capacities, opening)
        if sum(opening[:targets]) + opening[targets] == 0:
            continue
        open_ways += ow
        rem = tuple(n - k for n, k in zip(capacities, opening, strict=True))
        forced = (-1 if opening[targets] else
                  next(i for i in range(targets) if opening[i]))
        for drawn in _vectors(rem, draws):
            dw = _ways(rem, drawn)
            nominal_hand = tuple(opening[i] + drawn[i] for i in range(targets))
            true_hand = tuple(nominal_hand[i] - int(i == forced)
                              for i in range(targets))
            missing = tuple(i for i, count in enumerate(nominal_hand) if not count)
            h = opening[targets + 1] + drawn[targets + 1]
            d = opening[targets + 2] + drawn[targets + 2]
            guaranteed = opening[targets + 3] + drawn[targets + 3]
            coins = opening[targets + 4] + drawn[targets + 4]
            need_releases = max(0, targets - bench_slack)
            if bench_slack == 0 or guaranteed + coins < need_releases:
                continue
            for prize_bits in product((0, 1), repeat=len(missing)):
                prized = sum(prize_bits)
                if prized > prize_count:
                    continue
                w = ow * dw * comb(U - len(missing), prize_count - prized)
                prize_map = dict(zip(missing, prize_bits, strict=True))
                searchable = tuple(i in missing and not prize_map.get(i, 0)
                                   for i in range(targets))
                naive = all(nominal_hand[i] or ((h + d > 0) and searchable[i])
                            for i in range(targets))
                role = all(true_hand[i] or ((h + d > 0) and searchable[i])
                           for i in range(targets))
                typed = (sum(v == 0 for v in true_hand) <= h
                         and all(true_hand[i] or searchable[i]
                                 for i in range(targets)))
                nominal_ways += w * naive
                role_ways += w * role
                typed_ways += w * typed
                if typed:
                    needed_coin_heads = max(0, need_releases - guaranteed)
                    winning_coin_paths = sum(comb(coins, j)
                                             for j in range(needed_coin_heads, coins + 1))
                    exact_scaled_ways += w * winning_coin_paths * (1 << (coin_pickups - coins))
    if not open_ways:
        return JointAccess(*(Fraction(0) for _ in range(5)))
    base = open_ways * comb(deck_size - opening_size, draws) * cp
    return JointAccess(Fraction(open_ways, comb(deck_size, opening_size)),
                       Fraction(nominal_ways, base),
                       Fraction(role_ways, base),
                       Fraction(typed_ways, base),
                       Fraction(exact_scaled_ways, base * coin_scale))
