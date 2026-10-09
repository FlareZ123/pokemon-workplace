"""Exact raw-draw probability of a turn-two Beheeyem lock handoff.

A 60-card deck is uniformly shuffled. The opening seven cards form a hand;
six random Prize cards are then set aside. Without searches or further draw
effects, the two turn draws are an ordered uniform pair from the remaining
53 cards after the hand. No model of opponent actions is included.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb
import json


@dataclass(frozen=True)
class Scenario:
    label: str
    counts: tuple[int, ...]
    # Categories are Elgyem, replacement Basic, Beheeyem,
    # replacement Evolution, Triple Acceleration Energy, [Rare Candy].


def exact_handoff_probability(scenario: Scenario) -> tuple[Fraction, int]:
    """Require opening Elgyem, turn-one replacement Basic, all cards by turn two."""
    copies = scenario.counts
    if len(copies) not in (5, 6) or any(c < 1 or c > 4 for c in copies):
        raise ValueError("Expect five or six separate 1-4-copy engine components")
    if sum(copies) > 60:
        raise ValueError("Engine occupies more than 60 deck slots")
    capacities = copies + (60 - sum(copies),)
    space = comb(60, 7) * 53 * 52
    favorable = 0
    checked = 0

    for present in product(*(range(min(n, 7) + 1) for n in copies)):
        other = 7 - sum(present)
        if not 0 <= other <= capacities[-1]:
            continue
        opening = present + (other,)
        hands = comb(capacities[-1], other)
        for size, amount in zip(copies, present):
            hands *= comb(size, amount)
        remaining = tuple(size - amount for size, amount in zip(capacities, opening))

        for first, count_first in enumerate(remaining):
            if count_first == 0:
                continue
            for second, count_second in enumerate(remaining):
                ordered = count_first * (count_second - (first == second))
                if ordered == 0:
                    continue
                ways = hands * ordered
                checked += ways
                if opening[0] == 0:
                    continue
                if opening[1] + (first == 1) == 0:
                    continue
                if any(
                    opening[index] + (first == index) + (second == index) == 0
                    for index in range(len(copies))
                ):
                    continue
                favorable += ways

    assert checked == space, "Ordered sample space must conserve all deals"
    return Fraction(favorable, space), checked


def main() -> None:
    scenarios = (
        Scenario("Honchkrow-GX, 3 evolution copies", (4, 4, 4, 3, 4)),
        Scenario("Honchkrow-GX / Galarian Weezing, 4 evolution copies", (4, 4, 4, 4, 4)),
        Scenario("Stoutland + Rare Candy, 2 Stoutland copies", (4, 4, 4, 2, 4, 4)),
        Scenario("Stoutland + Rare Candy, 4 Stoutland copies", (4, 4, 4, 4, 4, 4)),
    )
    results = {}
    for scenario in scenarios:
        fraction, space = exact_handoff_probability(scenario)
        results[scenario.label] = {
            "copies": scenario.counts,
            "probability_percent": round(float(fraction) * 100, 6),
            "sample_space_verified": space == comb(60, 7) * 53 * 52,
        }
    assert results[scenarios[1].label]["probability_percent"] > results[scenarios[3].label]["probability_percent"]
    assert results[scenarios[3].label]["probability_percent"] > results[scenarios[2].label]["probability_percent"]
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
