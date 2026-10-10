"""Grand Tree deck-only accessibility after ordinary unselective draws.

Condition on one designated target Basic already occupying one opening hand
slot. Remaining 59 cards include 6 other opening hand cards, 6 Prizes, and
47 initially searchable deck cards. Each blind draw transfers a uniformly
random deck card from the searchable deck into inaccessible hand for the
specific Grand Tree deck-search action.
"""

from __future__ import annotations

from fractions import Fraction
from math import comb

from tools.grand_tree_initial_zone_probability import probability_full


def probability_stage_remaining(
    copies: int,
    blind_draws: int,
    *,
    n: int = 59,
    other_hand: int = 6,
    prizes: int = 6,
) -> Fraction:
    """Probability at least one copy remains searchable in the deck."""

    if copies < 0 or copies > n or blind_draws < 0:
        raise ValueError("invalid copy or draw counts")
    if other_hand + prizes + blind_draws > n:
        raise ValueError("blind draws exceed initially searchable deck cards")
    inaccessible = other_hand + prizes + blind_draws
    none = (
        Fraction(comb(inaccessible, copies), comb(n, copies))
        if copies <= inaccessible
        else Fraction(0)
    )
    return 1 - none


def probability_joint_after_draws(
    stage1: int,
    stage2: int,
    blind_draws: int,
    *,
    n: int = 59,
    other_hand: int = 6,
    prizes: int = 6,
) -> Fraction:
    """Both stage families have >=1 copy left in deck after blind draws."""

    if stage1 + stage2 > n or min(stage1, stage2) < 0:
        raise ValueError("stage copy counts outside remaining deck population")
    if blind_draws < 0 or other_hand + prizes + blind_draws > n:
        raise ValueError("invalid number of blind draws")
    return probability_full(
        n=n,
        hand=other_hand + blind_draws,
        prizes=prizes,
        first=stage1,
        second=stage2,
    )


def probability_stage2_given_stage1(
    stage1: int,
    stage2: int,
    blind_draws: int,
) -> Fraction:
    """Stage2 still in deck, conditional on at least one Stage1 in deck."""

    denominator = probability_stage_remaining(stage1, blind_draws)
    if denominator == 0:
        raise ValueError("conditional event of Stage1 in deck is impossible")
    return probability_joint_after_draws(stage1, stage2, blind_draws) / denominator
