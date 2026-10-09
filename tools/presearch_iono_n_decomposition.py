"""Exact pre-redraw paid search decomposition: material thinning versus K1 choice."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from prize_informed_iono_n_choice import ChoiceResult, prize_uncertain_choice


@dataclass(frozen=True)
class PaidSearchComparison:
    baseline: ChoiceResult
    after_payment: ChoiceResult
    thinning_effect: Fraction
    information_effect_after_payment: Fraction
    net_effect: Fraction


def compare_paid_search(
    *, deck_size: int, prizes_hidden: int, unknown_outs: int,
    hand_size: int, hand_outs: int, prize_draw_count: int,
    opponent_hand_size: int, payment_count: int, payment_outs: int,
) -> PaidSearchComparison:
    """Compare no pre-action against a search before two available Supporters.

    The optional pre-action consumes payment_count old-hand cards, including
    payment_outs strategically useful targets, adds no deck/hand output, and
    inspects/shuffles the deck. Existing deck-order belief is exchangeable.
    Search connector availability, Item lock, payment DCI, Supporter presence,
    and new information beyond K are assumed as external feasibility gates.
    """
    if any(type(x) is not int for x in (payment_count,payment_outs)):
        raise TypeError("payment sizes must be integers")
    if not (0<=payment_outs<=hand_outs
            and 0<=payment_count<=hand_size
            and payment_count-payment_outs<=hand_size-hand_outs):
        raise ValueError("infeasible payment composition")
    kw=dict(deck_size=deck_size,prizes_hidden=prizes_hidden,
            unknown_outs=unknown_outs,prize_draw_count=prize_draw_count,
            opponent_hand_size=opponent_hand_size)
    original=prize_uncertain_choice(**kw,hand_size=hand_size,hand_outs=hand_outs)
    paid=prize_uncertain_choice(**kw,hand_size=hand_size-payment_count,
                                hand_outs=hand_outs-payment_outs)
    thinning=paid.before_information-original.before_information
    info=paid.information_gain
    net=paid.after_information-original.before_information
    assert thinning+info==net
    return PaidSearchComparison(original,paid,thinning,info,net)
