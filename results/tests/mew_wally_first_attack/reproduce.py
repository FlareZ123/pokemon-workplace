"""Exact restricted Wally to Mew VMAX first-turn attack access in Aichi 2026 Mew/Genesect.

Use: python results/tests/mew_wally_first_attack/reproduce.py
All probabilities are rational, per shuffled initial seven plus first natural draw
and six Prize cards, with no extra draws or searches beyond Battle VIP Pass.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb

# 60-card fifth-place source: 4 Mew V, 4 Genesect V, 3 Mew VMAX,
# 1 Wally, 4 DCE, 3 Battle VIP Pass, 41 other cards.
POOL = (4, 4, 3, 1, 4, 3, 41)


def opening_counts(pool, k):
    if len(pool) == 1:
        if 0 <= k <= pool[0]:
            yield (k,), comb(pool[0], k)
        return
    for a in range(max(0, k - sum(pool[1:])), min(pool[0], k) + 1):
        for tail, ways in opening_counts(pool[1:], k - a):
            yield (a, *tail), ways * comb(pool[0], a)


def probability_all_prized(n, p, target):
    if target > p:
        return Fraction(0)
    return Fraction(comb(n - target, p - target), comb(n, p))


def exact(pool, hand, prizes):
    n = sum(pool)
    assert len(pool) == 7 and hand + prizes + 1 < n
    den = comb(n, hand) * (n - hand)
    direct = Fraction(0)
    vip = Fraction(0)
    for seen, ways in opening_counts(pool, hand):
        if not seen[0]:  # Mew V must be starting Active, before first draw.
            continue
        for drawn, copies in enumerate(pool):
            remaining = copies - seen[drawn]
            if not remaining:
                continue
            held = list(seen)
            held[drawn] += 1
            if not (held[3] and held[4]):  # Wally and DCE in hand.
                continue
            v = pool[2] - held[2]
            g = pool[1] - held[1]
            left = n - hand - 1
            vm_available = 1 - probability_all_prized(left, prizes, v)
            weight = Fraction(ways * remaining, den)
            if held[1]:
                direct += weight * vm_available
            elif held[5]:
                both_prized = probability_all_prized(left, prizes, v + g)
                gene_prized = probability_all_prized(left, prizes, g)
                vip += weight * (vm_available - gene_prized + both_prized)
    return direct, vip


def labeled_oracle(pool, hand_size, prizes):
    """Independent physical-card enumeration of both exclusive routes."""
    physical = tuple(i for kind, copies in enumerate(pool) for i in [kind] * copies)
    n = len(physical)
    hits = Counter()
    denominator = comb(n, hand_size) * comb(n - hand_size, prizes) * (n - hand_size - prizes)
    for h in combinations(range(n), hand_size):
        hs = set(h)
        if not any(physical[i] == 0 for i in hs):
            continue
        remaining = set(range(n)) - hs
        for p in combinations(sorted(remaining), prizes):
            ps = set(p)
            for draw in remaining - ps:
                held = Counter(physical[i] for i in hs)
                held[physical[draw]] += 1
                deck = Counter(physical[i] for i in remaining - ps - {draw})
                if not (held[3] and held[4] and deck[2]):
                    continue
                if held[1]:
                    hits["direct"] += 1
                elif held[5] and deck[1]:
                    hits["vip"] += 1
    return (Fraction(hits["direct"], denominator), Fraction(hits["vip"], denominator))


def main():
    for pool, hand, prize in (((1, 1, 1, 1, 1, 1, 4), 3, 2),
                              ((2, 2, 2, 1, 1, 1, 3), 4, 2)):
        model = exact(pool, hand, prize)
        oracle = labeled_oracle(pool, hand, prize)
        assert model == oracle, (pool, model, oracle)
        print(f"Exhaustive physical oracle N={sum(pool)} PASS {model}")
    direct, vip = exact(POOL, 7, 6)
    total = direct + vip
    valid = 1 - Fraction(comb(49, 7), comb(60, 7))
    mew = 1 - Fraction(comb(56, 7), comb(60, 7))
    expected = Fraction(18541777258637, 2042734652758800)
    assert total == expected
    assert direct == Fraction(1826378549, 314141781525)
    assert vip == Fraction(113315023076173, 34726489096899600)
    for name, value in (
        ("valid_initial_seven", valid),
        ("direct_genesect_launch", direct),
        ("vip_only_increment", vip),
        ("unconditional_launch", total),
        ("conditional_valid_seven", total / valid),
        ("conditional_opening_mew", total / mew),
    ):
        print(f"{name}: {float(value):.12%}; exact={value}")


if __name__ == "__main__":
    main()
