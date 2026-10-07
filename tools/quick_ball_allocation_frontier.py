"""Pareto frontier for allocating Quick Ball between attacker setup and Gladion access."""

from __future__ import annotations

from collections import defaultdict
from math import comb


Outcome = tuple[int, int]
Frontier = tuple[Outcome, ...]


def _choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


def _allocations(total: int, limits: tuple[int, ...]):
    current = [0] * len(limits)

    def rec(index: int, left: int):
        if index == len(limits) - 1:
            if left <= limits[index]:
                current[index] = left
                yield tuple(current)
            return
        for value in range(min(limits[index], left) + 1):
            current[index] = value
            yield from rec(index + 1, left - value)

    yield from rec(0, total)


def _pareto(outcomes: set[Outcome]) -> Frontier:
    maximal = {
        outcome
        for outcome in outcomes
        if not any(
            other != outcome
            and other[0] >= outcome[0]
            and other[1] >= outcome[1]
            for other in outcomes
        )
    }
    return tuple(sorted(maximal))


def allocation_frontier_distribution(
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
) -> dict[Frontier, float]:
    """Return frontier probabilities given a valid start and a critical Prize.

    Outcome coordinates are (attacker established, Gladion accessible). Quick
    Ball searches consume one physical copy and one designated disposable card.
    Exactly one Tapu Lele-GX-like setup Basic is modeled.
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
        raise ValueError("modeled counts must be non-negative and fit in deck")

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
    starters = support_basic + attacker_starter_copies + other_starters
    hand_denominator = _choose(deck_size, opening_hand_size)
    acceptance = (
        1.0
        - _choose(deck_size - starters, opening_hand_size) / hand_denominator
    )
    if acceptance == 0.0:
        raise ValueError("valid opening has zero probability")
    prize_denominator = _choose(deck_size - opening_hand_size, prize_count)

    critical_mass = 0.0
    frontier_mass: dict[Frontier, float] = defaultdict(float)

    for hand in _allocations(opening_hand_size, sizes):
        hc, hr, hl, ha, hq, hd, hs, hf = hand
        if hl + ha + hs == 0:
            continue
        hand_ways = (
            _choose(critical_nonstarter, hc)
            * _choose(rescue_nonstarter, hr)
            * _choose(support_basic, hl)
            * _choose(attacker_starter_copies, ha)
            * _choose(quick_ball_copies, hq)
            * _choose(disposable_nonstarter, hd)
            * _choose(other_starters, hs)
            * _choose(filler_nonstarter, hf)
        )
        if hand_ways == 0:
            continue
        hand_mass = hand_ways / hand_denominator / acceptance
        remaining = tuple(n - x for n, x in zip(sizes, hand))
        prize_limits = (
            remaining[0],
            remaining[1],
            remaining[2],
            remaining[3],
            remaining[4],
            remaining[5],
            remaining[6] + remaining[7],
        )

        for prizes in _allocations(prize_count, prize_limits):
            pc, pr, pl, pa, pq, pd, po = prizes
            if pc == 0:
                continue
            prize_ways = (
                _choose(remaining[0], pc)
                * _choose(remaining[1], pr)
                * _choose(remaining[2], pl)
                * _choose(remaining[3], pa)
                * _choose(remaining[4], pq)
                * _choose(remaining[5], pd)
                * _choose(remaining[6] + remaining[7], po)
            )
            if prize_ways == 0:
                continue
            mass = hand_mass * prize_ways / prize_denominator
            critical_mass += mass

            attacker_now = ha >= 1
            attacker_in_deck = attacker_starter_copies - ha - pa >= 1
            rescue_in_hand = hr >= 1
            rescue_in_deck = rescue_nonstarter - hr - pr >= 1
            support_preserved = hl == 1 and ha + hs >= 1
            support_in_deck = support_basic - hl - pl >= 1
            gladion_now = rescue_in_hand or (
                support_preserved and rescue_in_deck
            )

            searches = min(hq, hd)
            can_search_attacker = (
                not attacker_now and attacker_in_deck
            )
            can_search_support = (
                not gladion_now
                and support_in_deck
                and rescue_in_deck
            )

            outcomes: set[Outcome] = {
                (int(attacker_now), int(gladion_now))
            }
            if searches >= 1:
                if can_search_attacker:
                    outcomes.add((1, int(gladion_now)))
                if can_search_support:
                    outcomes.add((int(attacker_now), 1))
            if (
                searches >= 2
                and can_search_attacker
                and can_search_support
            ):
                outcomes.add((1, 1))

            frontier_mass[_pareto(outcomes)] += mass

    if critical_mass == 0.0:
        return {}
    return {
        key: value / critical_mass
        for key, value in frontier_mass.items()
    }


def additive_expected_utility(
    distribution: dict[Frontier, float],
    *,
    attacker_value: float,
    gladion_value: float,
) -> float:
    """Evaluate optimal non-negative additive utility on each frontier."""
    if attacker_value < 0 or gladion_value < 0:
        raise ValueError("frontier utility helper expects non-negative values")
    total = 0.0
    for frontier, probability in distribution.items():
        best = max(
            attacker_value * attacker + gladion_value * gladion
            for attacker, gladion in frontier
        )
        total += probability * best
    return total
