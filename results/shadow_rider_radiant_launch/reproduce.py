"""Exact Radiant Eternatus two-VMAX first-turn access in Aichi champion baseline.

Categories: Radiant Eternatus, Shadow Rider VMAX, Mysterious Treasure,
other opening-eligible Basics, all remaining cards. Prize sets and turn-one
draws follow the basic setup rulebook, with an independent physical toy oracle.

This is a mechanical access model, not a match win-rate simulator. Strategic
discard acceptability and alternative draw/search lines are intentionally out.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb, prod

from results.competitive_deck_baselines.shadow_rider_reproduce import (
    ENERGY,
    POKEMON,
    TRAINERS,
)

CATEGORIES = ("radiant", "shadow_vmax", "treasure", "other_basic", "other")
COUNTS = (1, 4, 4, 13, 38)


def allocations(total: int, caps: tuple[int, ...]):
    """Yield all bounded category counts for a sample of fixed size."""

    def visit(index: int, left: int, prefix: tuple[int, ...]):
        if index == len(caps) - 1:
            if 0 <= left <= caps[index]:
                yield prefix + (left,)
            return
        for value in range(min(caps[index], left) + 1):
            yield from visit(index + 1, left - value, prefix + (value,))

    yield from visit(0, total, ())


def classify(
    opening: tuple[int, ...],
    prizes: tuple[int, ...],
    draw_index: int,
    caps: tuple[int, ...],
) -> str:
    """Classify an accepted opening with one first-turn going-second draw."""
    if opening[0] + opening[3] == 0:
        return "reject"
    if opening[3] == 0:
        return "no_eligible_active"

    hand = [opening[i] + int(i == draw_index) for i in range(len(caps))]
    hand[3] -= 1  # Reserve one eligible other Basic as the Active Pokémon.
    deck = [
        caps[i] - opening[i] - prizes[i] - int(i == draw_index)
        for i in range(len(caps))
    ]

    if hand[0]:
        route = "direct"
    elif hand[2] and deck[0]:
        route = "treasure"
    else:
        return "no_radiant_access"

    copies = min(2, deck[1])
    return f"{route}_{copies}"


def exact(
    caps: tuple[int, ...] = COUNTS,
    opening_size: int = 7,
    prize_count: int = 6,
) -> dict[str, Fraction]:
    n = sum(caps)
    opening_ways = comb(n, opening_size) - comb(
        n - caps[0] - caps[3], opening_size
    )
    total_ways = (
        opening_ways
        * comb(n - opening_size, prize_count)
        * (n - opening_size - prize_count)
    )
    buckets: Counter[str] = Counter()
    witnessed = 0

    for opening in allocations(opening_size, caps):
        if opening[0] + opening[3] == 0:
            continue
        opening_weight = prod(comb(c, x) for c, x in zip(caps, opening))
        after_opening = tuple(c - x for c, x in zip(caps, opening))
        for prizes in allocations(prize_count, after_opening):
            prize_weight = opening_weight * prod(
                comb(c, x) for c, x in zip(after_opening, prizes)
            )
            after_prizes = tuple(
                c - x for c, x in zip(after_opening, prizes)
            )
            for draw_index, available in enumerate(after_prizes):
                if available == 0:
                    continue
                weight = prize_weight * available
                buckets[classify(opening, prizes, draw_index, caps)] += weight
                witnessed += weight

    assert witnessed == total_ways
    return {
        label: Fraction(weight, total_ways)
        for label, weight in sorted(buckets.items())
    }


def physical_oracle() -> None:
    """Independently enumerate fully labeled openings, Prizes, and draws."""
    caps = (1, 2, 1, 2, 4)
    card_classes = tuple(
        index
        for index, quantity in enumerate(caps)
        for _ in range(quantity)
    )
    counts: Counter[str] = Counter()
    accepted = 0

    for opening_slots in combinations(range(len(card_classes)), 3):
        opening_types = Counter(card_classes[i] for i in opening_slots)
        if not (opening_types[0] or opening_types[3]):
            continue
        remaining = [
            i for i in range(len(card_classes)) if i not in opening_slots
        ]
        for prize_slots in combinations(remaining, 2):
            prize_types = Counter(card_classes[i] for i in prize_slots)
            for draw_slot in remaining:
                if draw_slot in prize_slots:
                    continue
                label = classify(
                    tuple(opening_types[i] for i in range(5)),
                    tuple(prize_types[i] for i in range(5)),
                    card_classes[draw_slot],
                    caps,
                )
                counts[label] += 1
                accepted += 1

    grouped = exact(caps, opening_size=3, prize_count=2)
    assert set(grouped) == set(counts)
    for label, probability in grouped.items():
        assert probability == Fraction(counts[label], accepted)
    print(f"Exact physical oracle passed: {accepted} labeled worlds")


def main() -> None:
    """Validate the real list and regress exact rational probabilities."""
    total = sum(POKEMON.values()) + sum(TRAINERS.values()) + sum(
        ENERGY.values()
    )
    assert total == 60
    assert POKEMON["Radiant Eternatus"] == COUNTS[0]
    assert POKEMON["Shadow Rider Calyrex VMAX"] == COUNTS[1]
    assert TRAINERS["Mysterious Treasure"] == COUNTS[2]
    assert sum(POKEMON.values()) - COUNTS[0] - COUNTS[1] == COUNTS[3]
    assert total == sum(COUNTS)

    physical_oracle()
    result = exact()
    assert sum(result.values()) == 1
    assert result["direct_2"] == Fraction(2431309737, 20230837760)
    assert result["treasure_2"] == Fraction(176258415211, 556348038400)
    assert result["no_eligible_active"] == Fraction(283843, 10081280)
    for key, fraction in sorted(result.items()):
        print(f"{key}: {float(fraction):.12%} [{fraction}]")

    two_vmax = sum(
        fraction
        for label, fraction in result.items()
        if label.endswith("_2")
    )
    any_radiant = sum(
        fraction
        for label, fraction in result.items()
        if label.startswith(("direct", "treasure"))
    )
    assert two_vmax > Fraction(43, 100)
    assert any_radiant > two_vmax
    print(f"Any Radiant access: {float(any_radiant):.12%}")
    print(f"Two VMAX reachable: {float(two_vmax):.12%}")


if __name__ == "__main__":
    main()
