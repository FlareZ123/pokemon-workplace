"""Exact multiple-out access effect of spending cards before shuffle-back redraw."""
from __future__ import annotations

from fractions import Fraction
from math import comb


def hit_probability(pool_size: int, outs: int, draws: int) -> Fraction:
    """Probability at least one of \`outs\` appears in an unordered random draw."""
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in (pool_size, outs, draws)):
        raise TypeError("counts must be integers")
    if pool_size < 1 or not 0 <= outs <= pool_size or draws < 0:
        raise ValueError("invalid pool, outs, or draw count")
    draw = min(draws, pool_size)
    if draw == 0 or outs == 0:
        return Fraction(0)
    if pool_size - outs < draw:
        return Fraction(1)
    return 1 - Fraction(comb(pool_size - outs, draw), comb(pool_size, draw))


def shuffle_return_payment_delta(
    *, deck_size: int, hand_size: int, deck_outs: int, hand_outs: int,
    draws: int, payment_count: int, payment_outs: int,
) -> tuple[Fraction, Fraction, Fraction]:
    """(baseline, after payment, delta), conditional on known access classes.

    The old hand is after removing the reset source. All remaining hand cards
    would normally be returned to the deck. The pre-action instead consumes
    payment_count distinct old-hand cards, including payment_outs targets.
    The pre-action contributes no new cards to the deck, and the resulting
    shuffle restores exchangeability before a fixed-count draw.
    """
    for x in (deck_size, hand_size, deck_outs, hand_outs, draws, payment_count, payment_outs):
        if not isinstance(x, int) or isinstance(x, bool):
            raise TypeError("counts must be integers")
    if (deck_size < 1 or hand_size < 0 or draws < 0
        or not 0 <= deck_outs <= deck_size
        or not 0 <= hand_outs <= hand_size
        or not 0 <= payment_count <= hand_size
        or not 0 <= payment_outs <= hand_outs
        or payment_count - payment_outs > hand_size - hand_outs):
        raise ValueError("invalid deck/hand composition or payment")
    total = deck_size + hand_size
    outs = deck_outs + hand_outs
    before = hit_probability(total, outs, draws)
    after = hit_probability(total - payment_count, outs - payment_outs, draws)
    return before, after, after - before
