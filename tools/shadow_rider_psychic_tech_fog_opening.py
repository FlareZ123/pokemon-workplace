"""Exact static first-seven access to a singleton Basic Psychic tech via Fog Crystal."""
from __future__ import annotations

from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def psychic_tech_access(
    *, deck_size: int, basic_count: int, fog_crystal_count: int,
    opening_hand: int, prize_count: int
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    """Return (valid opening, direct hand, Fog search, combined given valid).

    One distinguished Basic Psychic tech is included in basic_count.
    The direct hand and Fog-only branches are mutually exclusive. The Fog
    route requires another Basic in the accepted opener, Fog Crystal in hand,
    and the tech outside initial six Prizes. It does not account for competing
    Fog Crystal uses, Active promotion, card effect locks, or match timing.
    """
    n, b, f, h, p = (
        deck_size, basic_count, fog_crystal_count,
        opening_hand, prize_count,
    )
    if (
        n < 1 or not 1 <= b <= n or not 0 <= f <= n - b
        or not 1 <= h < n - p or not 0 <= p < n - h
    ):
        raise ValueError("invalid physical card allocation parameters")
    denominator = comb(n, h)
    valid = Fraction(denominator - choose(n - b, h), denominator)
    direct = Fraction(h, n)
    fog = Fraction(0)
    target_still_in_deck = Fraction(n - h - p, n - h)

    for other_basics in range(1, min(b - 1, h) + 1):
        for fogs in range(1, min(f, h - other_basics) + 1):
            count = (
                choose(b - 1, other_basics)
                * choose(f, fogs)
                * choose(n - b - f, h - other_basics - fogs)
            )
            fog += (
                Fraction(count, denominator) * target_still_in_deck
            )
    return valid, direct, fog, (direct + fog) / valid
