"""Exact Forest Seal Stone fallback on the published Aichi Shadow Rider list.

The base grouped counts are unchanged from shadow_rider_quick_ball_frontier.
Of the 13 other Basics, exactly three are Shadow Rider Calyrex V; of
the 25 other cards, exactly one is Forest Seal Stone. Conditional physical
symmetry integrates those identities without a much larger category DP.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from math import comb, prod

from tools.shadow_rider_quick_ball_frontier import COUNTS, allocate

MODES = ("unrestricted", "energy", "energy_or_extra_search")
FAILURES = ("fail", "no_alternate_basic", "vm_depleted")


@lru_cache(None)
def stone_v_chance(
    held_other_basic: int, held_other_filler: int,
    v_copies: int = 3, basic_total: int = 13, filler_total: int = 25,
) -> Fraction:
    """P(Stone held AND at least one V held | grouped first-eight hand)."""
    if not held_other_basic or not held_other_filler:
        return Fraction()
    without_v = (
        comb(basic_total - v_copies, held_other_basic)
        if held_other_basic <= basic_total - v_copies else 0
    )
    return (
        Fraction(held_other_filler, filler_total)
        * (1 - Fraction(without_v, comb(basic_total, held_other_basic)))
    )


def route(
    opening: tuple[int, ...], prizes: tuple[int, ...], drawn: int,
    caps: tuple[int, ...], mode: str, v_copies: int = 3,
) -> tuple[str, Fraction]:
    """Find a source route, plus conditional Stone-and-V rescue chance."""
    hand = tuple(opening[i] + (i == drawn) for i in range(len(caps)))
    deck = tuple(
        caps[i] - opening[i] - prizes[i] - (i == drawn)
        for i in range(len(caps))
    )
    if not opening[5]:
        return "no_alternate_basic", Fraction()
    if deck[1] < 2:
        return "vm_depleted", Fraction()
    if hand[0]:
        return "direct", Fraction()
    if prizes[0] and hand[3]:
        return "heavy", Fraction()

    if deck[0]:
        if mode == "unrestricted":
            pay_t, pay_q = bool(hand[2]), bool(hand[4])
        elif mode == "energy":
            pay_t = bool(hand[2] and hand[6])
            pay_q = bool(hand[4] and hand[6])
        elif mode == "energy_or_extra_search":
            pay_t = bool(hand[2] and (
                hand[6] or hand[2] > 1 or hand[4]
            ))
            pay_q = bool(hand[4] and (hand[6] or hand[2]))
        else:
            raise ValueError(mode)
        if pay_t:
            return "treasure", Fraction()
        if pay_q:
            return "quick", Fraction()

    if deck[0] or (prizes[0] and deck[3]):
        chance = stone_v_chance(
            hand[5], hand[7], v_copies, caps[5], caps[7]
        )
        if chance:
            label = "stone_radiant" if deck[0] else "stone_heavy"
            return label, chance
    return "fail", Fraction()


def exact_stone(
    caps: tuple[int, ...] = COUNTS,
    opening_n: int = 7, prizes_n: int = 6, v_copies: int = 3,
) -> dict[str, dict[str, Fraction]]:
    """Return exact disjoint route distributions under each payment policy."""
    n = sum(caps)
    accepted = comb(n, opening_n) - comb(
        n - caps[0] - caps[5], opening_n
    )
    denominator = accepted * comb(n - opening_n, prizes_n) * (
        n - opening_n - prizes_n
    )
    tallies: dict[str, dict[str, Fraction]] = {
        mode: defaultdict(Fraction) for mode in MODES
    }
    for opening in allocate(opening_n, caps):
        if not opening[0] and not opening[5]:
            continue
        ways_open = prod(comb(c, q) for c, q in zip(caps, opening))
        remainder = tuple(c - q for c, q in zip(caps, opening))
        for prizes in allocate(prizes_n, remainder):
            ways = ways_open * prod(
                comb(c, q) for c, q in zip(remainder, prizes)
            )
            post_prize = tuple(
                c - q for c, q in zip(remainder, prizes)
            )
            for drawn, available in enumerate(post_prize):
                if not available:
                    continue
                mass = Fraction(ways * available, denominator)
                for mode, tally in tallies.items():
                    label, chance = route(
                        opening, prizes, drawn, caps, mode, v_copies
                    )
                    if label.startswith("stone_"):
                        tally[label] += mass * chance
                        tally["fail"] += mass * (1 - chance)
                    else:
                        tally[label] += mass
    for mode, tally in tallies.items():
        assert sum(tally.values()) == 1, mode
    return tallies


def success(tally: dict[str, Fraction]) -> Fraction:
    return sum(
        (probability for label, probability in tally.items()
         if label not in FAILURES), Fraction()
    )
