"""Exact Prize-uncertainty value of observing deck outs before choosing Iono/N."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

from iono_n_access_comparison import compare_iono_n


@dataclass(frozen=True)
class ChoiceRow:
    deck_outs: int
    prior_probability: Fraction
    iono_success: Fraction
    n_success: Fraction
    optimal_choice: str


@dataclass(frozen=True)
class ChoiceResult:
    before_information: Fraction
    after_information: Fraction
    information_gain: Fraction
    fixed_iono: Fraction
    fixed_n: Fraction
    rows: tuple[ChoiceRow, ...]


def prize_uncertain_choice(
    *, deck_size: int, prizes_hidden: int, unknown_outs: int,
    hand_size: int, hand_outs: int, prize_draw_count: int,
    opponent_hand_size: int,
) -> ChoiceResult:
    """Model K0 versus perfect deck-composition observation K1.

    Unknown pool of deck+Prize cards contains unknown_outs useful cards.
    Conditional on knowing only total unknown_outs, initial deck outs follow
    hypergeometric placement. Hand composition and Prize count are known.
    K1 exposes exact deck-outs count, at no modeled search/payment cost.
    """
    fields=(deck_size,prizes_hidden,unknown_outs,hand_size,hand_outs,
            prize_draw_count,opponent_hand_size)
    if any(type(x) is not int for x in fields):
        raise TypeError("counts must be integers")
    if (deck_size<1 or prizes_hidden<0 or hand_size<0 or prize_draw_count<0
        or opponent_hand_size<0 or not 0<=unknown_outs<=deck_size+prizes_hidden
        or not 0<=hand_outs<=hand_size):
        raise ValueError("invalid unknown-zone composition")
    denominator=comb(deck_size+prizes_hidden,unknown_outs)
    rows=[]
    for k in range(max(0,unknown_outs-prizes_hidden),min(deck_size,unknown_outs)+1):
        prior=Fraction(comb(deck_size,k)*comb(prizes_hidden,unknown_outs-k),denominator)
        outcomes=compare_iono_n(
            deck_size=deck_size,hand_size=hand_size,deck_outs=k,
            hand_outs=hand_outs,prizes_remaining=prize_draw_count,
            opponent_hand_size=opponent_hand_size)
        rows.append(ChoiceRow(k,prior,outcomes.iono_hit,outcomes.n_hit,
                              "Iono" if outcomes.iono_hit>=outcomes.n_hit else "N"))
    assert sum((r.prior_probability for r in rows),Fraction(0))==1
    fixed_iono=sum((r.prior_probability*r.iono_success for r in rows),Fraction(0))
    fixed_n=sum((r.prior_probability*r.n_success for r in rows),Fraction(0))
    after=sum((r.prior_probability*max(r.iono_success,r.n_success) for r in rows),Fraction(0))
    before=max(fixed_iono,fixed_n)
    assert after>=before
    return ChoiceResult(before,after,after-before,fixed_iono,fixed_n,tuple(rows))
