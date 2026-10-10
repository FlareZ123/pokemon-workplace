"""Exact deck-search access conditioned on at least one target Basic in hand.

This generalizes the earlier designated-Basic opening-hand model. With r
eligible Basic copies in a 60-card deck, condition on the initial seven
containing at least one of them, then set six random Prize cards.
Stage 1 and Stage 2 are disjoint named card families with copy counts a,b.
"""

from __future__ import annotations

from fractions import Fraction
from math import comb


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def check_counts(
    basics: int,
    stage1: int,
    stage2: int,
    *,
    cards: int,
    hand: int,
    prizes: int,
) -> None:
    if basics < 1 or min(stage1, stage2) < 0:
        raise ValueError("at least one target Basic and nonnegative stages required")
    if cards <= 0 or hand <= 0 or prizes < 0 or hand + prizes > cards:
        raise ValueError("invalid deck, hand, or Prize counts")
    if basics + stage1 + stage2 > cards:
        raise ValueError("category counts exceed deck size")


def probability_no_stage_deck_given_target_basic_hand(
    *,
    basics: int,
    stage_copies: int,
    cards: int = 60,
    hand: int = 7,
    prizes: int = 6,
) -> Fraction:
    """P(no copies of one stage in deck | opening hand has target Basic).

    Subtract the worlds whose hand has no target Basic from the
    unconditional probability that all copies lie in hand or Prizes.
    The subtraction is computed using a conditional hypergeometric
    distribution over Stage copies in hands containing no target Basic.
    """

    check_counts(basics, stage_copies, 0, cards=cards, hand=hand, prizes=prizes)
    inaccessible = hand + prizes
    unrestricted = Fraction(
        choose(inaccessible, stage_copies),
        choose(cards, stage_copies),
    )

    no_basic_hand = Fraction(
        choose(cards - basics, hand),
        choose(cards, hand),
    )
    if not no_basic_hand:
        return unrestricted

    no_stage_deck_given_no_basic = Fraction(0)
    for stage_in_hand in range(
        max(0, stage_copies - prizes),
        min(stage_copies, hand) + 1,
    ):
        hand_weight = Fraction(
            choose(stage_copies, stage_in_hand)
            * choose(cards - basics - stage_copies, hand - stage_in_hand),
            choose(cards - basics, hand),
        )
        prize_weight = Fraction(
            choose(prizes, stage_copies - stage_in_hand),
            choose(cards - hand, stage_copies - stage_in_hand),
        )
        no_stage_deck_given_no_basic += hand_weight * prize_weight

    return (
        unrestricted - no_basic_hand * no_stage_deck_given_no_basic
    ) / (1 - no_basic_hand)


def conditional_full_chain(
    *,
    basics: int,
    stage1: int,
    stage2: int,
    cards: int = 60,
    hand: int = 7,
    prizes: int = 6,
) -> Fraction:
    """Inclusion-exclusion conditional on >=1 target Basic in initial hand."""

    check_counts(basics, stage1, stage2, cards=cards, hand=hand, prizes=prizes)
    q1 = probability_no_stage_deck_given_target_basic_hand(
        basics=basics, stage_copies=stage1,
        cards=cards, hand=hand, prizes=prizes,
    )
    q2 = probability_no_stage_deck_given_target_basic_hand(
        basics=basics, stage_copies=stage2,
        cards=cards, hand=hand, prizes=prizes,
    )
    q12 = probability_no_stage_deck_given_target_basic_hand(
        basics=basics, stage_copies=stage1 + stage2,
        cards=cards, hand=hand, prizes=prizes,
    )
    return Fraction(1) - q1 - q2 + q12


def enumerate_conditional_full_chain(
    *,
    basics: int,
    stage1: int,
    stage2: int,
    cards: int = 60,
    hand: int = 7,
    prizes: int = 6,
) -> Fraction:
    """Independent four-category hand and Prize allocations."""

    check_counts(basics, stage1, stage2, cards=cards, hand=hand, prizes=prizes)
    filler = cards - basics - stage1 - stage2
    favourable = conditioned_total = 0

    for hb in range(1, min(basics, hand) + 1):
        for h1 in range(min(stage1, hand - hb) + 1):
            for h2 in range(min(stage2, hand - hb - h1) + 1):
                hf = hand - hb - h1 - h2
                if hf > filler:
                    continue
                hways = (
                    choose(basics, hb) * choose(stage1, h1)
                    * choose(stage2, h2) * choose(filler, hf)
                )
                left_b, left_1, left_2, left_f = (
                    basics - hb, stage1 - h1,
                    stage2 - h2, filler - hf,
                )
                conditioned_total += hways * choose(cards - hand, prizes)

                for pb in range(min(left_b, prizes) + 1):
                    for p1 in range(min(left_1, prizes - pb) + 1):
                        for p2 in range(min(left_2, prizes - pb - p1) + 1):
                            pf = prizes - pb - p1 - p2
                            d1, d2 = left_1 - p1, left_2 - p2
                            if d1 > 0 and d2 > 0:
                                favourable += hways * (
                                    choose(left_b, pb)
                                    * choose(left_1, p1)
                                    * choose(left_2, p2)
                                    * choose(left_f, pf)
                                )

    if conditioned_total == 0:
        raise ValueError("target Basic hand event must have positive probability")
    return Fraction(favourable, conditioned_total)
