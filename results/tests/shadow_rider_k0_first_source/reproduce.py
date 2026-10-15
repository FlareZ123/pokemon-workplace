"""K0 first-search source allocation for C1/F1 Shadow Rider versus Thorns.

The initial source is selected from observed opening and natural draw only.
Search targets can change after the first legal full-deck inspection.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb, prod

from results.tests.shadow_rider_fog_marshadow.reproduce import allocations
from results.tests.shadow_rider_fog_allocation.reproduce import prize_masks
from results.tests.shadow_rider_paid_search_allocation.reproduce import (
    capacities, feasible, verify_prints,
)

ACTIONS = ("direct", "fog", "treasure", "quick", "stone")
SOURCE = {"fog": 11, "treasure": 2, "quick": 12, "stone": 5}
TARGETS = {
    "fog": (8, 6, 10),
    "treasure": (0, 8, 6),
    "quick": (0, 8, 6),
    "stone": (0, 3, 8, 9),
}


def first_success(op: tuple[int, ...], hand: tuple[int, ...],
                  deck: tuple[int, ...], action: str) -> bool:
    if deck[1] < 2:
        return False
    benchable = bool(op[4] or op[6] or op[7])
    if not (benchable or op[8]):
        return False
    if action == "direct":
        return bool(hand[0] and (hand[9] or (benchable and hand[8]))
                    and (op[4] or hand[3]))
    idx = SOURCE[action]
    if not hand[idx]:
        return False
    if action in ("treasure", "quick") and not hand[10]:
        return False
    if action == "stone" and not hand[6]:
        return False
    for target in TARGETS[action]:
        if not deck[target]:
            continue
        if target == 10 and hand[10] >= 5:
            continue
        new_hand, new_deck = list(hand), list(deck)
        new_hand[idx] -= 1
        if action in ("treasure", "quick"):
            new_hand[10] -= 1
        new_deck[target] -= 1
        new_hand[target] += 1
        if feasible(op, tuple(new_hand), tuple(new_deck)):
            return True
    return False


def exact(q: tuple[int, ...], opening: int = 7,
          prizes: int = 6) -> tuple[Fraction, Fraction, dict[str, int]]:
    n = sum(q)
    basics = sum(q[i] for i in (0, 4, 6, 7, 8))
    prize_count = comb(n - opening - 1, prizes)
    denominator = (
        (comb(n, opening) - comb(n - basics, opening))
        * (n - opening) * prize_count
    )
    total = 0
    k1 = 0
    k0 = 0
    source_wins = dict.fromkeys(ACTIONS, 0)
    for index, op in enumerate(allocations(opening, q)):
        if not sum(op[i] for i in (0, 4, 6, 7, 8)):
            continue
        opening_weight = prod(comb(a, b) for a, b in zip(q, op))
        after = tuple(a - b for a, b in zip(q, op))
        for draw, copies in enumerate(after):
            if not copies:
                continue
            hand = tuple(op[i] + int(i == draw) for i in range(len(q)))
            pool = tuple(after[i] - int(i == draw) for i in range(len(q)))
            weight = opening_weight * copies
            total += weight * prize_count
            stocks = tuple(pool[i] for i in (0, 1, 3, 8, 9, 6))
            oracle_mass = 0
            source_mass = [0] * len(ACTIONS)
            for mask, ways in prize_masks(stocks, n - opening - 1, prizes):
                deck = list(pool)
                for bit, role in enumerate((0, 3, 8, 9, 6)):
                    deck[role] = int(not bool(mask & (1 << bit)))
                deck[1] = 2
                deck = tuple(deck)
                if not feasible(op, hand, deck):
                    continue
                oracle_mass += ways
                options = [first_success(op, hand, deck, s) for s in ACTIONS]
                assert any(options)
                for i, works in enumerate(options):
                    source_mass[i] += works * ways
            best = max(source_mass)
            assert best <= oracle_mass
            k1 += weight * oracle_mass
            k0 += weight * best
            source_wins[ACTIONS[source_mass.index(best)]] += weight * best
        if index % 1000 == 0:
            feasible.cache_clear()
    assert total == denominator
    assert sum(source_wins.values()) == k0
    return Fraction(k1, denominator), Fraction(k0, denominator), source_wins


def main() -> None:
    verify_prints()
    oracle, k0, source_wins = exact(capacities(1, 1))
    target = Fraction(26946742764678720, 367753188390588000)
    assert oracle == k0 == target
    assert source_wins == {
        "direct": 2776215577632672,
        "fog": 15097785778237696,
        "treasure": 7095938439519996,
        "quick": 1192693385166371,
        "stone": 784109584121985,
    }
    print(f"K1 oracle access: {float(oracle):.9%}")
    print(f"K0 first-search policy access: {float(k0):.9%}")
    print("PASS: zero first-source information gap under restricted model")


if __name__ == "__main__":
    main()
