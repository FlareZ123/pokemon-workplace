"""Exact Fog Crystal-to-Marshadow access under Path + Active Iron Thorns.

A restricted opening-access model, not a game or match win-rate estimate.
"""

from __future__ import annotations

import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb, prod
from pathlib import Path

from results.tests.shadow_rider_marshadow_path.reproduce import (
    EXPECTED_WITH_MARSHADOW_ENERGY_ONLY,
)


# Radiant, VMAX, Treasure, Cologne, Flutter, Seal Stone, Shadow Rider V,
# other Basic, Marshadow, other Path answers, Psychic Energy, Fog Crystal, filler.
def capacities(cologne: int, flutter: int) -> tuple[int, ...]:
    assert cologne >= 0 and flutter >= 0 and cologne + flutter <= 4
    stadiums = max(0, 3 - cologne - flutter)
    counts = (1, 4, 4, cologne, flutter, 1, 3, 9, 1,
              stadiums + 1, 11, 4, 21 - cologne - flutter - stadiums)
    assert sum(counts) == 60
    return counts


def allocations(amount: int, caps: tuple[int, ...]):
    if len(caps) == 1:
        if 0 <= amount <= caps[0]:
            yield (amount,)
        return
    for count in range(min(amount, caps[0]) + 1):
        for remainder in allocations(amount - count, caps[1:]):
            yield (count,) + remainder


@lru_cache(maxsize=None)
def prize_mask_ways(stocks: tuple[int, ...], prize_count: int, total: int):
    """Count exact Prize assignments by remaining search-target availability.

    The four mask bits mean all remaining copies of Radiant, Cologne,
    Marshadow, or other Path answers are Prized, respectively. VMAX count
    is tracked separately because the endpoint requires two deck VMAX.
    """
    q_r, q_v, q_c, q_m, q_p = stocks
    controlled = (q_r, q_c, q_m, q_p)

    @lru_cache(maxsize=None)
    def exhausted_ways(mask: int) -> int:
        forced = sum(q for i, q in enumerate(controlled) if mask & (1 << i))
        return sum(
            comb(q_v, v) * comb(
                total - q_v - forced, prize_count - v - forced
            )
            for v in range(min(q_v - 2, prize_count) + 1)
            if 0 <= prize_count - v - forced <= total - q_v - forced
        )

    out = []
    for exhausted in range(16):
        remaining = tuple(i for i in range(4) if not exhausted & (1 << i))
        ways = 0
        for subset in range(1 << len(remaining)):
            extra = sum(1 << remaining[i] for i in range(len(remaining))
                        if subset & (1 << i))
            term = exhausted_ways(exhausted | extra)
            ways += -term if subset.bit_count() % 2 else term
        if ways:
            out.append((exhausted, ways))
    assert sum(ways for _, ways in out) == exhausted_ways(0)
    return tuple(out)


def feasible(opening: tuple[int, ...], hand: tuple[int, ...],
             deck: tuple[int, ...], energy_only: bool,
             fog_to_marshadow: bool) -> bool:
    if deck[1] < 2:
        return False
    # An opening Marshadow must be Benched; Active Resetting Hole is invalid.
    benchable = bool(opening[4] or opening[6] or opening[7])
    if not (benchable or opening[8]):
        return False
    stone = bool(hand[5] and hand[6])
    radiant = bool(hand[0] or
                   (hand[2] and deck[0] and
                    (not energy_only or hand[10])))
    marshadow = bool(hand[8] or
                     (fog_to_marshadow and hand[11] and deck[8]))
    path = bool(hand[9] or (benchable and marshadow))
    thorns = bool(opening[4] or hand[3])
    missing = int(not radiant) + int(not path) + int(not thorns)
    if missing == 0:
        return True
    if missing != 1 or not stone:
        return False
    return bool(
        (not radiant and deck[0]) or
        (not path and (deck[9] or (benchable and deck[8]))) or
        (not thorns and deck[3])
    )


def exact_counts(quantities: tuple[int, ...], opening: int = 7,
                 prizes: int = 6) -> tuple[Fraction, ...]:
    total_cards = sum(quantities)
    basics = sum(quantities[i] for i in (0, 4, 6, 7, 8))
    prize_ways = comb(total_cards - opening - 1, prizes)
    denominator = (
        (comb(total_cards, opening) - comb(total_cards - basics, opening))
        * (total_cards - opening) * prize_ways
    )
    mass = [0, 0, 0, 0, 0]
    for opener in allocations(opening, quantities):
        if not sum(opener[i] for i in (0, 4, 6, 7, 8)):
            continue
        opener_ways = prod(comb(q, n) for q, n in zip(quantities, opener))
        after_opening = tuple(q - n for q, n in zip(quantities, opener))
        for drawn, copies in enumerate(after_opening):
            if not copies:
                continue
            hand = tuple(opener[i] + int(i == drawn)
                         for i in range(len(opener)))
            after_draw = tuple(after_opening[i] - int(i == drawn)
                               for i in range(len(opener)))
            mass[0] += opener_ways * copies * prize_ways
            stocks = tuple(after_draw[i] for i in (0, 1, 3, 8, 9))
            for exhausted, ways in prize_mask_ways(
                stocks, prizes, total_cards - opening - 1
            ):
                deck = list(after_draw)
                for index, bit in ((0, 0), (3, 1), (8, 2), (9, 3)):
                    deck[index] = int(not (exhausted & (1 << bit)))
                deck[1] = 2
                weight = opener_ways * copies * ways
                for (energy_only, fog), k in (
                    ((False, False), 1), ((True, False), 2),
                    ((False, True), 3), ((True, True), 4)
                ):
                    if feasible(opener, hand, tuple(deck), energy_only, fog):
                        mass[k] += weight
    assert mass[0] == denominator
    return tuple(Fraction(value, denominator) for value in mass[1:])


def physical_oracle() -> None:
    """Independently enumerate labeled 5-card openings, 1 Prize, 1 draw."""
    toy = (1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
    physical = tuple(i for i, number in enumerate(toy) for _ in range(number))
    counts = [0, 0, 0, 0, 0]
    for opener in combinations(range(len(physical)), 5):
        opening = tuple(sum(physical[x] == i for x in opener)
                        for i in range(len(toy)))
        if not sum(opening[i] for i in (0, 4, 6, 7, 8)):
            continue
        remaining = set(range(len(physical))) - set(opener)
        for prize in remaining:
            for drawn in remaining - {prize}:
                hand = tuple(opening[i] + int(physical[drawn] == i)
                             for i in range(len(toy)))
                deck = tuple(sum(physical[j] == i for j in remaining
                                 if j not in (prize, drawn))
                             for i in range(len(toy)))
                counts[0] += 1
                for (energy_only, fog), k in (
                    ((False, False), 1), ((True, False), 2),
                    ((False, True), 3), ((True, True), 4)
                ):
                    counts[k] += feasible(opening, hand, deck, energy_only, fog)
    assert counts == [135072, 13817, 11513, 15802, 13382]
    assert exact_counts(toy, opening=5, prizes=1) == tuple(
        Fraction(value, counts[0]) for value in counts[1:]
    )
    print("PASS: independent 135,072-world physical-card oracle")


def verify_sources() -> None:
    root = Path(__file__).resolve().parents[3]

    def card(identifier: str):
        set_id = identifier.rsplit("-", 1)[0]
        records = json.loads(
            (root / "resources" / "cards" / "en" / f"{set_id}.json")
            .read_text(encoding="utf-8")
        )
        return next(row for row in records if row["id"] == identifier)

    fog = card("swsh6-140")
    marshadow = card("sm10-81")
    assert fog["name"] == "Fog Crystal"
    assert any("Basic Psychic Pokémon" in rule for rule in fog["rules"])
    assert marshadow["types"] == ["Psychic"]
    assert any("on your Bench" in ability["text"] and
               "discard any Stadium" in ability["text"]
               for ability in marshadow["abilities"])
    assert card("swsh6-148")["name"] == "Path to the Peak"
    assert card("sv6-77")["name"] == "Iron Thorns ex"


def main() -> None:
    verify_sources()
    physical_oracle()
    strict = {}
    for total in range(5):
        for cologne in range(total + 1):
            flutter = total - cologne
            old_unrestricted, old_energy, new_unrestricted, new_energy = (
                exact_counts(capacities(cologne, flutter))
            )
            pair = (cologne, flutter)
            assert old_energy == EXPECTED_WITH_MARSHADOW_ENERGY_ONLY[pair]
            assert old_energy <= new_energy <= new_unrestricted
            assert old_unrestricted <= new_unrestricted
            strict[pair] = new_energy
            print(
                f"C={cologne} F={flutter} "
                f"baseline={float(old_energy):.9%} "
                f"Fog-Marshadow={float(new_energy):.9%} "
                f"gain_pp={100 * float(new_energy - old_energy):.9f}",
                flush=True,
            )
    winners = [
        max((rate, pair) for pair, rate in strict.items() if sum(pair) == n)[1]
        for n in range(5)
    ]
    assert winners == [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]
    print("PASS: all 15 full-60-card exact scenarios and baseline fractions")


if __name__ == "__main__":
    main()
