"""Exact accepted-opening and Prize-aware two-support Bench trigger feasibility.

This is a bounded access model, not an attack/draw/lock simulator. Two distinct
singleton Basic support Pokémon are wanted for hand-to-Bench activations. Ideal
hand connectors can fetch ONE Basic from deck; direct-Bench connectors never
produce a hand-to-Bench trigger. One transactional Bench slot may be recycled
by guaranteed or coin-flip pickup Items, assumed already usable and accessible.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import comb
from typing import Iterator


@dataclass(frozen=True)
class JointAccess:
    valid_start: Fraction
    nominal: Fraction
    role_aware: Fraction
    typed_one_use: Fraction
    stochastic_exact: Fraction

    @property
    def active_role_gap(self) -> Fraction:
        return self.nominal - self.role_aware

    @property
    def connector_gap(self) -> Fraction:
        return self.role_aware - self.typed_one_use

    @property
    def coin_gap(self) -> Fraction:
        return self.typed_one_use - self.stochastic_exact


def _vectors(capacities: tuple[int, ...], total: int) -> Iterator[tuple[int, ...]]:
    """Grouped hypergeometric count vectors (small number of card classes)."""
    current = [0] * len(capacities)

    def visit(i: int, remaining: int) -> Iterator[tuple[int, ...]]:
        if i == len(capacities) - 1:
            if 0 <= remaining <= capacities[i]:
                current[i] = remaining
                yield tuple(current)
            return
        for n in range(min(capacities[i], remaining) + 1):
            current[i] = n
            yield from visit(i + 1, remaining - n)

    yield from visit(0, total)


def _ways(capacities: tuple[int, ...], take: tuple[int, ...]) -> int:
    return _product(comb(n, k) for n, k in zip(capacities, take, strict=True))


def _product(values: Iterator[int]) -> int:
    total = 1
    for value in values:
        total *= value
    return total


def analyze(
    *,
    deck_size: int = 60,
    opening_size: int = 7,
    prize_count: int = 6,
    draws: int = 1,
    other_basics: int = 4,
    hand_connectors: int = 4,
    direct_connectors: int = 4,
    certain_pickups: int = 0,
    coin_pickups: int = 2,
    bench_slack: int = 1,
) -> JointAccess:
    """Exact conditional joint-trigger probability.

    Both required singleton support Basics must be in hand or fetched into
    hand from deck. Opening Active remains unavailable. Connector access is
    abstract, before paying real costs or resolving any support Abilities.
    Coin pickup attempts succeed independently at probability 1/2 each.
    """
    groups = (1, 1, other_basics, hand_connectors, direct_connectors,
              certain_pickups, coin_pickups)
    if min(groups) < 0 or sum(groups) > deck_size:
        raise ValueError("invalid deck-class counts")
    if opening_size < 1 or opening_size > deck_size:
        raise ValueError("invalid opening_size")
    if draws < 0 or prize_count < 0 or opening_size + draws + prize_count > deck_size:
        raise ValueError("invalid draws/prizes")
    if bench_slack < 0 or bench_slack > 5:
        raise ValueError("invalid bench_slack")

    capacities = (*groups, deck_size - sum(groups))
    visible_unseen = deck_size - opening_size - draws
    prize_denominator = comb(visible_unseen, prize_count)
    coin_scale = 1 << coin_pickups
    valid_opening_ways = 0
    nominal_ways = role_ways = typed_ways = realized_scaled_ways = 0

    # Given a visible future random draw, the hidden Prize set is uniform among
    # the remaining unseen cards. This reverses the two exchangeable sampling
    # stages mathematically, without giving the player an extra observation.
    for opening in _vectors(capacities, opening_size):
        ow = _ways(capacities, opening)
        a, b, other, *_ = opening
        if not (a or b or other):
            continue
        valid_opening_ways += ow
        remaining = tuple(n - k for n, k in zip(capacities, opening, strict=True))
        forced_active_a = int(not other and a > 0)
        forced_active_b = int(not other and not a and b > 0)

        for drawn in _vectors(remaining, draws):
            dw = _ways(remaining, drawn)
            missing_a = int(opening[0] + drawn[0] == 0)
            missing_b = int(opening[1] + drawn[1] == 0)
            missing_total = missing_a + missing_b
            seen_hand = opening[3] + drawn[3]
            seen_direct = opening[4] + drawn[4]
            seen_certain = opening[5] + drawn[5]
            seen_coin = opening[6] + drawn[6]
            nominal_in_hand = (opening[0] + drawn[0], opening[1] + drawn[1])
            true_in_hand = (nominal_in_hand[0] - forced_active_a,
                            nominal_in_hand[1] - forced_active_b)

            # Only at most two unseen singleton targets can be in Prizes.
            for indicators in product((0, 1), repeat=missing_total):
                prize_a = indicators[0] if missing_a else 0
                prize_b = indicators[-1] if missing_b else 0
                chosen = sum(indicators)
                if chosen > prize_count:
                    continue
                prize_ways = comb(visible_unseen - missing_total,
                                  prize_count - chosen)
                weight = ow * dw * prize_ways
                searchable = (missing_a and not prize_a,
                              missing_b and not prize_b)
                nominal_reachable = all(
                    nominal_in_hand[i] > 0 or (seen_hand + seen_direct > 0 and searchable[i])
                    for i in range(2)
                )
                role_reachable = all(
                    true_in_hand[i] > 0 or (seen_hand + seen_direct > 0 and searchable[i])
                    for i in range(2)
                )
                required_connectors = sum(
                    1 for i in range(2) if true_in_hand[i] == 0
                )
                typed_reachable = (
                    all(true_in_hand[i] > 0 or searchable[i] for i in range(2))
                    and required_connectors <= seen_hand
                )
                release_possible = bench_slack >= 2 or (
                    bench_slack == 1 and seen_certain + seen_coin > 0
                )
                if bench_slack >= 1 and release_possible:
                    nominal_ways += weight * nominal_reachable
                    role_ways += weight * role_reachable
                    typed_ways += weight * typed_reachable
                    if typed_reachable:
                        if bench_slack >= 2 or seen_certain:
                            realized_scaled_ways += weight * coin_scale
                        else:
                            realized_scaled_ways += weight * (
                                coin_scale - (1 << (coin_pickups - seen_coin))
                            )

    if valid_opening_ways == 0:
        return JointAccess(*(Fraction(0) for _ in range(5)))
    base_denominator = (
        valid_opening_ways * comb(deck_size - opening_size, draws)
        * prize_denominator
    )
    return JointAccess(
        Fraction(valid_opening_ways, comb(deck_size, opening_size)),
        Fraction(nominal_ways, base_denominator),
        Fraction(role_ways, base_denominator),
        Fraction(typed_ways, base_denominator),
        Fraction(realized_scaled_ways, base_denominator * coin_scale),
    )
