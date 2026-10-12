"""Exact state-dependent discard-cost sensitivity for a real Shadow Rider list.

Mysterious Treasure must discard another card from hand before fetching
Radiant Eternatus. The general legal action is known to be payable
mechanically at the modeled time. This study prices deliberately restricted
acceptable cost families instead of assuming any held card is expendable.

It refines only Treasure -> Radiant -> two VMAX; direct Radiant and Heavy Ball
routes remain separately available. Unknown discard opportunity costs mean
these are hypothetical policy sensitivity curves rather than true win rates.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from math import comb, prod

from shadow_rider_heavy_ball_launch import COUNTS, allocations, classify


def treasure_two_vmax_hand_buckets(
    caps: tuple[int, ...] = COUNTS,
    *,
    opening_size: int = 7,
    prize_count: int = 6,
    first_turn_draw: bool = True,
) -> dict[tuple[int, int], Fraction]:
    """P(unconditional accepted start; Treasure route; Fhand; Treasurehand).

    All copies in the broad 'other' category are exchangeable before a
    specific discardable subset is designated; the subcategory event can
    therefore be conditioned exactly from the hand count without expanding
    the whole opening-and-Prize combinatorial state space.
    """

    n = sum(caps)
    accepted = comb(n, opening_size) - comb(
        n - caps[0] - caps[4], opening_size
    )
    denominator = accepted * comb(n - opening_size, prize_count)
    if first_turn_draw:
        denominator *= n - opening_size - prize_count

    weighted: Counter[tuple[int, int]] = Counter()
    for opening in allocations(opening_size, caps):
        if opening[0] + opening[4] == 0:
            continue
        opening_weight = prod(
            comb(count, amount) for count, amount in zip(caps, opening)
        )
        post_opening = tuple(c - o for c, o in zip(caps, opening))
        for prizes in allocations(prize_count, post_opening):
            prizes_weight = opening_weight * prod(
                comb(c, p) for c, p in zip(post_opening, prizes)
            )
            post_prizes = tuple(c - p for c, p in zip(post_opening, prizes))
            draws = (
                ((index, available) for index, available in enumerate(post_prizes)
                 if available)
                if first_turn_draw else ((None, 1),)
            )
            for drawn, draw_weight in draws:
                if classify(opening, prizes, drawn, caps) != "treasure_2":
                    continue
                filler_in_hand = opening[5] + int(drawn == 5)
                treasures_in_hand = opening[2] + int(drawn == 2)
                weighted[(filler_in_hand, treasures_in_hand)] += (
                    prizes_weight * draw_weight
                )

    return {
        bucket: Fraction(weight, denominator)
        for bucket, weight in sorted(weighted.items())
    }


def acceptable_discard_probability(
    buckets: dict[tuple[int, int], Fraction],
    *,
    safe_filler_copies: int,
    total_filler_copies: int = COUNTS[5],
    allow_spare_treasure: bool = False,
) -> Fraction:
    """Exact unconditional Treasure-route probability under named cost policy.

    A subset of the generic filler cards is declared acceptable to discard.
    Conditional on h filler draws in hand, its chance to appear is
        1 - C(F-K,h) / C(F,h).
    Optionally another held Treasure is acceptable: this requires at least
    two total Treasures in hand (one is played, another pays its discard).
    """

    if not 0 <= safe_filler_copies <= total_filler_copies:
        raise ValueError("safe filler count outside the total filler pool")

    probability = Fraction(0)
    for (filler_hand, treasure_hand), event_probability in buckets.items():
        if allow_spare_treasure and treasure_hand >= 2:
            acceptance = Fraction(1)
        elif filler_hand == 0:
            acceptance = Fraction(0)
        elif filler_hand > total_filler_copies - safe_filler_copies:
            acceptance = Fraction(1)
        else:
            acceptance = Fraction(1) - Fraction(
                comb(total_filler_copies - safe_filler_copies, filler_hand),
                comb(total_filler_copies, filler_hand),
            )
        probability += event_probability * acceptance
    return probability


def named_cost_frontier(
    safe_counts: tuple[int, ...] = (0, 1, 2, 4, 8, 11, 16, 24, 37),
) -> tuple[tuple[int, Fraction, Fraction], ...]:
    """Return strict filler-only and filler-or-spare-Treasure action access."""

    buckets = treasure_two_vmax_hand_buckets()
    return tuple(
        (
            count,
            acceptable_discard_probability(
                buckets, safe_filler_copies=count
            ),
            acceptable_discard_probability(
                buckets, safe_filler_copies=count,
                allow_spare_treasure=True
            ),
        )
        for count in safe_counts
    )
