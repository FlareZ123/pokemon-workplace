"""Exact accepted-opening frequency for naturally held Aichi G&H spare fetching.

The deck has singleton Jirachi, G copies of Guzma & Hala, two
TM: Evolution, two Jet Energy, A Artazon, and other cards including
the remaining eligible Basics. The initial seven-card opener must
contain Jirachi, then one natural turn draw becomes visible after six
random Prize placements. Require G&H held, exactly one TM and one Jet
among eight visible cards, their spare copies searchable and at least
one Artazon searchable. This is mechanical opportunity, not payoff.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class Opportunity:
    probability: Fraction
    by_held_gnh_and_artazon: tuple[tuple[int, int, Fraction], ...]
    accepted_probability: Fraction


def exact(
    n: int = 60, opener: int = 7, prizes: int = 6,
    basics: int = 14, gnh: int = 4, artazon: int = 2,
) -> Opportunity:
    """P(named event | opener has any Basic), one subsequent natural draw."""
    filler = n - 1 - gnh - 2 - 2 - artazon
    if (n < 8 or not 1 <= opener < n or not 0 <= prizes <= n-opener-1
            or not 1 <= basics <= filler+1 or gnh < 1 or artazon < 1
            or filler < 0):
        raise ValueError("Invalid deck size, starter, or category counts")
    accepted = Fraction(
        choose(n,opener)-choose(n-basics,opener),choose(n,opener))
    if not accepted:
        raise ValueError("No valid Basic starters")

    visible_other_than_jirachi = opener
    unknown = n - 1 - visible_other_than_jirachi
    seen_denom = choose(n-1,visible_other_than_jirachi)
    prize_denom = choose(unknown,prizes)
    p_jirachi_opener = Fraction(opener,n)
    details = []
    for held_gnh in range(1,gnh+1):
        for held_artazon in range(artazon):
            other_held = visible_other_than_jirachi - held_gnh - 2 - held_artazon
            seen_ways = (
                choose(gnh,held_gnh)*choose(2,1)*choose(2,1)*
                choose(artazon,held_artazon)*choose(filler,other_held)
            )
            available_artazon = artazon-held_artazon
            other_unknown = unknown-2-available_artazon
            prize_ways = sum(
                choose(available_artazon,j) *
                choose(other_unknown,prizes-j)
                for j in range(available_artazon)
            )
            mass = (p_jirachi_opener*Fraction(seen_ways,seen_denom)*
                    Fraction(prize_ways,prize_denom)/accepted)
            details.append((held_gnh,held_artazon,mass))
    total = sum((row[2] for row in details),Fraction(0))
    return Opportunity(total,tuple(details),accepted)
