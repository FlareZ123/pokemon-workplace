"""Exact static opening allocation for one Alolan Muk and Dream Balls."""
from fractions import Fraction
from math import comb


def c(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def opening_allocation(
    *, deck_size: int, basic_count: int, dream_ball_count: int,
    opening_hand: int, prize_count: int, prizes_awarded: int
) -> tuple[Fraction, Fraction, Fraction]:
    """Return valid-hand probability, joint event, and event given valid hand.

    A static random seven-card opening is Basic-valid; one Muk remains in
    the deck; a Dream Ball occurs among k uniformly chosen first Prizes.
    This does not model actual gameplay, card search, or Prize decisions.
    """
    n, b, d, h, p, k = (
        deck_size, basic_count, dream_ball_count,
        opening_hand, prize_count, prizes_awarded,
    )
    if (
        n < 1 or not 0 < b <= n or not 0 <= d <= n - b - 1
        or not 1 <= h < n - p or not 0 <= p < n - h
        or not 0 <= k <= p
    ):
        raise ValueError("invalid card-count or opening parameters")
    denominator = comb(n, h)
    valid = Fraction(denominator - c(n - b, h), denominator)
    total = Fraction(0)
    others = n - b - d - 1
    muk_deck_probability = Fraction(n - h - p, n - h)
    for hb in range(1, min(b, h) + 1):
        for hd in range(min(d, h - hb) + 1):
            ways = c(b, hb) * c(d, hd) * c(others, h - hb - hd)
            if not ways:
                continue
            prize_pool = n - h - 1
            hit = 1 - Fraction(c(prize_pool - d + hd, k), c(prize_pool, k))
            total += Fraction(ways, denominator) * muk_deck_probability * hit
    return valid, total, total / valid
