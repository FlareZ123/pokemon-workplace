"""Exact Fog Crystal -> Shadow Rider V -> Forest Seal Stone launch extension.

Radiant Eternatus is Dragon-type, so Fog Crystal cannot search it
directly. Fog Crystal can, however, fetch a Basic Psychic Shadow Rider V
to host an already held Forest Seal Stone that accesses Radiant or a
Hisuian Heavy Ball for a Prized Radiant. This adds only worlds missed by
the previously modeled paid Treasure/Quick V-host search branches.
"""
from fractions import Fraction
from functools import lru_cache
from math import comb, prod

from tools.shadow_rider_quick_ball_frontier import COUNTS, allocate
from tools.shadow_rider_forest_stone_frontier import MODES
from tools.shadow_rider_stone_host_bridge import payable_search_source


@lru_cache(None)
def chance_host_missing_stone_and_fog(
    held_basics: int, prized_basics: int, held_fillers: int,
    v_total: int = 3, basic_total: int = 13,
    filler_total: int = 25, fog_total: int = 4,
) -> Fraction:
    """Physical chance Stone and Fog are held, no V held, V remains in deck."""
    if held_fillers < 2:
        return Fraction()
    not_held = (
        comb(basic_total - held_basics, v_total)
        if basic_total - held_basics >= v_total else 0
    )
    all_prized = (
        comb(prized_basics, v_total)
        if prized_basics >= v_total else 0
    )
    v_chance = Fraction(
        not_held - all_prized, comb(basic_total, v_total)
    )
    non_fog = filler_total - 1 - fog_total
    no_fog_given_stone = Fraction(
        comb(non_fog, held_fillers - 1)
        if held_fillers - 1 <= non_fog else 0,
        comb(filler_total - 1, held_fillers - 1),
    )
    return (
        v_chance * Fraction(held_fillers, filler_total)
        * (1 - no_fog_given_stone)
    )


def exact_increment(
    counts: tuple[int, ...] = COUNTS,
    opening_n: int = 7, prizes_n: int = 6,
    v_total: int = 3, fog_total: int = 4,
) -> dict[str, Fraction]:
    """Extra Fog-hosted launch access beyond the earlier five sources."""
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
        remainder = tuple(c - q for c, q in zip(counts, opening))
        for prizes in allocate(prizes_n, remainder):
            prize_ways = open_ways * prod(
                comb(c, q) for c, q in zip(remainder, prizes)
            )
            post_prize = tuple(
                c - q for c, q in zip(remainder, prizes)
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
                if deck[1] < 2 or not (
                    deck[0] or (prizes[0] and deck[3])
                ):
                    continue
                chance = chance_host_missing_stone_and_fog(
                    hand[5], prizes[5], hand[7], v_total,
                    counts[5], counts[7], fog_total,
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
