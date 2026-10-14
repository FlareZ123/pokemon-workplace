"""Exact next-natural-draw Psychic reserve following a two-VMAX Treasure launch.

In the named line, starting deck 46 after the first draw loses Radiant from
Mysterious Treasure and exactly two Shadow Rider VMAX from Climactic Gate.
The shuffled next-turn deck therefore has 43 cards before the next draw.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from math import comb, prod

from tools.shadow_rider_heavy_ball_launch import (
    COUNTS,
    allocations,
    classify,
)


def treasure_hand_prize_buckets(
    caps: tuple[int, ...] = COUNTS,
    *,
    opening_size: int = 7,
    prize_count: int = 6,
) -> dict[tuple[int, int, int], Fraction]:
    """Probability mass by (held filler, Prized filler, held Treasure)."""

    n = sum(caps)
    accepted = comb(n, opening_size) - comb(
        n - caps[0] - caps[4], opening_size
    )
    denominator = (
        accepted
        * comb(n - opening_size, prize_count)
        * (n - opening_size - prize_count)
    )
    weights: Counter[tuple[int, int, int]] = Counter()

    for opening in allocations(opening_size, caps):
        if opening[0] + opening[4] == 0:
            continue
        first = prod(
            comb(count, copies)
            for count, copies in zip(caps, opening)
        )
        remaining = tuple(c - o for c, o in zip(caps, opening))
        for prizes in allocations(prize_count, remaining):
            ways = first * prod(
                comb(count, copies)
                for count, copies in zip(remaining, prizes)
            )
            post_prize = tuple(
                c - p for c, p in zip(remaining, prizes)
            )
            for drawn, count in enumerate(post_prize):
                if not count or classify(
                    opening, prizes, drawn, caps
                ) != "treasure_2":
                    continue
                hand_filler = opening[5] + int(drawn == 5)
                hand_treasure = opening[2] + int(drawn == 2)
                weights[(
                    hand_filler,
                    prizes[5],
                    hand_treasure,
                )] += ways * count

    return {
        key: Fraction(weight, denominator)
        for key, weight in sorted(weights.items())
    }


def next_draw_psychic_readiness(
    *,
    at_least_after_draw: int,
    allow_spare_treasure_payment: bool = False,
    caps: tuple[int, ...] = COUNTS,
    opening_size: int = 7,
    prize_count: int = 6,
    psychic_energy: int = 11,
    buckets: dict[tuple[int, int, int], Fraction] | None = None,
) -> Fraction:
    """Exact route mass with Psychic in hand after its next natural draw.

    Condition on the physically available two-VMAX Treasure route and
    search/shuffle effects. Additional draw, disruption, attachment, and
    full turn action sequences are outside this partial continuation.
    """

    if at_least_after_draw < 0:
        raise ValueError("at_least_after_draw cannot be negative")
    filler_total = caps[5]
    if not 0 <= psychic_energy <= filler_total:
        raise ValueError("invalid Psychic count")
    n = sum(caps)
    post_search_deck = n - opening_size - prize_count - 1 - 3
    if post_search_deck <= 0:
        raise ValueError("post-search deck must permit one natural draw")

    state_buckets = (
        treasure_hand_prize_buckets(
            caps,
            opening_size=opening_size,
            prize_count=prize_count,
        )
        if buckets is None else buckets
    )
    denominator = comb(filler_total, psychic_energy)
    success = Fraction()
    for (hand_filler, prized_filler, held_treasure), route_mass in (
        state_buckets.items()
    ):
        deck_filler = filler_total - hand_filler - prized_filler
        for hand_psychic in range(
            min(hand_filler, psychic_energy) + 1
        ):
            for prize_psychic in range(
                min(prized_filler, psychic_energy - hand_psychic) + 1
            ):
                deck_psychic = (
                    psychic_energy - hand_psychic - prize_psychic
                )
                if not 0 <= deck_psychic <= deck_filler:
                    continue
                position_weight = Fraction(
                    comb(hand_filler, hand_psychic)
                    * comb(prized_filler, prize_psychic)
                    * comb(deck_filler, deck_psychic),
                    denominator,
                )
                pay_spare = (
                    allow_spare_treasure_payment
                    and held_treasure >= 2
                )
                if not pay_spare and hand_psychic == 0:
                    continue
                energy_after_payment = (
                    hand_psychic
                    if pay_spare else hand_psychic - 1
                )
                if energy_after_payment >= at_least_after_draw:
                    ready = Fraction(1)
                elif energy_after_payment == at_least_after_draw - 1:
                    ready = Fraction(deck_psychic, post_search_deck)
                else:
                    ready = Fraction()
                success += route_mass * position_weight * ready
    return success
