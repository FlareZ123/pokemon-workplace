"""Exact shared Fog Crystal allocation to Marshadow or Shadow Rider V.

Card access conditioned on a Basic-valid opening and opposing Path + Thorns;
this is not an estimate of game or match win rate.
"""

from __future__ import annotations

import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb, prod
from pathlib import Path

from results.tests.shadow_rider_fog_marshadow.reproduce import (
    allocations,
    capacities,
    exact_counts as fog_marshadow_exact,
    feasible as fog_marshadow_feasible,
)


# Category indices: Radiant, VMAX, Treasure, Cologne, Flutter, Stone,
# Shadow Rider V, other Basics, Marshadow, other Path answer, Energy, Fog, filler.
def feasible(opening, hand, deck, energy_only: bool,
             allow_fog_to_v: bool) -> bool:
    if not allow_fog_to_v:
        return fog_marshadow_feasible(opening, hand, deck, energy_only, True)
    if deck[1] < 2:
        return False
    benchable_marshadow = bool(opening[4] or opening[6] or opening[7])
    if not (benchable_marshadow or opening[8]):
        return False

    # Explicit allocations enforce that one Fog Crystal searches one Basic.
    for fog_for_marshadow in range(min(1, hand[11]) + 1):
        if fog_for_marshadow and not (benchable_marshadow and deck[8]):
            continue
        for fog_for_v in range(min(1, hand[11] - fog_for_marshadow) + 1):
            if fog_for_v and not (hand[5] and deck[6]):
                continue
            stone = bool(hand[5] and (hand[6] or fog_for_v))
            radiant = bool(
                hand[0] or (hand[2] and deck[0] and
                            (not energy_only or hand[10]))
            )
            path = bool(
                hand[9] or
                (benchable_marshadow and (hand[8] or fog_for_marshadow))
            )
            thorns = bool(opening[4] or hand[3])
            missing = int(not radiant) + int(not path) + int(not thorns)
            if not missing:
                return True
            if missing == 1 and stone and (
                (not radiant and deck[0])
                or (not path and (
                    deck[9] or (benchable_marshadow and deck[8])
                ))
                or (not thorns and deck[3])
            ):
                return True
    return False


@lru_cache(maxsize=None)
def prize_masks(stocks: tuple[int, ...], pool_size: int, prize_count: int):
    """Five-bit exhausted-identity distribution, exactly marginalizing Prizes.

    Bits encode Radiant, Cologne, Marshadow, Path answer, Shadow Rider V.
    VMAX surviving deck copies are separately required to be at least two.
    """
    residual = pool_size - sum(stocks)
    options = (*stocks, residual)
    counts = [0] * 32
    for assignment in allocations(prize_count, options):
        left = [q - n for q, n in zip(stocks, assignment)]
        if left[1] < 2:
            continue
        mask = sum(1 << bit for bit, index in
                   enumerate((0, 2, 3, 4, 5)) if left[index] == 0)
        ways = prod(comb(q, drawn) for q, drawn
                    in zip(options, assignment))
        counts[mask] += ways
    return tuple((mask, weight) for mask, weight in
                 enumerate(counts) if weight)


def exact_counts(quantities: tuple[int, ...], opening: int = 7,
                 prizes: int = 6) -> tuple[Fraction, Fraction]:
    size = sum(quantities)
    basics = sum(quantities[i] for i in (0, 4, 6, 7, 8))
    prize_ways = comb(size - opening - 1, prizes)
    denominator = (
        (comb(size, opening) - comb(size - basics, opening))
        * (size - opening) * prize_ways
    )
    masses = [0, 0, 0]
    for opener in allocations(opening, quantities):
        if not sum(opener[i] for i in (0, 4, 6, 7, 8)):
            continue
        opener_ways = prod(comb(q, n) for q, n in zip(quantities, opener))
        after_opener = tuple(q - n for q, n in zip(quantities, opener))
        for drawn, copies in enumerate(after_opener):
            if not copies:
                continue
            hand = tuple(opener[i] + int(i == drawn)
                         for i in range(len(quantities)))
            after = tuple(after_opener[i] - int(i == drawn)
                          for i in range(len(quantities)))
            masses[0] += opener_ways * copies * prize_ways
            stocks = tuple(after[i] for i in (0, 1, 3, 8, 9, 6))
            for mask, ways in prize_masks(
                stocks, size - opening - 1, prizes
            ):
                deck = list(after)
                for bit, index in enumerate((0, 3, 8, 9, 6)):
                    deck[index] = int(not mask & (1 << bit))
                deck[1] = 2
                weight = opener_ways * copies * ways
                masses[1] += weight * feasible(opener, hand, deck, True, False)
                masses[2] += weight * feasible(opener, hand, deck, True, True)
    assert masses[0] == denominator
    return Fraction(masses[1], denominator), Fraction(masses[2], denominator)


def physical_oracle() -> None:
    """Independent enumeration of 247,590 accepted labeled toy worlds."""
    toy = (1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1)
    cards = tuple(i for i, n in enumerate(toy) for _ in range(n))
    count = [0, 0, 0]
    for chosen in combinations(range(len(cards)), 5):
        opener = tuple(sum(cards[x] == i for x in chosen)
                       for i in range(len(toy)))
        if not sum(opener[i] for i in (0, 4, 6, 7, 8)):
            continue
        remaining = set(range(len(cards))) - set(chosen)
        for prize in remaining:
            for draw in remaining - {prize}:
                hand = tuple(opener[i] + int(cards[draw] == i)
                             for i in range(len(toy)))
                deck = tuple(sum(cards[j] == i for j in remaining
                                 if j not in (prize, draw))
                             for i in range(len(toy)))
                count[0] += 1
                count[1] += feasible(opener, hand, deck, True, False)
                count[2] += feasible(opener, hand, deck, True, True)
    assert count == [247590, 25025, 28565]
    assert exact_counts(toy, 5, 1) == (
        Fraction(count[1], count[0]), Fraction(count[2], count[0])
    )
    print("PASS: independent 247,590-world physical-card oracle")


def verify_prints() -> None:
    root = Path(__file__).resolve().parents[3]

    def card(cid):
        set_id = cid.rsplit("-", 1)[0]
        path = root / "resources" / "cards" / "en" / f"{set_id}.json"
        return next(row for row in json.loads(path.read_text(encoding="utf-8"))
                    if row["id"] == cid)

    fog = card("swsh6-140")
    shadow = card("swsh6-74")
    assert fog["name"] == "Fog Crystal"
    assert "Basic Psychic Pokémon" in fog["rules"][0]
    assert shadow["name"] == "Shadow Rider Calyrex V"
    assert shadow["types"] == ["Psychic"]
    assert shadow["subtypes"] and "Basic" in shadow["subtypes"]
    stone = card("swsh12-156")
    assert "Pokémon V" in stone["rules"][0]
    assert any(a["name"] == "Star Alchemy" for a in stone["abilities"])


def main() -> None:
    verify_prints()
    physical_oracle()
    results = {}
    for total_techs in range(5):
        for cologne in range(total_techs + 1):
            flutter = total_techs - cologne
            before, after = exact_counts(capacities(cologne, flutter))
            assert before <= after
            results[(cologne, flutter)] = after
            print(
                f"C={cologne} F={flutter} "
                f"Fog-Marshadow={float(before):.9%} "
                f"plus-Fog-V={float(after):.9%}",
                flush=True,
            )
    expected_prior = fog_marshadow_exact(capacities(1, 1))[3]
    assert exact_counts(capacities(1, 1))[0] == expected_prior
    winners = [
        max((v, pair) for pair, v in results.items() if sum(pair) == n)[1]
        for n in range(5)
    ]
    assert winners == [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]
    print("PASS: all 15 exact paid-connector allocation scenarios")


if __name__ == "__main__":
    main()
