"""Exact Quick Ball payment and Nest Ball pickup-replay support planner.

Single target A needs to be played from hand onto Bench to trigger once.
The initial A may be in hand, searchable deck, or the Active Spot. A Nest
Ball-like Item can put A on Bench without the trigger; a pickup followed by
manual hand play can trigger it. A forced Active A can be picked up only
after a different Basic O is Benched for promotion.

Only this bounded action system is modeled, excluding actual Ability
payloads, lock effects, opposing play, and complex setup exceptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import comb

from bench_double_trigger_access import _vectors, _ways

UNAVAILABLE, HAND, DECK, ACTIVE, PRETRIGGER_BENCH = range(5)


@dataclass(frozen=True)
class PaidReplayState:
    a_zone: int
    other_in_hand: int
    other_in_deck: int
    other_on_bench: int
    quick_balls: int
    nest_balls: int
    discard_fuel: int
    sure_pickups: int
    coin_pickups: int


@lru_cache(maxsize=None)
def _optimal(state: PaidReplayState, free_slots: int, allow_backup_nest: bool, allow_target_nest: bool) -> Fraction:
    """Maximize probability over legal sequential actions and coin outcomes."""
    s = state
    # A is in hand and there is capacity for a genuine hand-entry play.
    if s.a_zone == HAND and s.other_on_bench < free_slots:
        return Fraction(1)
    best = Fraction(0)

    # When A starts Active, put a backup ordinary Basic onto Bench.
    if s.a_zone == ACTIVE and s.other_on_bench < free_slots:
        if s.other_in_hand:
            best = max(best, _optimal(PaidReplayState(
                s.a_zone, s.other_in_hand - 1, s.other_in_deck,
                s.other_on_bench + 1, s.quick_balls, s.nest_balls,
                s.discard_fuel, s.sure_pickups, s.coin_pickups,
            ), free_slots, allow_backup_nest, allow_target_nest))
        if allow_backup_nest and s.nest_balls and s.other_in_deck:
            best = max(best, _optimal(PaidReplayState(
                s.a_zone, s.other_in_hand, s.other_in_deck - 1,
                s.other_on_bench + 1, s.quick_balls, s.nest_balls - 1,
                s.discard_fuel, s.sure_pickups, s.coin_pickups,
            ), free_slots, allow_backup_nest, allow_target_nest))

    # Nest Ball may place A from deck directly onto Bench. This entry
    # does not trigger; the later pickup-and-hand-play transition can.
    if (allow_target_nest and s.a_zone == DECK and s.nest_balls
            and s.other_on_bench < free_slots):
        best = max(best, _optimal(PaidReplayState(
            PRETRIGGER_BENCH, s.other_in_hand, s.other_in_deck,
            s.other_on_bench, s.quick_balls, s.nest_balls - 1,
            s.discard_fuel, s.sure_pickups, s.coin_pickups,
        ), free_slots, allow_backup_nest, allow_target_nest))

    # Quick Ball searches exactly one useful Basic into hand after the
    # one-other-card payment. Every payment type is a separate action.
    if s.quick_balls:
        search_targets = []
        if s.a_zone == DECK:
            search_targets.append((HAND, s.other_in_hand, s.other_in_deck))
        if s.a_zone == ACTIVE and s.other_in_deck:
            search_targets.append(
                (ACTIVE, s.other_in_hand + 1, s.other_in_deck - 1)
            )
        for zone, fetched_other_hand, fetched_other_deck in search_targets:
            payments = []
            if s.discard_fuel:
                payments.append((
                    s.quick_balls - 1, s.nest_balls, s.discard_fuel - 1,
                    s.sure_pickups, s.coin_pickups, fetched_other_hand,
                ))
            if s.quick_balls >= 2:
                payments.append((
                    s.quick_balls - 2, s.nest_balls, s.discard_fuel,
                    s.sure_pickups, s.coin_pickups, fetched_other_hand,
                ))
            if s.nest_balls:
                payments.append((
                    s.quick_balls - 1, s.nest_balls - 1, s.discard_fuel,
                    s.sure_pickups, s.coin_pickups, fetched_other_hand,
                ))
            if s.sure_pickups:
                payments.append((
                    s.quick_balls - 1, s.nest_balls, s.discard_fuel,
                    s.sure_pickups - 1, s.coin_pickups, fetched_other_hand,
                ))
            if s.coin_pickups:
                payments.append((
                    s.quick_balls - 1, s.nest_balls, s.discard_fuel,
                    s.sure_pickups, s.coin_pickups - 1, fetched_other_hand,
                ))
            if s.other_in_hand:
                payments.append((
                    s.quick_balls - 1, s.nest_balls, s.discard_fuel,
                    s.sure_pickups, s.coin_pickups, fetched_other_hand - 1,
                ))
            for q, d, fuel, sure, coin, other_hand in payments:
                best = max(best, _optimal(PaidReplayState(
                    zone, other_hand, fetched_other_deck, s.other_on_bench,
                    q, d, fuel, sure, coin,
                ), free_slots, allow_backup_nest, allow_target_nest))

    # Scoop A from Active after the backup O occupies Bench, and promote O.
    # If A is on Bench from Nest Ball, scoop it with the original O Active.
    if s.a_zone == PRETRIGGER_BENCH or (
        s.a_zone == ACTIVE and s.other_on_bench
    ):
        promoted_bench = (
            s.other_on_bench - int(s.a_zone == ACTIVE)
        )
        if s.sure_pickups:
            best = max(best, _optimal(PaidReplayState(
                HAND, s.other_in_hand, s.other_in_deck, promoted_bench,
                s.quick_balls, s.nest_balls, s.discard_fuel,
                s.sure_pickups - 1, s.coin_pickups,
            ), free_slots, allow_backup_nest, allow_target_nest))
        if s.coin_pickups:
            success = PaidReplayState(
                HAND, s.other_in_hand, s.other_in_deck, promoted_bench,
                s.quick_balls, s.nest_balls, s.discard_fuel,
                s.sure_pickups, s.coin_pickups - 1,
            )
            failure = PaidReplayState(
                s.a_zone, s.other_in_hand, s.other_in_deck,
                s.other_on_bench, s.quick_balls, s.nest_balls,
                s.discard_fuel, s.sure_pickups, s.coin_pickups - 1,
            )
            best = max(best, (
                _optimal(success, free_slots, allow_backup_nest, allow_target_nest) +
                _optimal(failure, free_slots, allow_backup_nest, allow_target_nest)
            ) / 2)

    return best


def optimal_paid_replay(*, a_zone: int, other_in_hand: int,
                        other_in_deck: int, quick_balls: int,
                        nest_balls: int, discard_fuel: int,
                        sure_pickups: int, coin_pickups: int,
                        free_slots: int = 1,
                        allow_backup_nest: bool = True,
                        allow_target_nest: bool = True) -> Fraction:
    """Exact best-order chance for a supplied visible state."""
    if a_zone not in (UNAVAILABLE, HAND, DECK, ACTIVE):
        raise ValueError("invalid initial target zone")
    if min(other_in_hand, other_in_deck, quick_balls, nest_balls,
           discard_fuel, sure_pickups, coin_pickups) < 0:
        raise ValueError("negative card count")
    if not 1 <= free_slots <= 5:
        raise ValueError("free_slots must be in 1..5")
    return _optimal(PaidReplayState(
        a_zone, other_in_hand, other_in_deck, 0, quick_balls,
        nest_balls, discard_fuel, sure_pickups, coin_pickups,
    ), free_slots, allow_backup_nest, allow_target_nest)


def analyze_paid_replay(*, deck_size: int = 60,
                        opening_size: int = 7,
                        prize_count: int = 6,
                        draws: int = 1,
                        other_basics: int = 3,
                        quick_balls: int = 4,
                        nest_balls: int = 4,
                        expendable: int = 0,
                        sure_pickups: int = 0,
                        coin_pickups: int = 4,
                        free_slots: int = 1,
                        allow_backup_nest: bool = True,
                        allow_target_nest: bool = True) -> Fraction:
    """Exact accepted-opening-conditional access with realistic QB payment."""
    classes = (1, other_basics, quick_balls, nest_balls,
               expendable, sure_pickups, coin_pickups)
    if min(classes) < 0 or sum(classes) > deck_size:
        raise ValueError("invalid deck classes")
    if not 1 <= opening_size <= deck_size:
        raise ValueError("invalid opening size")
    if min(prize_count, draws) < 0 or opening_size + prize_count + draws > deck_size:
        raise ValueError("invalid Prize/draw state")
    if not 1 <= free_slots <= 5:
        raise ValueError("invalid free_slots")

    capacities = (*classes, deck_size - sum(classes))
    unseen = deck_size - opening_size - draws
    valid_opening_ways = 0
    weighted_success = Fraction(0)

    for opening in _vectors(capacities, opening_size):
        ow = _ways(capacities, opening)
        if not (opening[0] or opening[1]):
            continue
        valid_opening_ways += ow
        remaining = tuple(c-v for c, v in zip(capacities, opening, strict=True))
        forced_active = bool(opening[0] and not opening[1])

        for drawn in _vectors(remaining, draws):
            dw = _ways(remaining, drawn)
            target_visible = opening[0] + drawn[0]
            other_visible = opening[1] + drawn[1]
            other_unseen = other_basics - other_visible
            target_unseen = int(target_visible == 0)

            for prized_a in (range(2) if target_unseen else (0,)):
                for prized_other in range(
                    min(other_unseen, prize_count-prized_a) + 1
                ):
                    weight = (
                        ow * dw * comb(other_unseen, prized_other)
                        * comb(unseen - target_unseen - other_unseen,
                               prize_count - prized_a - prized_other)
                    )
                    zone = (
                        ACTIVE if forced_active else
                        HAND if target_visible else
                        DECK if prized_a == 0 else UNAVAILABLE
                    )
                    other_hand = other_visible - int(not forced_active)
                    success = optimal_paid_replay(
                        a_zone=zone, other_in_hand=other_hand,
                        other_in_deck=other_unseen - prized_other,
                        quick_balls=opening[2] + drawn[2],
                        nest_balls=opening[3] + drawn[3],
                        discard_fuel=opening[4] + drawn[4],
                        sure_pickups=opening[5] + drawn[5],
                        coin_pickups=opening[6] + drawn[6],
                        free_slots=free_slots,
                        allow_backup_nest=allow_backup_nest,
                        allow_target_nest=allow_target_nest,
                    )
                    weighted_success += weight * success

    if not valid_opening_ways:
        return Fraction(0)
    samples = (
        valid_opening_ways
        * comb(deck_size - opening_size, draws)
        * comb(unseen, prize_count)
    )
    return weighted_success / samples
