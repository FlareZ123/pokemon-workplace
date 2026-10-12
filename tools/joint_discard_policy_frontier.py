"""Exact shared-hand Item discard frontiers under five state-dependent DCI policies.

Each policy specifies which physical cards may pay for Quick Ball (1),
Ultra Ball (2), and Secret Box (3). Sequential multi-Item events reserve
one physical source copy of each selected Item and use no fetched outputs.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from math import comb

COST = {1: 1, 2: 2, 3: 3}
POLICIES = (
    "filler_only", "same_source_spares", "non_ace_sources",
    "all_sources", "all_sources_extra_basics"
)
ACTIONS = ((1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3))
ACTION_NAMES = (
    "quick", "ultra", "secret", "quick_ultra", "quick_secret",
    "ultra_secret", "all_three"
)


def can_pay(hand: tuple[int, ...], chosen: tuple[int, ...], policy: str) -> bool:
    """Can distinct, reserved source copies pay all chosen source costs?"""
    if any(hand[i] < 1 for i in chosen):
        return False
    b, q, u, s, f, _ = hand
    cost = sum(COST[i] for i in chosen)
    if policy == "filler_only":
        pool = f
    elif policy == "same_source_spares":
        pool = f + sum(hand[i] - 1 for i in chosen)
    elif policy == "non_ace_sources":
        pool = f + q + u - sum(i in (1, 2) for i in chosen)
    elif policy == "all_sources":
        pool = f + q + u + s - len(chosen)
    elif policy == "all_sources_extra_basics":
        pool = f + q + u + s + b - len(chosen)
    else:
        raise ValueError("unknown payment policy")
    return pool >= cost


def classify_policy(hand: tuple[int, ...]) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for policy in POLICIES:
        values = tuple(can_pay(hand, chosen, policy) for chosen in ACTIONS)
        for name, yes in zip(ACTION_NAMES, values):
            out[f"{policy}_{name}"] = yes
        out[f"{policy}_any"] = any(values[:3])
        out[f"{policy}_two"] = any(values[3:6])
    return out


def exact_policy_frontier(
    *, deck_size: int = 60, basics: int = 12, quick: int = 4,
    ultra: int = 4, secret: int = 1, filler: int = 8,
    opening: int = 7, prizes: int = 6,
) -> dict[str, Fraction]:
    counts = (basics, quick, ultra, secret, filler,
              deck_size - basics - quick - ultra - secret - filler)
    if any(type(n) is not int for n in (*counts, deck_size, opening, prizes)):
        raise TypeError("integer parameters required")
    if (min(counts) < 0 or basics < 1 or min((quick, ultra, secret)) < 1
            or secret != 1 or opening < 1 or prizes < 0
            or opening + prizes >= deck_size):
        raise ValueError("invalid deck composition or setup")
    accepted = comb(deck_size, opening) - comb(deck_size - basics, opening)
    if accepted == 0:
        raise ValueError("no valid starter")
    tally: dict[str, Fraction] = {}
    total = Fraction()
    for opener in product(*(range(min(n, opening) + 1) for n in counts)):
        if opener[0] == 0 or sum(opener) != opening:
            continue
        count = 1
        for n, held in zip(counts, opener):
            count *= comb(n, held)
        weight0 = Fraction(count, accepted)
        for drawn, n in enumerate(counts):
            remaining = n - opener[drawn]
            if remaining == 0:
                continue
            final = list(opener)
            final[0] -= 1
            final[drawn] += 1
            weight = weight0 * Fraction(remaining, deck_size - opening)
            total += weight
            for key, yes in classify_policy(tuple(final)).items():
                if yes:
                    tally[key] = tally.get(key, Fraction()) + weight
    assert total == 1
    for name in (*ACTION_NAMES, "any", "two"):
        probabilities = [tally.get(f"{p}_{name}", Fraction()) for p in POLICIES]
        assert probabilities == sorted(probabilities), (name, probabilities)
    return {
        f"{p}_{a}": tally.get(f"{p}_{a}", Fraction())
        for p in POLICIES for a in (*ACTION_NAMES, "any", "two")
    }


def brute_policy_frontier(
    *, deck_size: int, basics: int, quick: int, ultra: int,
    secret: int, filler: int, opening: int, prizes: int,
) -> dict[str, Fraction]:
    """Independent oracle enumerating labeled openers, Prizes and draws."""
    kinds = (["B"] * basics + ["Q"] * quick + ["U"] * ultra
             + ["S"] * secret + ["F"] * filler)
    kinds += ["P"] * (deck_size - len(kinds))
    ids = tuple(range(deck_size))
    totals: dict[str, int] = {}
    worlds = 0
    for opening_hand in combinations(ids, opening):
        if not any(kinds[i] == "B" for i in opening_hand):
            continue
        hand = set(opening_hand)
        active = next(i for i in opening_hand if kinds[i] == "B")
        hand.remove(active)
        unseen = tuple(i for i in ids if i not in opening_hand)
        for prizes_taken in combinations(unseen, prizes):
            prizes_set = set(prizes_taken)
            for drawn in unseen:
                if drawn in prizes_set:
                    continue
                final = hand | {drawn}
                histogram = tuple(
                    sum(kinds[i] == kind for i in final)
                    for kind in ("B", "Q", "U", "S", "F", "P")
                )
                worlds += 1
                for key, yes in classify_policy(histogram).items():
                    if yes:
                        totals[key] = totals.get(key, 0) + 1
    return {
        f"{p}_{a}": Fraction(totals.get(f"{p}_{a}", 0), worlds)
        for p in POLICIES for a in (*ACTION_NAMES, "any", "two")
    }
