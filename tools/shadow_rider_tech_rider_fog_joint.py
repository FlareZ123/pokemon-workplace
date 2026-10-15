"""Joint singleton Psychic counter + Shadow Rider V access with Fog contention.

Only Fog Crystal in the first seven is allowed as a search connector. One
copy of Fog may fetch one missing Basic Psychic target; both target classes
must be in hand or still searchable in the deck after six initial Prizes.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def two_target_fog_access(
    *, deck_size: int, basic_count: int, rider_count: int,
    fog_count: int, hand_size: int, prize_count: int
) -> tuple[Fraction, Fraction, dict[int, Fraction]]:
    """Return P(valid Basic), P(both targets | valid), and searches-needed split.

    One singleton Psychic Basic counter is part of basic_count; the named
    Rider class contains rider_count copies, also part of basic_count.
    Search-count branches 0, 1 and 2 are mutually exclusive.
    """
    n, b, r, f, h, p = (
        deck_size, basic_count, rider_count, fog_count, hand_size, prize_count
    )
    if (
        n < 1 or not 2 <= b <= n or not 1 <= r < b
        or not 0 <= f <= n-b or not 1 <= h < n-p
        or not 0 <= p < n-h
    ):
        raise ValueError("invalid 60-card physical allocation parameters")

    other_basics = b - 1 - r
    other_cards = n - b - f
    total_initial_hands = comb(n, h)
    total_prize_allocations = comb(n-h, p)
    denominator = total_initial_hands * total_prize_allocations
    valid = Fraction(
        total_initial_hands - choose(n-b, h), total_initial_hands
    )
    successes = {0: 0, 1: 0, 2: 0}

    for tech_hand in (0, 1):
        for rider_hand in range(min(r, h-tech_hand) + 1):
            for other_basic_hand in range(
                min(other_basics, h-tech_hand-rider_hand) + 1
            ):
                for fog_hand in range(
                    min(f, h-tech_hand-rider_hand-other_basic_hand) + 1
                ):
                    other_hand = (
                        h - tech_hand - rider_hand
                        - other_basic_hand - fog_hand
                    )
                    ways = (
                        choose(1, tech_hand)
                        * choose(r, rider_hand)
                        * choose(other_basics, other_basic_hand)
                        * choose(f, fog_hand)
                        * choose(other_cards, other_hand)
                    )
                    if not ways or not (
                        tech_hand + rider_hand + other_basic_hand
                    ):
                        continue

                    need_tech = int(tech_hand == 0)
                    need_rider = int(rider_hand == 0)
                    searches = need_tech + need_rider
                    if fog_hand < searches:
                        continue

                    tech_remaining = 1 - tech_hand
                    rider_remaining = r - rider_hand
                    other_remaining = (
                        n - h - tech_remaining - rider_remaining
                    )
                    prize_compatible = 0
                    for tech_prized in range(
                        min(tech_remaining, p) + 1
                    ):
                        for rider_prized in range(
                            min(rider_remaining, p-tech_prized) + 1
                        ):
                            if need_tech and tech_prized == tech_remaining:
                                continue
                            if need_rider and rider_prized == rider_remaining:
                                continue
                            prize_compatible += (
                                choose(tech_remaining, tech_prized)
                                * choose(rider_remaining, rider_prized)
                                * choose(
                                    other_remaining,
                                    p-tech_prized-rider_prized,
                                )
                            )
                    successes[searches] += ways * prize_compatible

    partition = {
        searches: Fraction(count, denominator) / valid
        for searches, count in successes.items()
    }
    return valid, sum(partition.values(), Fraction(0)), partition
