"""Exact Basic-valid opening and six-Prize access for one non-Basic gust source."""
from fractions import Fraction
from math import comb
from tools.stochastic_opponent_gust_arrival import win_probability


def opening_access(total=60, basics=12, hand_size=7, prize_count=6):
    """Return accepted-hand rate and source probabilities in hand, Prizes, deck.

    There is one non-Basic gust source, ``basics`` Basic Pokemon and
    filler cards. The opening hand is conditioned to contain a Basic.
    """
    if not (1 <= basics < total and 0 < hand_size < total-prize_count):
        raise ValueError("invalid opening composition")
    valid = 1 - Fraction(comb(total-basics, hand_size), comb(total, hand_size))
    if not valid:
        raise ValueError("no Basic-valid opening possible")
    hand = (Fraction(hand_size,total) *
            (1-Fraction(comb(total-1-basics,hand_size-1),
                        comb(total-1,hand_size-1))) / valid)
    prize = (1-hand)*Fraction(prize_count,total-hand_size)
    deck = (1-hand)-prize
    return valid,hand,prize,deck


def chance_accessible_by_reply(basics, replies, total=60, hand_size=7, prize_count=6):
    """P(source initially in hand or drawn by one-per-reply draw k)."""
    _,hand,_,_=opening_access(total,basics,hand_size,prize_count)
    available_draws=min(replies,total-hand_size-prize_count)
    return hand+(1-hand)*Fraction(available_draws,total-hand_size)


def opening_mixture_win_probability(own_active,own_bench,enemy_active,enemy_bench,
                                    own_bosses,own_catchers,enemy_prizes,
                                    source,basics,total=60,hand_size=7,prize_count=6):
    """Win chance after public revelation of initial source zone and each draw."""
    _,h,p,d=opening_access(total,basics,hand_size,prize_count)
    args=(own_active,own_bench,enemy_active,enemy_bench,
          own_bosses,own_catchers,6,enemy_prizes)
    deck_size=total-hand_size-prize_count
    return (h*win_probability(*args,source,deck_size,'held') +
            p*win_probability(*args,'none',deck_size) +
            d*win_probability(*args,source,deck_size,'unseen'))
