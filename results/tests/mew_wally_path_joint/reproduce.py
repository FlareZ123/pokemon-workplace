"""Exact original 60 +Tapu Lele Wally launch under an opponent's active Path.

Launch: first-turn going second Mew V starter, DCE, Wally or Wonder Tag,
Mew VMAX in deck, Genesect V on Bench. Opposing Path may be removed by
naturally held Sky Field, Field Blower or Lost Vacuum (with distinct payment).

Use: python results/tests/mew_wally_path_joint/reproduce.py
"""
from __future__ import annotations

import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from results.tests.mew_wally_first_attack.reproduce import (
    opening_counts, probability_all_prized,
)

# Mew, Genesect, VMAX, Wally, DCE, VIP, Quick, Ultra, Tapu,
# Sky Field, Field Blower, Lost Vacuum, other.
POOL = (4, 4, 3, 1, 4, 3, 4, 4, 1, 2, 1, 1, 28)
NAMES = ("wally_held", "tapu_held_sky", "tapu_ball_sky",
         "tapu_held_blower", "tapu_ball_blower",
         "tapu_held_vacuum", "tapu_ball_vacuum")


def all_survive(deck_size: int, prizes: int, sizes: list[int]) -> Fraction:
    result = Fraction(0)
    for k in range(len(sizes) + 1):
        for subset in combinations(sizes, k):
            result += (-1 if k % 2 else 1) * probability_all_prized(
                deck_size, prizes, sum(subset)
            )
    return result


def payment_feasible(held, enabler: str | None) -> bool:
    """Pick cheaper distinct Balls first, reserve compulsory held resources.

    Seven opening plus one natural draw; the initial Mew has moved Active.
    Every unreserved other hand card may *mechanically* pay one discard.
    This says nothing about strategic resource value.
    """
    required_ball_searches = int(not held[8]) + int(not (held[1] or held[5]))
    if held[6] + held[7] < required_ball_searches:
        return False
    quick = min(held[6], required_ball_searches)
    ultra = required_ball_searches - quick
    payment = quick + 2 * ultra
    reserved = (
        1 + 1  # Starting Mew Active and held Double Colorless Energy
        + int(bool(held[8]))  # Hand-held Tapu must be Benched
        + int(bool(held[1] or held[5]))  # Genesect or 1 VIP retained
        + required_ball_searches  # Used Quick/Ultra cards
        + int(enabler is not None)  # Must retain the Path-removal card
    )
    if enabler == "vacuum":
        payment += 1  # Lost Vacuum puts a *different* hand card in Lost Zone
    return 8 - reserved >= payment


def physical_route(held: Counter, deck: Counter, path_active: bool) -> str | None:
    if not (held[0] and held[4] and deck[2]):
        return None
    if held[3]:
        if held[1] or (deck[1] and (held[5] or held[6] or held[7])):
            return "wally_held"
        return None
    if not deck[3] or (not held[8] and not deck[8]):
        return None
    if not held[1] and not deck[1]:
        return None
    label = "tapu_held" if held[8] else "tapu_ball"
    if not path_active:
        return label if payment_feasible(held, None) else None
    for kind, i in (("sky", 9), ("blower", 10), ("vacuum", 11)):
        if held[i] and payment_feasible(held, kind):
            return label + "_" + kind
    return None


def exact(pool: tuple[int, ...], hand: int, prizes: int, path_active: bool):
    n = sum(pool)
    result = Counter()
    for opening, ways in opening_counts(pool, hand):
        if not opening[0]:
            continue  # Mew must be Active before seeing natural draw.
        for k, copies in enumerate(pool):
            remaining = copies - opening[k]
            if not remaining:
                continue
            held = list(opening)
            held[k] += 1
            if not held[4]:
                continue
            if held[3]:
                if not (held[1] or held[5] or held[6] or held[7]):
                    continue
                required = [pool[2] - held[2]]
                if not held[1]:
                    required.append(pool[1] - held[1])
                label = "wally_held"
            else:
                if held[6] + held[7] < int(not held[8]) + int(not (held[1] or held[5])):
                    continue
                remedy = None
                if path_active:
                    for kind, idx in (("sky", 9), ("blower", 10), ("vacuum", 11)):
                        if held[idx] and payment_feasible(held, kind):
                            remedy = kind
                            break
                    if remedy is None:
                        continue
                elif not payment_feasible(held, None):
                    continue
                required = [pool[2] - held[2], pool[3] - held[3]]
                if not held[8]:
                    required.append(pool[8] - held[8])
                if not held[1]:
                    required.append(pool[1] - held[1])
                label = ("tapu_held" if held[8] else "tapu_ball")
                if remedy:
                    label += "_" + remedy
            chance = all_survive(n - hand - 1, prizes, required)
            result[label] += Fraction(
                ways * remaining, comb(n, hand) * (n - hand)
            ) * chance
    return dict(result)


def labeled_oracle(pool: tuple[int, ...], hand: int, prizes: int, path_active: bool):
    cards = tuple(k for k, copies in enumerate(pool) for _ in range(copies))
    n = len(cards)
    den = comb(n, hand) * comb(n - hand, prizes) * (n - hand - prizes)
    hits = Counter()
    for initial in combinations(range(n), hand):
        opening = set(initial)
        if not any(cards[i] == 0 for i in opening):
            continue
        left = set(range(n)) - opening
        for p in combinations(sorted(left), prizes):
            prize_set = set(p)
            for d in left - prize_set:
                held = Counter(cards[i] for i in opening | {d})
                deck = Counter(cards[i] for i in left - prize_set - {d})
                category = physical_route(held, deck, path_active)
                if category:
                    hits[category] += 1
    return {k: Fraction(v, den) for k, v in hits.items()}


def main():
    fixtures = (
        ((1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1), 3, 2),
        ((2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), 4, 2),
    )
    for pool, hand, prizes in fixtures:
        for active in (False, True):
            observed = exact(pool, hand, prizes, active)
            truth = labeled_oracle(pool, hand, prizes, active)
            assert observed == truth, (pool, active, observed, truth)
            print(f"Physical-oracle PASS N={sum(pool)}, opponent Path={active}")
    no_path = exact(POOL, 7, 6, False)
    path = exact(POOL, 7, 6, True)
    assert sum(no_path.values()) == Fraction(636040115150563, 8681622274224900)
    assert path["wally_held"] == Fraction(167155400140607, 11575496365633200)
    assert sum(path.values()) == Fraction(16510599747617, 513199346259600)
    required = {
        "sky": Fraction(25443804376439, 2604486682267470),
        "blower": Fraction(24005155197563, 5483129857405200),
        "vacuum": Fraction(665602537771, 185703150250800),
    }
    for kind, expected in required.items():
        actual = sum(v for k, v in path.items() if k.endswith("_" + kind))
        assert actual == expected, (kind, actual, expected)
    for route, p in sorted(path.items()):
        print(f"{route}: {float(p):.12%}; exact={p}")
    print(f"unopposed total {float(sum(no_path.values())):.12%}")
    print(f"Path present total {float(sum(path.values())):.12%}")
    print(f"Path access loss {float(sum(no_path.values()) - sum(path.values())):.12%}")
    print(f"Path with Sky only {float(path['wally_held'] + required['sky']):.12%}")
    print(f"Path with Sky/Blower {float(path['wally_held'] + required['sky'] + required['blower']):.12%}")


if __name__ == "__main__":
    main()
