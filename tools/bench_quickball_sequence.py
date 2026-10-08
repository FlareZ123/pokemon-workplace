"""Exact finite-state Quick Ball payment and hand-to-Bench sequencing."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import comb

UNAVAILABLE, HAND, DECK, BENCH, DISCARD = range(5)


@dataclass(frozen=True)
class SequenceState:
    a: int
    b: int
    triggered: int
    quick_balls: int
    discard_fuel: int
    sure_pickups: int
    coin_pickups: int


@lru_cache(maxsize=None)
def _optimize(state: SequenceState, free_slots: int) -> Fraction:
    """Maximize completion probability over adaptive legal action order."""
    if state.triggered == 3:
        return Fraction(1)

    zones = (state.a, state.b)
    best = Fraction(0)

    if sum(zone == BENCH for zone in zones) < free_slots:
        for i, zone in enumerate(zones):
            if zone == HAND and not (state.triggered & (1 << i)):
                updated = list(zones)
                updated[i] = BENCH
                best = max(best, _optimize(SequenceState(
                    *updated, state.triggered | (1 << i), state.quick_balls,
                    state.discard_fuel, state.sure_pickups, state.coin_pickups
                ), free_slots))

    # The played Quick Ball requires discarding one distinct other hand card.
    if state.quick_balls:
        for i, zone in enumerate(zones):
            if zone != DECK or (state.triggered & (1 << i)):
                continue
            updated = list(zones)
            updated[i] = HAND
            payments: list[tuple[int, int, int, int, list[int]]] = []
            if state.discard_fuel:
                payments.append((state.quick_balls - 1, state.discard_fuel - 1,
                                 state.sure_pickups, state.coin_pickups, updated))
            if state.quick_balls >= 2:
                payments.append((state.quick_balls - 2, state.discard_fuel,
                                 state.sure_pickups, state.coin_pickups, updated))
            if state.sure_pickups:
                payments.append((state.quick_balls - 1, state.discard_fuel,
                                 state.sure_pickups - 1, state.coin_pickups, updated))
            if state.coin_pickups:
                payments.append((state.quick_balls - 1, state.discard_fuel,
                                 state.sure_pickups, state.coin_pickups - 1, updated))
            for j, in_hand in enumerate(zones):
                if in_hand == HAND and (state.triggered & (1 << j)):
                    after_payment = updated.copy()
                    after_payment[j] = DISCARD
                    payments.append((state.quick_balls - 1, state.discard_fuel,
                                     state.sure_pickups, state.coin_pickups,
                                     after_payment))
            for qb, fuel, sure, coin, after in payments:
                best = max(best, _optimize(SequenceState(
                    *after, state.triggered, qb, fuel, sure, coin
                ), free_slots))

    # A pickup reclaims a slot, returns its spent support to hand, and can
    # create new discard fuel for a subsequent Quick Ball.
    for i, zone in enumerate(zones):
        if zone != BENCH:
            continue
        updated = list(zones)
        updated[i] = HAND
        if state.sure_pickups:
            best = max(best, _optimize(SequenceState(
                *updated, state.triggered, state.quick_balls,
                state.discard_fuel, state.sure_pickups - 1,
                state.coin_pickups
            ), free_slots))
        if state.coin_pickups:
            success = SequenceState(
                *updated, state.triggered, state.quick_balls,
                state.discard_fuel, state.sure_pickups,
                state.coin_pickups - 1
            )
            failed = SequenceState(
                *zones, state.triggered, state.quick_balls,
                state.discard_fuel, state.sure_pickups,
                state.coin_pickups - 1
            )
            best = max(best, (_optimize(success, free_slots)
                              + _optimize(failed, free_slots)) / 2)

    return best


def optimal_sequence_probability(*, a: int, b: int, quick_balls: int,
                                 discard_fuel: int, sure_pickups: int,
                                 coin_pickups: int,
                                 free_slots: int = 1) -> Fraction:
    """Optimal probability in this restricted two-trigger action model."""
    if a not in (UNAVAILABLE, HAND, DECK) or b not in (UNAVAILABLE, HAND, DECK):
        raise ValueError("invalid initial target zone")
    if min(quick_balls, discard_fuel, sure_pickups, coin_pickups) < 0:
        raise ValueError("negative resource count")
    if not 1 <= free_slots <= 5:
        raise ValueError("free_slots must be 1..5")
    return _optimize(SequenceState(
        a, b, 0, quick_balls, discard_fuel, sure_pickups, coin_pickups
    ), free_slots)


def payment_first_probability(*, a: int, b: int, quick_balls: int,
                              discard_fuel: int, sure_pickups: int,
                              coin_pickups: int, free_slots: int = 1) -> Fraction:
    """Best probability if both needed deck searches must occur first.

    Missing target searches can pay only from initial disposable cards,
    surplus Quick Balls, and pickup Items. Recycling a triggered Basic
    after its activation is deliberately forbidden in this baseline.
    """
    if UNAVAILABLE in (a, b):
        return Fraction(0)
    needs = int(a == DECK) + int(b == DECK)
    if quick_balls < needs:
        return Fraction(0)
    initial_fuel = discard_fuel + quick_balls - needs
    pickups_needed = max(0, 2 - free_slots)
    best = Fraction(0)
    for used_sure in range(sure_pickups + 1):
        for used_coin in range(coin_pickups + 1):
            if initial_fuel + used_sure + used_coin < needs:
                continue
            sure_left = sure_pickups - used_sure
            coin_left = coin_pickups - used_coin
            coin_needed = max(0, pickups_needed - sure_left)
            possible = sum(comb(coin_left, j)
                           for j in range(coin_needed, coin_left + 1))
            best = max(best, Fraction(possible, 1 << coin_left))
    return best
