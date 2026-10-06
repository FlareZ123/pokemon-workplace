"""Exact opening-window Gladion access through Quick Ball and Tapu Lele-GX.

The model captures a setup-specific trigger loss that generic connector graphs
miss: if Tapu Lele-GX is the only setup-eligible starter in the accepted opening
hand, it must be placed in the Active Spot during setup and cannot later fire
Wonder Tag merely by already being in play.

If another starter is present, the model assumes skilled play preserves Tapu
Lele-GX in hand for a manual hand-to-Bench play during the turn.

Quick Ball is modeled with a binary DCI-style disposable-card pool. Optionally,
spare Quick Ball copies beyond the one being played may also be discarded.
"""

from __future__ import annotations

from itertools import product
from math import comb


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def opening_gladion_access_probability(
    deck_size: int,
    prize_count: int,
    *,
    other_starters: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    quick_ball_copies: int,
    disposable_nonstarter: int,
    opening_hand_size: int = 7,
    allow_spare_quick_ball_discard: bool = False,
    ignore_setup_trigger_loss: bool = False,
) -> float:
    """Return P(current-window Gladion access | valid start, any critical Prized).

    Exactly one Tapu Lele-GX-like support Basic is modeled. It is a setup-
    eligible starter. Other starters, critical cards, rescue Supporters, Quick
    Ball copies, and disposable cards are disjoint categories.
    """
    support_basic = 1
    filler_nonstarter = (
        deck_size
        - support_basic
        - other_starters
        - critical_nonstarter
        - rescue_nonstarter
        - quick_ball_copies
        - disposable_nonstarter
    )
    if min(
        other_starters,
        critical_nonstarter,
        rescue_nonstarter,
        quick_ball_copies,
        disposable_nonstarter,
        filler_nonstarter,
    ) < 0:
        raise ValueError("modeled card counts must be non-negative and fit in the deck")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must fit in the deck")
    if not 0 <= opening_hand_size <= deck_size - prize_count:
        raise ValueError("opening hand must fit before Prize cards")

    # Category order:
    # critical, rescue, Tapu Lele-GX, Quick Ball, disposable, other starter, filler.
    sizes = (
        critical_nonstarter,
        rescue_nonstarter,
        support_basic,
        quick_ball_copies,
        disposable_nonstarter,
        other_starters,
        filler_nonstarter,
    )
    total_starters = support_basic + other_starters
    opening_denominator = _choose(deck_size, opening_hand_size)
    opening_acceptance = 1.0 - _choose(
        deck_size - total_starters,
        opening_hand_size,
    ) / opening_denominator
    if opening_acceptance == 0.0:
        raise ValueError("valid opening has zero probability")

    access_mass = 0.0
    critical_mass = 0.0

    for opening in product(*[
        range(min(size, opening_hand_size) + 1)
        for size in sizes
    ]):
        if sum(opening) != opening_hand_size:
            continue
        if opening[2] + opening[5] == 0:
            continue

        opening_ways = 1
        for size, count in zip(sizes, opening):
            opening_ways *= _choose(size, count)
        if opening_ways == 0:
            continue

        opening_mass = (
            opening_ways
            / opening_denominator
            / opening_acceptance
        )
        remaining = tuple(
            size - count
            for size, count in zip(sizes, opening)
        )
        prize_denominator = _choose(
            deck_size - opening_hand_size,
            prize_count,
        )

        for prizes in product(*[
            range(min(size, prize_count) + 1)
            for size in remaining
        ]):
            if sum(prizes) != prize_count:
                continue
            if prizes[0] == 0:
                continue

            prize_ways = 1
            for size, count in zip(remaining, prizes):
                prize_ways *= _choose(size, count)
            if prize_ways == 0:
                continue

            mass = (
                opening_mass
                * prize_ways
                / prize_denominator
            )
            critical_mass += mass

            rescue_in_hand = opening[1]
            rescue_in_deck = (
                rescue_nonstarter
                - opening[1]
                - prizes[1]
            )

            support_in_hand = opening[2] == 1
            support_in_deck = (
                support_basic
                - opening[2]
                - prizes[2]
            )

            if ignore_setup_trigger_loss:
                support_preserved = support_in_hand
            else:
                # If Tapu Lele-GX is the only starter in the accepted opening,
                # it must enter play during setup rather than being preserved in hand.
                support_preserved = (
                    support_in_hand
                    and opening[5] >= 1
                )

            discardable = opening[4]
            if allow_spare_quick_ball_discard:
                discardable += max(0, opening[3] - 1)

            direct_rescue = rescue_in_hand >= 1
            preserved_support_line = (
                support_preserved
                and rescue_in_deck >= 1
            )
            quick_ball_line = (
                opening[3] >= 1
                and discardable >= 1
                and support_in_deck >= 1
                and rescue_in_deck >= 1
            )

            if (
                direct_rescue
                or preserved_support_line
                or quick_ball_line
            ):
                access_mass += mass

    if critical_mass == 0.0:
        return 0.0
    return access_mass / critical_mass
