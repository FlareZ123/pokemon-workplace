"""Exact probability of rescuing a forced starting-Active support Basic.

A single Basic support requires a hand-to-Bench entry. If it was forced to
start Active, a pickup can return it to hand once another Basic occupies the
Bench and can be promoted. Idealized deck-to-hand and direct-Bench search
can both establish that backup; only the former can obtain the support
itself into hand when it remains in deck. All searches are zero-cost here.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb

from bench_double_trigger_access import _vectors, _ways


@dataclass(frozen=True)
class ActiveRescue:
    valid_start: Fraction
    no_active_recovery: Fraction
    with_active_recovery: Fraction
    gain: Fraction
    rescue_attempt_possible: Fraction


def analyze_rescue(*, deck_size: int = 60,
                   opening_size: int = 7,
                   prize_count: int = 6,
                   later_random_draws: int = 1,
                   other_basics: int = 3,
                   hand_connectors: int = 4,
                   direct_bench_items: int = 4,
                   guaranteed_pickups: int = 0,
                   coin_pickups: int = 4) -> ActiveRescue:
    """Exact conditional hand-to-Bench trigger access with Active pickup.

    The two relevant backups are an ordinary Basic drawn after setup, or
    an unprized ordinary Basic fetched by a visible hand/direct-Bench Item.
    An Active support A may be scooped only after one backup is established.
    On a successful scoop, the player's new Active is that backup.
    """
    groups = (1, other_basics, hand_connectors, direct_bench_items,
              guaranteed_pickups, coin_pickups)
    if min(groups) < 0 or sum(groups) > deck_size:
        raise ValueError("invalid card counts")
    if not 1 <= opening_size <= deck_size:
        raise ValueError("invalid opening size")
    if min(prize_count, later_random_draws) < 0:
        raise ValueError("negative Prize or draw count")
    if opening_size + prize_count + later_random_draws > deck_size:
        raise ValueError("exhausted deck")

    capacities = (*groups, deck_size - sum(groups))
    unseen = deck_size - opening_size - later_random_draws
    valid_openings = 0
    no_rescue = Fraction(0)
    with_rescue = Fraction(0)
    attempt_mass = Fraction(0)

    for opening in _vectors(capacities, opening_size):
        opening_ways = _ways(capacities, opening)
        if not (opening[0] or opening[1]):
            continue
        valid_openings += opening_ways
        remaining = tuple(n - k for n, k in zip(capacities, opening, strict=True))
        forced_active = opening[0] > 0 and opening[1] == 0

        for drawn in _vectors(remaining, later_random_draws):
            draw_ways = _ways(remaining, drawn)
            unseen_a = int(opening[0] + drawn[0] == 0)
            other_left = other_basics - opening[1] - drawn[1]
            already_have_backup = opening[1] + drawn[1] > 0
            hand_outs = opening[2] + drawn[2]
            bench_outs = opening[3] + drawn[3]
            sure = opening[4] + drawn[4]
            coins = opening[5] + drawn[5]

            # Conditional on visible opening and draw, choose Prize membership
            # of the singleton A and count of remaining other Basic copies.
            for prized_a in (range(2) if unseen_a else (0,)):
                for prized_other in range(
                    min(other_left, prize_count - prized_a) + 1
                ):
                    compatible_prizes = (
                        comb(other_left, prized_other)
                        * comb(unseen - unseen_a - other_left,
                               prize_count - prized_a - prized_other)
                    )
                    weight = opening_ways * draw_ways * compatible_prizes
                    a_in_deck = unseen_a and prized_a == 0
                    baseline = (
                        opening[0] + drawn[0] - int(forced_active) > 0
                        or (hand_outs > 0 and a_in_deck)
                    )
                    backup = (
                        already_have_backup
                        or (hand_outs + bench_outs > 0
                            and other_left > prized_other)
                    )
                    can_attempt_rescue = bool(
                        forced_active and backup and (sure + coins) > 0
                    )
                    success_coin = (
                        Fraction(1) if sure
                        else Fraction((1 << coins) - 1, 1 << coins)
                    )
                    no_rescue += weight * int(baseline)
                    attempt_mass += weight * int(can_attempt_rescue)
                    with_rescue += weight * (
                        int(baseline)
                        + (success_coin
                           if can_attempt_rescue and not baseline
                           else 0)
                    )

    if valid_openings == 0:
        z = Fraction(0)
        return ActiveRescue(z, z, z, z, z)

    denominator = (
        valid_openings
        * comb(deck_size - opening_size, later_random_draws)
        * comb(unseen, prize_count)
    )
    p0 = no_rescue / denominator
    p1 = with_rescue / denominator
    return ActiveRescue(
        Fraction(valid_openings, comb(deck_size, opening_size)),
        p0, p1, p1 - p0, attempt_mass / denominator,
    )
