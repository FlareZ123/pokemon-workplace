"""Post-draw Pareto frontier for Quick Ball allocation."""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
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
    return tuple(sorted(
        outcome
        for outcome in outcomes
        if not any(
            other != outcome
            and other[0] >= outcome[0]
            and other[1] >= outcome[1]
            for other in outcomes
        )
    ))


def allocation_draw_frontier_distribution(
    deck_size: int,
    prize_count: int,
    *,
    other_starters: int,
    attacker_starter_copies: int,
    critical_nonstarter: int,
    rescue_nonstarter: int,
    quick_ball_copies: int,
    disposable_nonstarter: int,
    later_random_draws: int,
    opening_hand_size: int = 7,
) -> dict[Frontier, float]:
    """Return the post-draw frontier over attacker and Gladion access."""
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
    post_prize_deck = deck_size - opening_hand_size - prize_count
    if not 0 <= later_random_draws <= post_prize_deck:
        raise ValueError("later_random_draws must fit in post-Prize deck")
    draw_denominator = _choose(post_prize_deck, later_random_draws)

    critical_mass = 0.0
    frontier_mass: dict[Frontier, float] = defaultdict(float)

    @lru_cache(maxsize=None)
    def draw_distribution(
        rescue_remaining: int,
        support_remaining: int,
        attacker_remaining: int,
        quick_remaining: int,
        disposable_remaining: int,
        other_remaining: int,
        rescue_in_hand: int,
        support_preserved: int,
        attacker_in_hand: int,
        quick_in_hand: int,
        disposable_in_hand: int,
    ) -> tuple[tuple[Frontier, float], ...]:
        local: dict[Frontier, float] = defaultdict(float)
        limits = (
            rescue_remaining,
            support_remaining,
            attacker_remaining,
            quick_remaining,
            disposable_remaining,
            other_remaining,
        )

        for drawn in _allocations(later_random_draws, limits):
            dr, dl, da, dq, dd, do = drawn
            ways = (
                _choose(rescue_remaining, dr)
                * _choose(support_remaining, dl)
                * _choose(attacker_remaining, da)
                * _choose(quick_remaining, dq)
                * _choose(disposable_remaining, dd)
                * _choose(other_remaining, do)
            )
            if ways == 0:
                continue

            attacker_now = attacker_in_hand + da >= 1
            attacker_in_deck = attacker_remaining - da >= 1
            rescue_hand = rescue_in_hand + dr >= 1
            rescue_deck = rescue_remaining - dr >= 1
            support_hand = support_preserved + dl >= 1
            support_deck = support_remaining - dl >= 1
            gladion_now = rescue_hand or (
                support_hand and rescue_deck
            )

            searches = min(
                quick_in_hand + dq,
                disposable_in_hand + dd,
            )
            can_search_attacker = (
                not attacker_now and attacker_in_deck
            )
            can_search_support = (
                not gladion_now
                and support_deck
                and rescue_deck
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

            local[_pareto(outcomes)] += ways / draw_denominator

        return tuple(local.items())

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
            rescue_remaining = remaining[1] - pr
            support_remaining = remaining[2] - pl
            attacker_remaining = remaining[3] - pa
            quick_remaining = remaining[4] - pq
            disposable_remaining = remaining[5] - pd
            other_remaining = post_prize_deck - (
                rescue_remaining
                + support_remaining
                + attacker_remaining
                + quick_remaining
                + disposable_remaining
            )
            support_preserved = int(
                hl == 1 and ha + hs >= 1
            )

            for frontier, probability in draw_distribution(
                rescue_remaining,
                support_remaining,
                attacker_remaining,
                quick_remaining,
                disposable_remaining,
                other_remaining,
                hr,
                support_preserved,
                ha,
                hq,
                hd,
            ):
                frontier_mass[frontier] += mass * probability

    if critical_mass == 0.0:
        return {}
    return {
        frontier: mass / critical_mass
        for frontier, mass in frontier_mass.items()
    }
