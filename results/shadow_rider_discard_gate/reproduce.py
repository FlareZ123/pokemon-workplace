"""Conditional discard-safe stock sensitivity for Radiant Eternatus launch.

A distinguished exogenous subset d of the champion deck's 38 'other' cards
is safe to discard. Everything else is protected. Integrates the fraction
of safe hands exactly into the existing grouped Treasure launch probability.
This is a strict hypothetical DCI gate, not a learned real-play policy.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb, prod

from results.shadow_rider_radiant_launch.reproduce import (
    COUNTS,
    allocations,
    classify,
    exact,
)


def presence_if_other_hand(d: int, h: int, total_other: int) -> Fraction:
    """Hypergeometric chance >=1 safe other card in a hand of h others."""
    if not 0 <= d <= total_other:
        raise ValueError("safe category count outside existing other-card stock")
    if not 0 <= h <= total_other:
        raise ValueError("other-hand count outside underlying class population")
    if h > total_other - d:
        return Fraction(1)
    return 1 - Fraction(comb(total_other - d, h), comb(total_other, h))


def treasure_two_by_other_hand(
    caps: tuple[int, ...] = COUNTS,
    opening_size: int = 7,
    prize_size: int = 6,
) -> dict[int, Fraction]:
    """Distribution of other hand count for the unconstrained Treasure route."""
    n = sum(caps)
    eligible = comb(n, opening_size) - comb(
        n - caps[0] - caps[3], opening_size
    )
    total = (
        eligible
        * comb(n - opening_size, prize_size)
        * (n - opening_size - prize_size)
    )
    masses: Counter[int] = Counter()

    for opening in allocations(opening_size, caps):
        if opening[0] + opening[3] == 0:
            continue
        op_weight = prod(comb(c, x) for c, x in zip(caps, opening))
        after_opening = tuple(c - x for c, x in zip(caps, opening))
        for prizes in allocations(prize_size, after_opening):
            prize_weight = op_weight * prod(
                comb(c, x) for c, x in zip(after_opening, prizes)
            )
            after_prizes = tuple(
                c - x for c, x in zip(after_opening, prizes)
            )
            for draw_index, copies in enumerate(after_prizes):
                if not copies:
                    continue
                if classify(opening, prizes, draw_index, caps) != "treasure_2":
                    continue
                h = opening[4] + int(draw_index == 4)
                masses[h] += prize_weight * copies

    return {
        h: Fraction(mass, total)
        for h, mass in sorted(masses.items())
    }


def safe_route_probability(
    d: int,
    masses: dict[int, Fraction],
    *,
    total_other: int = COUNTS[4],
) -> Fraction:
    """P(treasure dual-launch AND safely payable) under strict DCI partition."""
    return sum(
        (
            probability
            * presence_if_other_hand(d, h, total_other)
            for h, probability in masses.items()
        ),
        Fraction(0),
    )


def toy_physical_oracle() -> None:
    """Compare analytic safe inclusion with exact individual-card enumeration."""
    caps = (1, 2, 1, 2, 4)
    safe_d = 2
    ids = tuple(
        (category, instance)
        for category, quantity in enumerate(caps)
        for instance in range(quantity)
    )
    total = 0
    pay_success = 0
    directly_ready = 0

    for opener in combinations(range(len(ids)), 3):
        oc = Counter(ids[i][0] for i in opener)
        if not oc[0] and not oc[3]:
            continue
        rest = [i for i in range(len(ids)) if i not in opener]
        for prize_set in combinations(rest, 2):
            pc = Counter(ids[i][0] for i in prize_set)
            left = [i for i in rest if i not in prize_set]
            for draw in left:
                opening = tuple(oc[i] for i in range(5))
                prizes = tuple(pc[i] for i in range(5))
                outcome = classify(opening, prizes, ids[draw][0], caps)
                hand_ids = opener + (draw,)
                has_safe = any(
                    ids[i][0] == 4 and ids[i][1] < safe_d
                    for i in hand_ids
                )
                if outcome == "direct_2":
                    directly_ready += 1
                if outcome == "treasure_2" and has_safe:
                    pay_success += 1
                total += 1

    masses = treasure_two_by_other_hand(caps, 3, 2)
    paying = safe_route_probability(safe_d, masses, total_other=4)
    assert paying == Fraction(pay_success, total)
    direct = exact(caps, 3, 2)["direct_2"]
    assert direct == Fraction(directly_ready, total)
    print(f"Exact payment/physical oracle passed: {total} toy worlds")


def main() -> None:
    toy_physical_oracle()
    masses = treasure_two_by_other_hand()
    baseline = exact()
    assert sum(masses.values()) == baseline["treasure_2"]
    direct = baseline["direct_2"]
    assert direct == Fraction(2431309737, 20230837760)
    assert masses[0] > 0
    assert safe_route_probability(0, masses) == 0

    for d in (0, 1, 2, 4, 8, 10, 12, 16, 20, 24, 32, 38):
        treasure = safe_route_probability(d, masses)
        total = direct + treasure
        assert direct <= total <= direct + baseline["treasure_2"]
        print(
            f"safe d={d:2d}/38: treasure={float(treasure):.12%}, "
            f"total dual launch={float(total):.12%}"
        )

    assert safe_route_probability(10, masses) > Fraction(23, 100)
    assert safe_route_probability(20, masses) > Fraction(30, 100)
    assert (
        baseline["treasure_2"] - safe_route_probability(38, masses)
        == masses[0]
    )
    print(f"Unpayable even at d=38 (no other hand): {float(masses[0]):.12%}")


if __name__ == "__main__":
    main()
