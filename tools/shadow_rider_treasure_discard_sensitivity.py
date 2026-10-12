"""Exact discard-payment sensitivity of the Aichi champion's Radiant launch.

A six-category hypergeometric model preserves the real list's counts while
testing declared *hypothetical* discard-conservation policies. This is an
opening-access and opportunity-cost sensitivity, not an optimal-play model.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb, prod

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    ENERGY,
    POKEMON,
    TRAINERS,
)
from results.shadow_rider_radiant_launch.reproduce import exact as original_exact

# Radiant / Shadow Rider VMAX / Mysterious Treasure / other Basics /
# Psychic Energy / all remaining cards.
COUNTS = (1, 4, 4, 13, 11, 27)
ROUTES = (
    "direct",
    "treasure_free",
    "treasure_energy",
    "treasure_energy_2",
    "treasure_spare_treasure",
    "treasure_energy_spare",
    "treasure_energy2_spare",
    "treasure_energy2_spare_vmax",
)


@lru_cache(maxsize=None)
def allocations(total: int, caps: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """Enumerate all physical category multiplicities in an unordered draw."""

    def visit(index: int, left: int, prefix: tuple[int, ...]):
        if index == len(caps) - 1:
            if 0 <= left <= caps[index]:
                yield prefix + (left,)
            return
        for number in range(min(caps[index], left) + 1):
            yield from visit(index + 1, left - number, prefix + (number,))

    return tuple(visit(0, total, ()))


def success_flags(
    opening: tuple[int, ...],
    prizes: tuple[int, ...],
    drawn_category: int,
    caps: tuple[int, ...],
) -> dict[str, bool] | None:
    """Classify one accepted opening, six Prizes and first going-second draw.

    A different non-Radiant Basic must start Active from the opening seven.
    The sole Treasure played is removed from hand before discard selection.
    """
    if opening[0] + opening[3] == 0:
        return None  # Mulligan; excluded from denominator.

    flags = {route: False for route in ROUTES}
    if opening[3] == 0:
        return flags  # Radiant is the only possible starting Basic.

    hand = tuple(
        opening[index] + int(index == drawn_category)
        for index in range(len(caps))
    )
    deck = tuple(
        caps[index] - opening[index] - prizes[index]
        - int(index == drawn_category)
        for index in range(len(caps))
    )
    if deck[1] < 2:
        return flags

    if hand[0]:
        flags["direct"] = True
        return flags

    # Radiant must remain in the deck and one Treasure must be held.
    if deck[0] == 0 or hand[2] == 0:
        return flags

    flags["treasure_free"] = True
    energy = hand[4]
    treasures = hand[2]
    vmax = hand[1]

    flags["treasure_energy"] = energy >= 1
    flags["treasure_energy_2"] = energy >= 2
    flags["treasure_spare_treasure"] = treasures >= 2
    flags["treasure_energy_spare"] = energy >= 1 or treasures >= 2
    flags["treasure_energy2_spare"] = energy >= 2 or treasures >= 2
    flags["treasure_energy2_spare_vmax"] = (
        energy >= 2 or treasures >= 2 or vmax >= 1
    )
    return flags


def exact(
    caps: tuple[int, ...] = COUNTS,
    *,
    opening_size: int = 7,
    prize_count: int = 6,
) -> dict[str, Fraction]:
    """Exact probabilities conditional on a legal Basic-containing opening."""
    n = sum(caps)
    opening_ways = (
        comb(n, opening_size)
        - comb(n - caps[0] - caps[3], opening_size)
    )
    denominator = (
        opening_ways * comb(n - opening_size, prize_count)
        * (n - opening_size - prize_count)
    )
    outcomes: dict[str, int] = defaultdict(int)
    accounted = 0

    for opening in allocations(opening_size, caps):
        if opening[0] + opening[3] == 0:
            continue
        opening_weight = prod(
            comb(cap, n_drawn) for cap, n_drawn in zip(caps, opening)
        )
        after_opening = tuple(c - x for c, x in zip(caps, opening))
        for prizes in allocations(prize_count, after_opening):
            prize_weight = opening_weight * prod(
                comb(cap, n_prized)
                for cap, n_prized in zip(after_opening, prizes)
            )
            after_prizes = tuple(
                c - x for c, x in zip(after_opening, prizes)
            )
            for draw, available in enumerate(after_prizes):
                if not available:
                    continue
                weight = prize_weight * available
                accounted += weight
                flags = success_flags(opening, prizes, draw, caps)
                assert flags is not None
                for route, success in flags.items():
                    if success:
                        outcomes[route] += weight

    assert accounted == denominator
    return {
        route: Fraction(outcomes[route], denominator)
        for route in ROUTES
    }


def physical_oracle() -> int:
    """Independently enumerate labeled 11-card toy opening/Prize/draw deals."""
    caps = (1, 2, 2, 2, 2, 2)
    physical = tuple(
        category for category, count in enumerate(caps)
        for _copy in range(count)
    )
    counted: dict[str, int] = defaultdict(int)
    accepted = 0
    for opened in combinations(range(len(physical)), 3):
        opening = tuple(
            sum(physical[index] == category for index in opened)
            for category in range(len(caps))
        )
        remaining = tuple(i for i in range(len(physical)) if i not in opened)
        for prized in combinations(remaining, 2):
            prizes = tuple(
                sum(physical[index] == category for index in prized)
                for category in range(len(caps))
            )
            for drawn in remaining:
                if drawn in prized:
                    continue
                flags = success_flags(
                    opening, prizes, physical[drawn], caps
                )
                if flags is None:
                    continue
                accepted += 1
                for route, success in flags.items():
                    counted[route] += int(success)

    grouped = exact(caps, opening_size=3, prize_count=2)
    for route, probability in grouped.items():
        assert probability == Fraction(counted[route], accepted), route
    return accepted


def run() -> dict[str, Fraction]:
    assert sum(POKEMON.values()) + sum(TRAINERS.values()) + sum(
        ENERGY.values()
    ) == 60
    assert POKEMON["Radiant Eternatus"] == COUNTS[0]
    assert POKEMON["Shadow Rider Calyrex VMAX"] == COUNTS[1]
    assert TRAINERS["Mysterious Treasure"] == COUNTS[2]
    assert sum(POKEMON.values()) - COUNTS[0] - COUNTS[1] == COUNTS[3]
    assert ENERGY == {"Psychic Energy": COUNTS[4]}
    assert sum(COUNTS) == 60

    assert physical_oracle() == 18312
    result = exact()
    original = original_exact()
    assert result["direct"] == original["direct_2"]
    assert result["treasure_free"] == original["treasure_2"]
    assert result["direct"] == Fraction(2431309737, 20230837760)
    assert result["treasure_energy"] == Fraction(402091494907, 1618467020800)
    assert result["treasure_energy2_spare"] == Fraction(
        44709766217, 278174019200
    )
    assert result["treasure_energy2_spare_vmax"] == Fraction(
        284582197, 1241848300
    )
    assert (
        result["treasure_spare_treasure"]
        <= result["treasure_energy2_spare"]
        <= result["treasure_energy_spare"]
        <= result["treasure_free"]
    )
    for route, probability in result.items():
        assert 0 <= probability <= 1, route
    return result


if __name__ == "__main__":
    output = run()
    for route, probability in output.items():
        print(
            f"{route}: Treasure-route={float(probability):.9%}, "
            f"total-with-direct={float(probability+output['direct']):.9%}"
            if route != "direct"
            else f"direct: {float(probability):.9%}"
        )
    print("Six-category discard sensitivity and physical oracle passed")
