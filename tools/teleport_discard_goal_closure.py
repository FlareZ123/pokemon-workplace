"""Goal-level correction for a discard-fed Teleport line: natural target access.

The path-only event in teleport_discard_access_bound demands the target remain
in deck to be searched with Ultra Ball. The same Bench objective can be met
if the target is already in hand, while Ultra Ball still discards Sky Field
and another card to supply a live Teleport Room. This module sums the two
disjoint exact probability events.
"""
from __future__ import annotations

from fractions import Fraction

from teleport_discard_access_bound import (
    UnknownPool,
    at_least_one_of_each,
    k0_payload_probability,
    k1_payload_probability,
)


def target_naturally_in_hand_k0(spec: UnknownPool) -> Fraction:
    """Unconditional six-Prize/five-seen sample: singleton target is seen."""
    if spec.seen == 0:
        return Fraction(0)
    return Fraction(spec.seen, spec.total) * at_least_one_of_each(
        spec.total - 1,
        spec.seen - 1,
        (spec.ultra_ball, spec.sky_field, spec.approved_discard),
    )


def goal_level_k0(spec: UnknownPool) -> Fraction:
    """Ultra Ball supplies Sky to Teleport, target either in deck or hand."""
    return (
        k0_payload_probability(spec)
        + target_naturally_in_hand_k0(spec)
    )


def target_naturally_in_hand_k1(
    unprized_total: int,
    seen: int,
    *,
    unprized_ultra_ball: int,
    unprized_sky_field: int,
    unprized_approved_discard: int,
    target_prized: bool = False,
) -> Fraction:
    if target_prized or seen == 0:
        return Fraction(0)
    return Fraction(seen, unprized_total) * at_least_one_of_each(
        unprized_total - 1,
        seen - 1,
        (
            unprized_ultra_ball,
            unprized_sky_field,
            unprized_approved_discard,
        ),
    )


def goal_level_k1(
    unprized_total: int,
    seen: int,
    *,
    unprized_ultra_ball: int,
    unprized_sky_field: int,
    unprized_approved_discard: int,
    target_prized: bool = False,
) -> Fraction:
    kw = dict(
        unprized_ultra_ball=unprized_ultra_ball,
        unprized_sky_field=unprized_sky_field,
        unprized_approved_discard=unprized_approved_discard,
        target_prized=target_prized,
    )
    return k1_payload_probability(unprized_total, seen, **kw) + target_naturally_in_hand_k1(
        unprized_total, seen, **kw
    )


def exhaustive_goal_k0(spec: UnknownPool) -> tuple[Fraction, Fraction, Fraction]:
    """Independent labeled enumeration: target in deck and naturally in hand."""
    from itertools import combinations
    from math import comb

    symbols = (
        ("T",) * spec.searched_singleton
        + ("U",) * spec.ultra_ball
        + ("S",) * spec.sky_field
        + ("D",) * spec.approved_discard
    )
    symbols += ("F",) * (spec.total - len(symbols))
    deck_success = hand_success = total = 0
    universe = tuple(range(spec.total))
    for prizes in combinations(universe, spec.prizes):
        prize_set = set(prizes)
        available = tuple(i for i in universe if i not in prize_set)
        for seen in combinations(available, spec.seen):
            total += 1
            seen_types = {symbols[i] for i in seen}
            if not {"U", "S", "D"} <= seen_types:
                continue
            if any(symbols[i] == "T" for i in prizes):
                continue
            if "T" in seen_types:
                hand_success += 1
            else:
                deck_success += 1
    assert total == comb(spec.total, spec.prizes) * comb(
        spec.total - spec.prizes, spec.seen
    )
    return (
        Fraction(deck_success, total),
        Fraction(hand_success, total),
        Fraction(deck_success + hand_success, total),
    )
