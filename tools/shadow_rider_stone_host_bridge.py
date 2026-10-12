"""Exact search-Item -> V host -> Forest Seal Stone -> Heavy Ball prize rescue.

R is Prized, Heavy Ball remains in deck, and V is not initially held.
One payable Mysterious Treasure or Quick Ball can search Shadow Rider V;
Forest Seal Stone can then fetch Heavy Ball to retrieve Radiant Eternatus.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from math import comb, prod

from tools.shadow_rider_quick_ball_frontier import COUNTS, allocate
from tools.shadow_rider_forest_stone_frontier import MODES


@lru_cache(None)
def missing_host_rescue_probability(
    held_basics: int, prized_basics: int, held_fillers: int,
    v_copies: int = 3, basic_total: int = 13, filler_total: int = 25,
) -> Fraction:
    """Stone held AND no V held AND at least one V remains in deck."""
    if held_fillers == 0:
        return Fraction()
    denominator = comb(basic_total, v_copies)
    not_in_hand = (
        comb(basic_total - held_basics, v_copies)
        if basic_total - held_basics >= v_copies else 0
    )
    all_prized = (
        comb(prized_basics, v_copies) if prized_basics >= v_copies else 0
    )
    return (
        Fraction(held_fillers, filler_total)
        * Fraction(not_in_hand - all_prized, denominator)
    )


def payable_search_source(
    hand: tuple[int, ...], mode: str,
) -> str | None:
    """Conservatively choose the first paid Psychic/Basic V tutor."""
    if mode == "unrestricted":
        return "treasure" if hand[2] else "quick" if hand[4] else None
    if mode == "energy":
        if hand[2] and hand[6]:
            return "treasure"
        return "quick" if hand[4] and hand[6] else None
    if mode == "energy_or_extra_search":
        if hand[2] and (hand[6] or hand[2] > 1 or hand[4]):
            return "treasure"
        if hand[4] and (hand[6] or hand[2]):
            return "quick"
        return None
    raise ValueError(mode)


def exact_extension(
    counts: tuple[int, ...] = COUNTS,
    opening_n: int = 7, prizes_n: int = 6, v_copies: int = 3,
) -> dict[str, dict[str, Fraction]]:
    """Disjoint extra bridge probability beyond naturally held V hosts."""
    n = sum(counts)
    accepted = comb(n, opening_n) - comb(
        n - counts[0] - counts[5], opening_n
    )
    denominator = accepted * comb(n - opening_n, prizes_n) * (
        n - opening_n - prizes_n
    )
    events: dict[str, dict[str, Fraction]] = {
        mode: defaultdict(Fraction) for mode in MODES
    }
    for opening in allocate(opening_n, counts):
        if not opening[5]:
            continue
        opening_ways = prod(
            comb(c, q) for c, q in zip(counts, opening)
        )
        remainder = tuple(c - q for c, q in zip(counts, opening))
        for prizes in allocate(prizes_n, remainder):
            if prizes[0] != 1:
                continue
            ways = opening_ways * prod(
                comb(c, q) for c, q in zip(remainder, prizes)
            )
            post_prize = tuple(
                c - q for c, q in zip(remainder, prizes)
            )
            for drawn, available in enumerate(post_prize):
                if not available:
                    continue
                hand = tuple(
                    opening[i] + (drawn == i)
                    for i in range(len(counts))
                )
                deck = tuple(
                    post_prize[i] - (drawn == i)
                    for i in range(len(counts))
                )
                if deck[1] < 2 or deck[3] != 1:
                    continue
                chance = missing_host_rescue_probability(
                    hand[5], prizes[5], hand[7],
                    v_copies, counts[5], counts[7]
                )
                if not chance:
                    continue
                mass = Fraction(ways * available, denominator) * chance
                for mode, tally in events.items():
                    source = payable_search_source(hand, mode)
                    if source:
                        tally[source] += mass
    return events
