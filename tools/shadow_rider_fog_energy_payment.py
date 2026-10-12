"""Exact Fog Crystal -> Psychic Energy -> paid Treasure/Quick launch bridge.

Search Fog for deck Psychic Energy, then discard the fetched Energy to
pay a held Mysterious Treasure or Quick Ball and fetch Radiant Eternatus.
Only worlds missed by direct/Heavy/paid Item/Forest Stone/Fog-host routes
are credited. The policy allows an added pre-payment Item action.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb, prod

from tools.shadow_rider_quick_ball_frontier import COUNTS, allocate
from tools.shadow_rider_forest_stone_frontier import MODES
from tools.shadow_rider_stone_host_bridge import payable_search_source


@lru_cache(None)
def fresh_fog_energy_chance(
    held_fillers: int, prized_basics: int,
    basic_total: int = 13, filler_total: int = 25,
    v_count: int = 3, fog_count: int = 4,
) -> Fraction:
    """Held Fog minus previous Stone+Fog success when a V is available."""
    if not held_fillers:
        return Fraction()
    no_fog = (
        comb(filler_total - fog_count, held_fillers)
        if held_fillers <= filler_total - fog_count else 0
    )
    fog_held = 1 - Fraction(
        no_fog, comb(filler_total, held_fillers)
    )
    non_fog_without_stone = filler_total - 1 - fog_count
    no_fog_given_stone = Fraction(
        comb(non_fog_without_stone, held_fillers - 1)
        if held_fillers - 1 <= non_fog_without_stone else 0,
        comb(filler_total - 1, held_fillers - 1),
    )
    stone_and_fog = (
        Fraction(held_fillers, filler_total)
        * (1 - no_fog_given_stone)
    )
    all_v_prized = Fraction(
        comb(prized_basics, v_count)
        if prized_basics >= v_count else 0,
        comb(basic_total, v_count),
    )
    return fog_held - stone_and_fog * (1 - all_v_prized)


def exact_increment(
    counts: tuple[int, ...] = COUNTS,
    opening_n: int = 7, prizes_n: int = 6,
    v_count: int = 3, fog_count: int = 4,
) -> dict[str, Fraction]:
    n = sum(counts)
    accepted = comb(n, opening_n) - comb(
        n - counts[0] - counts[5], opening_n
    )
    denominator = accepted * comb(n - opening_n, prizes_n) * (
        n - opening_n - prizes_n
    )
    results = {mode: Fraction() for mode in MODES}
    for opening in allocate(opening_n, counts):
        if not opening[5]:
            continue
        open_ways = prod(comb(c, q) for c, q in zip(counts, opening))
        remaining = tuple(c - q for c, q in zip(counts, opening))
        for prizes in allocate(prizes_n, remaining):
            prize_ways = open_ways * prod(
                comb(c, q) for c, q in zip(remaining, prizes)
            )
            post_prize = tuple(
                c - q for c, q in zip(remaining, prizes)
            )
            for drawn, copies in enumerate(post_prize):
                if not copies:
                    continue
                hand = tuple(
                    opening[i] + (i == drawn)
                    for i in range(len(counts))
                )
                deck = tuple(
                    post_prize[i] - (i == drawn)
                    for i in range(len(counts))
                )
                if (
                    deck[0] != 1 or deck[1] < 2
                    or hand[6] or not deck[6]
                    or not (hand[2] or hand[4])
                ):
                    continue
                chance = fresh_fog_energy_chance(
                    hand[7], prizes[5], counts[5],
                    counts[7], v_count, fog_count,
                )
                if not chance:
                    continue
                mass = Fraction(
                    prize_ways * copies, denominator
                ) * chance
                for mode in MODES:
                    if not payable_search_source(hand, mode):
                        results[mode] += mass
    return results
