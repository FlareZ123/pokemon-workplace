"""Exact pickup-assisted replay of a hand-to-Bench Basic support."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

from bench_double_trigger_access import _vectors, _ways


@dataclass(frozen=True)
class ReplayAccess:
    valid_start: Fraction
    no_pickup: Fraction
    active_recovery: Fraction
    bench_replay: Fraction
    combined: Fraction


def analyze_replay(*, deck_size: int = 60,
                   opening_size: int = 7,
                   prize_count: int = 6,
                   draws: int = 1,
                   other_basics: int = 3,
                   hand_search: int = 4,
                   direct_bench: int = 4,
                   guaranteed_pickups: int = 0,
                   coin_pickups: int = 4) -> ReplayAccess:
    """Exact accepted-opening access including two pickup-origin transitions.

    A singleton Basic support requires a from-hand Bench entry. Pickup allows
    replay after either forced starting-Active occupancy or an initial
    direct-from-deck-to-Bench placement. Search, pickup access and other
    gameplay details beyond the stated state variables are idealized.
    """
    groups = (1, other_basics, hand_search, direct_bench,
              guaranteed_pickups, coin_pickups)
    if min(groups) < 0 or sum(groups) > deck_size:
        raise ValueError("invalid card counts")
    if not 1 <= opening_size <= deck_size:
        raise ValueError("invalid opening size")
    if min(prize_count, draws) < 0:
        raise ValueError("negative Prize/draw count")
    if opening_size + prize_count + draws > deck_size:
        raise ValueError("exhausted deck")

    capacities = (*groups, deck_size - sum(groups))
    unseen = deck_size - opening_size - draws
    valid_openings = 0
    baseline_total = Fraction(0)
    active_total = Fraction(0)
    bench_total = Fraction(0)

    for opening in _vectors(capacities, opening_size):
        ow = _ways(capacities, opening)
        if not (opening[0] or opening[1]):
            continue
        valid_openings += ow
        remaining = tuple(a-b for a, b in zip(capacities, opening, strict=True))
        forced_active = int(opening[0] > 0 and opening[1] == 0)

        for drawn in _vectors(remaining, draws):
            dw = _ways(remaining, drawn)
            target_visible = opening[0] + drawn[0]
            other_seen = opening[1] + drawn[1]
            other_left = other_basics - other_seen
            hand = opening[2] + drawn[2]
            direct = opening[3] + drawn[3]
            sure = opening[4] + drawn[4]
            coin = opening[5] + drawn[5]
            pickup_success = (
                Fraction(1) if sure
                else Fraction((1 << coin) - 1, 1 << coin)
            )
            target_unseen = int(target_visible == 0)

            for prized_a in (range(2) if target_unseen else (0,)):
                for prized_other in range(
                    min(other_left, prize_count-prized_a) + 1
                ):
                    prize_ways = (
                        comb(other_left, prized_other)
                        * comb(unseen - target_unseen - other_left,
                               prize_count - prized_a - prized_other)
                    )
                    weight = ow * dw * prize_ways
                    a_searchable = bool(target_unseen and prized_a == 0)
                    ordinary = (
                        target_visible - forced_active > 0
                        or (hand > 0 and a_searchable)
                    )
                    # If the support starts Active, a different Basic must be
                    # Benched before scooping it, then promoted to Active.
                    active_possible = (
                        forced_active and (other_seen > 0 or (
                            hand + direct > 0 and other_left > prized_other
                        )) and (sure + coin) > 0
                    )
                    # If A starts in deck, first Nest Ball A directly onto
                    # Bench, scoop it, then play it from hand onto Bench.
                    bench_possible = (
                        a_searchable and hand == 0
                        and direct > 0 and (sure + coin) > 0
                    )
                    baseline_total += weight * int(ordinary)
                    active_total += weight * (
                        pickup_success if active_possible and not ordinary
                        else 0
                    )
                    bench_total += weight * (
                        pickup_success if bench_possible and not ordinary
                        else 0
                    )

    if valid_openings == 0:
        z = Fraction(0)
        return ReplayAccess(z, z, z, z, z)
    denom = (valid_openings
             * comb(deck_size - opening_size, draws)
             * comb(unseen, prize_count))
    baseline = baseline_total / denom
    active = active_total / denom
    bench = bench_total / denom
    return ReplayAccess(
        Fraction(valid_openings, comb(deck_size, opening_size)),
        baseline, active, bench, baseline + active + bench,
    )
