"""Exact 2026 Aichi Shadow Rider Radiant launch with Hisuian Heavy Ball.

Source-driven groups: Radiant Eternatus, Shadow Rider VMAX, Mysterious
Treasure, Hisuian Heavy Ball, other initial Basic, remaining filler.
The named routes take at most one natural first-turn draw. The finite model
assumes access to a discardable card for Mysterious Treasure.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from math import comb, prod

# Index: Radiant, VMAX, Treasure, Heavy Ball, other Basic, other cards.
COUNTS = (1, 4, 4, 1, 13, 37)


def allocations(total: int, caps: tuple[int, ...]):
    """Enumerate category-count vectors summing to total."""

    if len(caps) == 1:
        if 0 <= total <= caps[0]:
            yield (total,)
        return
    for value in range(min(total, caps[0]) + 1):
        for tail in allocations(total - value, caps[1:]):
            yield (value,) + tail


def classify(
    opening: tuple[int, ...],
    prizes: tuple[int, ...],
    drawn: int | None,
    caps: tuple[int, ...],
) -> str:
    """Route the accessible Radiant and VMAX stock in one physical world.

    Opening Active choice is fixed before the draw and Prize search: only
    an *other* Basic in opening seven can provide the requisite starting
    Active while Radiant is played later from hand onto the Bench.
    """

    if opening[0] + opening[4] == 0:
        return "reject"
    if opening[4] == 0:
        return "no_eligible_active"

    hand = tuple(
        opening[index] + int(drawn == index)
        for index in range(len(caps))
    )
    deck = tuple(
        caps[index] - opening[index] - prizes[index] - int(drawn == index)
        for index in range(len(caps))
    )
    if hand[0]:
        route = "direct"
    elif hand[3] and prizes[0]:
        # Hisuian Heavy Ball swaps the Prized Radiant for itself. This does
        # not change the number of Shadow Rider VMAX still in the deck.
        route = "heavy"
    elif hand[2] and deck[0]:
        route = "treasure"
    else:
        return "no_radiant_access"
    return f"{route}_{min(2, deck[1])}"


def exact(
    caps: tuple[int, ...] = COUNTS,
    *,
    opening_size: int = 7,
    prize_count: int = 6,
    first_turn_draw: bool = True,
) -> dict[str, Fraction]:
    """Sum every accepted opening, six-Prize subset and possible first draw."""

    n = sum(caps)
    opening_ways = comb(n, opening_size) - comb(
        n - caps[0] - caps[4], opening_size
    )
    first_deck_size = n - opening_size - prize_count
    denominator = opening_ways * comb(n - opening_size, prize_count)
    if first_turn_draw:
        denominator *= first_deck_size

    weighted = Counter()
    for opening in allocations(opening_size, caps):
        if opening[0] + opening[4] == 0:
            continue
        opening_weight = prod(comb(count, qty) for count, qty in zip(caps, opening))
        post_opening = tuple(count - qty for count, qty in zip(caps, opening))

        for prizes in allocations(prize_count, post_opening):
            prize_weight = opening_weight * prod(
                comb(count, qty) for count, qty in zip(post_opening, prizes)
            )
            post_prizes = tuple(
                count - qty for count, qty in zip(post_opening, prizes)
            )
            if first_turn_draw:
                for drawn, available in enumerate(post_prizes):
                    if available:
                        weighted[classify(opening, prizes, drawn, caps)] += (
                            prize_weight * available
                        )
            else:
                weighted[classify(opening, prizes, None, caps)] += prize_weight

    if sum(weighted.values()) != denominator:
        raise AssertionError("physical category mass was not conserved")
    return {
        name: Fraction(weight, denominator)
        for name, weight in sorted(weighted.items())
    }


def launch_probability(results: dict[str, Fraction]) -> Fraction:
    return sum(
        (probability for name, probability in results.items() if name.endswith("_2")),
        start=Fraction(0),
    )


def baseline_without_heavy_route(
    results: dict[str, Fraction],
) -> Fraction:
    """Retain the direct/Treasure outcome mass in the actual same 60-card list."""

    return results["direct_2"] + results["treasure_2"]
