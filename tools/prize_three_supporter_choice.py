"""Iono, N, and Professor's Research: exact K0/K1 action-envelope comparison.

All three legal printed effects use a single Supporter slot. Assumes the
specific Supporters are simultaneously available for the next decision, the
player can play one, and no effects prohibit them. Deck order is exchangeable.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from hand_return_payment_frontier import hit_probability
from multi_action_information_envelope import ActionEnvelope, action_information_envelope
from prize_informed_iono_n_choice import prize_uncertain_choice


@dataclass(frozen=True)
class ThreeSupporterResult:
    envelope: ActionEnvelope
    rows: tuple[tuple[int, Fraction, Fraction, Fraction, Fraction], ...]


def three_supporter_choice(
    *, deck_size: int, prizes_hidden: int, unknown_outs: int,
    hand_size: int, hand_outs: int, prize_draw_count: int,
    opponent_hand_size: int,
) -> ThreeSupporterResult:
    """Success = >=1 interchangeable target in the newly drawn hand.

    N shuffles hand into deck and draws prizes_remaining.
    Iono bottoms hand and draws prizes_remaining if either hand was returned.
    Professor's Research discards hand and draws seven from the old deck.
    Hidden K is the only unknown; hand outs R remain known.

    Source-action acquisition, loss of pre-existing resources, future attacks,
    alternate objectives, and post-draw game value are deliberately excluded.
    """
    if hand_size + opponent_hand_size == 0:
        raise ValueError("Iono cannot change an empty-hand / empty-hand state")
    if not 1 <= prize_draw_count <= 6:
        raise ValueError("model an ongoing six-Prize game with 1..6 Prizes")
    binary = prize_uncertain_choice(
        deck_size=deck_size, prizes_hidden=prizes_hidden,
        unknown_outs=unknown_outs, hand_size=hand_size,
        hand_outs=hand_outs, prize_draw_count=prize_draw_count,
        opponent_hand_size=opponent_hand_size,
    )
    rows = tuple((row.deck_outs, row.prior_probability, row.iono_success,
                  row.n_success, hit_probability(deck_size, row.deck_outs, 7))
                 for row in binary.rows)
    envelope = action_information_envelope((p, {
        "Iono": iono, "N": n, "Professor's Research": research,
    }) for _, p, iono, n, research in rows)
    return ThreeSupporterResult(envelope, rows)


def paid_search_three_supporter_choice(
    *, payment_count: int, payment_outs: int, **kwargs: int,
) -> tuple[ThreeSupporterResult, ThreeSupporterResult, Fraction, Fraction, Fraction]:
    """An exogenous legal search pays before K is revealed; do not use K to pay.

    Return (baseline, postpayment, material, information, total) with exact
    material + information = total accounting. Feasibility is externally
    conditioned; search output is zero and its deck shuffle is neutral.
    """
    if type(payment_count) is not int or type(payment_outs) is not int:
        raise TypeError("payment counts must be integers")
    h, r = kwargs["hand_size"], kwargs["hand_outs"]
    if not (0 <= payment_outs <= r and 0 <= payment_count <= h
            and payment_count - payment_outs <= h-r):
        raise ValueError("invalid payment composition")
    before = three_supporter_choice(**kwargs)
    paid = dict(kwargs)
    paid["hand_size"] = h - payment_count
    paid["hand_outs"] = r - payment_outs
    after = three_supporter_choice(**paid)
    material = after.envelope.best_fixed_value - before.envelope.best_fixed_value
    information = after.envelope.information_value
    total = after.envelope.observed_value - before.envelope.best_fixed_value
    assert material + information == total
    return before, after, material, information, total
