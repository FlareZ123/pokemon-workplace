"""Exact search-target availability after setup conditioning and early exposure.

This module computes the probability that specified non-Basic target groups still
have enough copies in the deck at a search window after:
1. an accepted opening hand containing at least one forced Basic starter;
2. Prize cards;
3. a fixed number of ordinary pre-search draws.

Target groups are assumed to be disjoint from the forced-starter class.
"""

from __future__ import annotations

from itertools import product
from math import comb


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def conditioned_searchability(
    deck_size: int,
    forced_starters: int,
    target_copies: tuple[int, ...],
    *,
    opening_hand_size: int = 7,
    prize_count: int = 6,
    pre_search_draws: int = 1,
    required_remaining: tuple[int, ...] | None = None,
) -> float:
    """Return P(required target copies remain in deck | accepted opening).

    Prize cards and ordinary draws are combined into one random exposed block,
    since neither operation selects cards by identity.

    Example:
        target_copies=(2, 1), required_remaining=(1, 1)
    asks for the probability that at least one copy from a two-copy target group
    and the singleton target both remain searchable.
    """
    target_copies = tuple(target_copies)
    if required_remaining is None:
        required_remaining = (1,) * len(target_copies)
    required_remaining = tuple(required_remaining)

    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if forced_starters <= 0:
        raise ValueError("forced_starters must be positive")
    if len(target_copies) != len(required_remaining):
        raise ValueError("required_remaining must match target_copies")
    if any(copies < 0 for copies in target_copies):
        raise ValueError("target copy counts must be non-negative")
    if any(need < 0 for need in required_remaining):
        raise ValueError("required copy counts must be non-negative")
    if any(need > copies for need, copies in zip(required_remaining, target_copies)):
        return 0.0
    if opening_hand_size < 0 or prize_count < 0 or pre_search_draws < 0:
        raise ValueError("zone sizes must be non-negative")
    if opening_hand_size + prize_count + pre_search_draws > deck_size:
        raise ValueError("opening, Prize cards, and draws exceed deck size")

    target_total = sum(target_copies)
    filler = deck_size - forced_starters - target_total
    if filler < 0:
        raise ValueError("category counts exceed deck size")

    total_openings = _choose(deck_size, opening_hand_size)
    rejected_openings = _choose(
        deck_size - forced_starters,
        opening_hand_size,
    )
    accepted_openings = total_openings - rejected_openings
    if accepted_openings == 0:
        raise ValueError("accepted opening has zero probability")

    exposed_count = prize_count + pre_search_draws
    remaining_deck_size = deck_size - opening_hand_size
    exposed_denominator = _choose(remaining_deck_size, exposed_count)

    success = 0.0

    opening_ranges = tuple(
        range(min(copies, opening_hand_size) + 1)
        for copies in target_copies
    )

    for target_in_hand in product(*opening_ranges):
        target_hand_total = sum(target_in_hand)
        max_starters = min(
            forced_starters,
            opening_hand_size - target_hand_total,
        )

        for starters_in_hand in range(1, max_starters + 1):
            filler_in_hand = (
                opening_hand_size
                - target_hand_total
                - starters_in_hand
            )
            if not 0 <= filler_in_hand <= filler:
                continue

            opening_ways = (
                _choose(forced_starters, starters_in_hand)
                * _choose(filler, filler_in_hand)
            )
            for copies, used in zip(target_copies, target_in_hand):
                opening_ways *= _choose(copies, used)
            if opening_ways == 0:
                continue

            opening_mass = opening_ways / accepted_openings
            remaining_targets = tuple(
                copies - used
                for copies, used in zip(target_copies, target_in_hand)
            )
            remaining_starters = forced_starters - starters_in_hand
            remaining_filler = filler - filler_in_hand

            exposed_ranges = tuple(
                range(min(copies, exposed_count) + 1)
                for copies in remaining_targets
            )

            for target_exposed in product(*exposed_ranges):
                target_exposed_total = sum(target_exposed)
                max_exposed_starters = min(
                    remaining_starters,
                    exposed_count - target_exposed_total,
                )

                for exposed_starters in range(max_exposed_starters + 1):
                    exposed_filler = (
                        exposed_count
                        - target_exposed_total
                        - exposed_starters
                    )
                    if not 0 <= exposed_filler <= remaining_filler:
                        continue

                    exposed_ways = (
                        _choose(remaining_starters, exposed_starters)
                        * _choose(remaining_filler, exposed_filler)
                    )
                    for copies, used in zip(
                        remaining_targets,
                        target_exposed,
                    ):
                        exposed_ways *= _choose(copies, used)
                    if exposed_ways == 0:
                        continue

                    still_searchable = all(
                        copies - used >= need
                        for copies, used, need in zip(
                            remaining_targets,
                            target_exposed,
                            required_remaining,
                        )
                    )
                    if still_searchable:
                        success += (
                            opening_mass
                            * exposed_ways
                            / exposed_denominator
                        )

    return success


def accepted_opening_probability(
    deck_size: int,
    forced_starters: int,
    *,
    opening_hand_size: int = 7,
) -> float:
    """Return P(opening hand contains at least one forced starter)."""
    return 1.0 - (
        _choose(deck_size - forced_starters, opening_hand_size)
        / _choose(deck_size, opening_hand_size)
    )


def main() -> None:
    base = dict(
        deck_size=60,
        forced_starters=14,
        opening_hand_size=7,
        prize_count=6,
        pre_search_draws=1,
    )
    profiles = (
        (1,),
        (2,),
        (3,),
        (4,),
        (2, 2),
        (2, 1),
        (2, 2, 2, 1),
    )

    print("target profile | probability all groups remain searchable")
    for profile in profiles:
        probability = conditioned_searchability(
            target_copies=profile,
            **base,
        )
        print(f"{str(profile):20s} | {100 * probability:.6f}%")


if __name__ == "__main__":
    main()
