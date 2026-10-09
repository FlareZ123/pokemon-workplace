"""Exact local comparison of Iono and N for one player's draw of useful outs.

The player-level Iono return/draw trigger depends on either player's hand.
Card text: Iono bottom-returns both hands and draws for each remaining Prize
if either returned cards. N shuffles both hands into respective decks and
draws for each remaining Prize without an empty-hand condition.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction

from hand_return_payment_frontier import hit_probability


@dataclass(frozen=True)
class IonoNComparison:
    iono_hit: Fraction
    n_hit: Fraction
    iono_minus_n: Fraction


def compare_iono_n(*, deck_size: int, hand_size: int,
                   deck_outs: int, hand_outs: int,
                   prizes_remaining: int, opponent_hand_size: int) -> IonoNComparison:
    """Conditional chance of drawing >=1 interchangeable out, per player.

    Assumes an exchangeable original deck, player has exactly deck_outs outs in
    deck and hand_outs in old hand, and no other relevant interrupts. Original
    deck ordered positions are unknown and uniform; N shuffles old hand into
    deck before drawing, while Iono appends randomized hand below old deck.
    For Iono the bottom-returned portion is included in the draw when
    prizes_remaining exceeds original deck_size; this extension is exact under
    exchangeability of original deck and returned hand order.
    """
    values = (deck_size, hand_size, deck_outs, hand_outs,
              prizes_remaining, opponent_hand_size)
    if any(type(v) is not int for v in values):
        raise TypeError("card counts must be integers")
    if (deck_size < 1 or hand_size < 0 or opponent_hand_size < 0
        or prizes_remaining < 0 or not 0 <= deck_outs <= deck_size
        or not 0 <= hand_outs <= hand_size):
        raise ValueError("infeasible state")
    n = hit_probability(deck_size + hand_size, deck_outs + hand_outs,
                        prizes_remaining)
    if hand_size + opponent_hand_size == 0:
        iono = Fraction(0)
    elif prizes_remaining <= deck_size:
        iono = hit_probability(deck_size, deck_outs, prizes_remaining)
    else:
        # Exhaust the old deck, then a random sample from old hand.
        old_target_miss = 1 - hit_probability(deck_size, deck_outs, deck_size)
        bottom_target_miss = 1 - hit_probability(
            hand_size, hand_outs, prizes_remaining - deck_size
        ) if hand_size else Fraction(1)
        iono = 1 - old_target_miss * bottom_target_miss
    return IonoNComparison(iono, n, iono - n)
