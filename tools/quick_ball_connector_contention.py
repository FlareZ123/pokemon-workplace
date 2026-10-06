"""Exact Quick Ball connector contention between attacker setup and Gladion access.

The model asks for two first-window goals at once:
1. establish at least one required Basic attacker;
2. obtain current-window Gladion access, directly or through Tapu Lele-GX.

Quick Ball can search either missing Basic target, but each copy can only perform
one search. A counterfactual "reusable connector" mode deliberately violates that
capacity to quantify how much a simple reachability graph can overstate joint
feasibility.

All Quick Ball discards use a designated binary disposable-card pool.
"""

from __future__ import annotations

from itertools import product
from math import comb


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def joint_attacker_and_gladion_probability(
    deck_size: int,
    prize_count: int,
    *,
    other_starters: int,
    attacker_starter_copies: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    quick_ball_copies: int,
    disposable_nonstarter: int,
    opening_hand_size: int = 7,
    reusable_connector_counterfactual: bool = False,
) -> float:
    """Return exact joint success given a valid start and any critical Prized.

    Exactly one Tapu Lele-GX-like support Basic is modeled. The required attacker
    is also a setup-eligible Basic and may have one or more copies.
    """
    support_basic = 1
    filler_nonstarter = (
        deck_size
        - support_basic
        - other_starters
        - attacker_starter_copies
        - critical_nonstarter
        - rescue_nonstarter
        - quick_ball_copies
        - disposable_nonstarter
    )
    if min(
        other_starters,
        attacker_starter_copies,
        critical_nonstarter,
        rescue_nonstarter,
        quick_ball_copies,
        disposable_nonstarter,
        filler_nonstarter,
    ) < 0:
        raise ValueError("modeled card counts must be non-negative and fit in the deck")

    # Category order:
    # critical, rescue, support Basic, attacker, Quick Ball, disposable,
    # other starter, filler.
    sizes = (
        critical_nonstarter,
        rescue_nonstarter,
        support_basic,
        attacker_starter_copies,
        quick_ball_copies,
        disposable_nonstarter,
        other_starters,
        filler_nonstarter,
    )
    total_starters = (
        support_basic
        + attacker_starter_copies
        + other_starters
    )
    opening_denominator = _choose(
        deck_size, opening_hand_size
    )
    opening_acceptance = 1.0 - _choose(
        deck_size - total_starters,
        opening_hand_size,
    ) / opening_denominator
    if opening_acceptance == 0.0:
        raise ValueError("valid opening has zero probability")

    joint_success_mass = 0.0
    critical_mass = 0.0

    for opening in product(*[
        range(min(size, opening_hand_size) + 1)
        for size in sizes
    ]):
        if sum(opening) != opening_hand_size:
            continue
        if opening[2] + opening[3] + opening[6] == 0:
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

            attacker_in_hand = opening[3] >= 1
            attacker_in_deck = (
                attacker_starter_copies
                - opening[3]
                - prizes[3]
            ) >= 1
            if not attacker_in_hand and not attacker_in_deck:
                continue

            rescue_in_hand = opening[1] >= 1
            rescue_in_deck = (
                rescue_nonstarter
                - opening[1]
                - prizes[1]
            ) >= 1

            support_in_hand = opening[2] == 1
            support_in_deck = (
                support_basic
                - opening[2]
                - prizes[2]
            ) >= 1

            # Wonder Tag is preserved only if some other starter can be used for
            # setup. The attacker itself can satisfy that role.
            support_preserved = (
                support_in_hand
                and opening[3] + opening[6] >= 1
            )

            attacker_searches = (
                0 if attacker_in_hand else 1
            )

            if rescue_in_hand:
                support_searches = 0
            elif support_preserved and rescue_in_deck:
                support_searches = 0
            elif support_in_deck and rescue_in_deck:
                support_searches = 1
            else:
                continue

            physical_searches = (
                attacker_searches + support_searches
            )
            if physical_searches == 0:
                joint_success_mass += mass
                continue

            if reusable_connector_counterfactual:
                # Deliberately wrong graph abstraction: one Quick Ball presence
                # may satisfy both missing Basic targets and pays only one discard.
                quick_balls_required = 1
                discards_required = 1
            else:
                quick_balls_required = physical_searches
                discards_required = physical_searches

            if opening[4] < quick_balls_required:
                continue
            if opening[5] < discards_required:
                continue

            joint_success_mass += mass

    if critical_mass == 0.0:
        return 0.0
    return joint_success_mass / critical_mass
