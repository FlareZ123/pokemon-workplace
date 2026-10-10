"""Exact opening-hand and Prize zone odds for a Grand Tree chain.

Given one designated Basic in the opening hand, 59 other cards divide into
6 other hand cards, 6 Prize cards, and 47 searchable deck cards. Stage 1
and Stage 2 copies are distinguished from exchangeable filler cards.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class ZoneAccess:
    full_chain: Fraction
    stage1_only: Fraction
    no_stage1: Fraction
    stage1_with_stage2_all_prized: Fraction

    def __post_init__(self) -> None:
        if self.full_chain + self.stage1_only + self.no_stage1 != 1:
            raise ValueError("outcome categories must sum to one")


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def check(n: int, hand: int, prizes: int, first: int, second: int) -> None:
    if min(n, hand, prizes, first, second) < 0:
        raise ValueError("counts must be nonnegative")
    if hand + prizes > n or first + second > n:
        raise ValueError("card counts exceed population")


def probability_full(
    *, n: int = 59, hand: int = 6, prizes: int = 6,
    first: int = 1, second: int = 1,
) -> Fraction:
    """Inclusion-exclusion for >=1 of each evolution stage in the deck."""
    check(n, hand, prizes, first, second)
    out = hand + prizes
    return (
        Fraction(1)
        - Fraction(choose(out, first), choose(n, first))
        - Fraction(choose(out, second), choose(n, second))
        + Fraction(choose(out, first + second), choose(n, first + second))
    )


def enumerate_access(
    *, n: int = 59, hand: int = 6, prizes: int = 6,
    first: int = 1, second: int = 1,
) -> ZoneAccess:
    """Independently enumerate Stage1/Stage2 allocations to hand/Prize/deck.

    Sequentially choose a uniformly random hand subset and then a random
    Prize subset from the remaining population. Each category allocation
    has its exact combinatorial multiplicity.
    """
    check(n, hand, prizes, first, second)
    filler = n - first - second
    total = choose(n, hand) * choose(n - hand, prizes)
    full = only = none = all_prized = 0

    for h1 in range(min(first, hand) + 1):
        for h2 in range(min(second, hand - h1) + 1):
            hf = hand - h1 - h2
            if hf > filler:
                continue
            hand_ways = choose(first, h1) * choose(second, h2) * choose(filler, hf)
            left1, left2, leftf = first - h1, second - h2, filler - hf
            for p1 in range(min(left1, prizes) + 1):
                for p2 in range(min(left2, prizes - p1) + 1):
                    weight = (
                        hand_ways
                        * choose(left1, p1)
                        * choose(left2, p2)
                        * choose(leftf, prizes - p1 - p2)
                    )
                    d1, d2 = left1 - p1, left2 - p2
                    if d1 == 0:
                        none += weight
                    elif d2 == 0:
                        only += weight
                    else:
                        full += weight
                    if d1 > 0 and p2 == second:
                        all_prized += weight

    if full + only + none != total:
        raise AssertionError("zone enumeration failed normalization")
    return ZoneAccess(
        Fraction(full, total), Fraction(only, total),
        Fraction(none, total), Fraction(all_prized, total),
    )
