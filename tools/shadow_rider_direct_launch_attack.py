"""Exact direct Radiant Eternatus dual-VMAX launch to next-turn Max Geist.

Require a non-Radiant Basic in the opening seven, Radiant in hand by turn
one's natural draw, and two VMAX left in deck. First-turn launch ends that
turn. An undisturbed next-turn draw precedes Underworld Door charging.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import comb, prod

from tools.shadow_rider_post_launch_energy import (
    EnergyWindow,
    attack_ready_probability,
    attack_and_pivot_ready_probability,
)

# Radiant, non-Radiant Basics, VMAX, Psychic Energy, Float Stone, other.
# The unchanged Aichi 2026 champion's complete 60-card deck.
COUNTS = (1, 13, 4, 11, 1, 30)


def choose(n: int, k: int) -> int:
    return comb(n, k) if 0 <= k <= n else 0


@lru_cache(None)
def allocations(n: int, caps: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    if len(caps) == 1:
        return ((n,),) if 0 <= n <= caps[0] else ()
    return tuple(
        (i,) + tail
        for i in range(min(n, caps[0]) + 1)
        for tail in allocations(n - i, caps[1:])
    )


@dataclass(frozen=True)
class LaunchAttack:
    launch: Fraction
    ready: Fraction
    ready_and_float: Fraction
    joint_residual_states: int


def exact_direct(
    *,
    counts: tuple[int, int, int, int, int, int] = COUNTS,
    opening: int = 7,
    prizes: int = 6,
    attack_cost: int = 3,
) -> LaunchAttack:
    """Exact route probabilities conditioned on an accepted Basic opener.

    The launcher is held/drawn Radiant rather than a paid search. At least
    one other Basic must be in the initial opening for Radiant to stay in
    hand rather than being the mandatory starting Active. Two VMAX are taken
    from the deck by Climactic Gate, followed by one next-turn natural draw.
    """
    if min(counts) < 0 or counts[0] != 1 or counts[2] < 2:
        raise ValueError("requires one Radiant and at least two VMAX")
    n = sum(counts)
    if not (0 < opening < n and 0 <= prizes <= n - opening - 5):
        raise ValueError("insufficient cards for setup, Prize, launch and draws")
    accepted = choose(n, opening) - choose(n - counts[0] - counts[1], opening)
    denominator = (
        accepted * choose(n - opening, prizes)
        * (n - opening - prizes) * (n - opening - prizes - 3)
    )
    weights: dict[tuple[int, int, int, int], int] = defaultdict(int)
    for hand in allocations(opening, counts):
        if not hand[1]:
            continue
        hand_ways = prod(choose(size, amount) for size, amount in zip(counts, hand))
        remaining = tuple(size - amount for size, amount in zip(counts, hand))
        for prize in allocations(prizes, remaining):
            prize_ways = prod(choose(size, amount) for size, amount in zip(remaining, prize))
            unseen = tuple(size - amount for size, amount in zip(remaining, prize))
            for first_draw, copies in enumerate(unseen):
                if not copies or not hand[0] + (first_draw == 0):
                    continue
                after_first = list(unseen)
                after_first[first_draw] -= 1
                if after_first[2] < 2:
                    continue
                after_first[2] -= 2
                weight = hand_ways * prize_ways * copies
                for next_draw, next_copies in enumerate(after_first):
                    if not next_copies:
                        continue
                    after_second = list(after_first)
                    after_second[next_draw] -= 1
                    key = (
                        hand[3] + (first_draw == 3) + (next_draw == 3),
                        after_second[3],
                        hand[4] + (first_draw == 4) + (next_draw == 4),
                        after_second[4],
                    )
                    weights[key] += weight * next_copies
    launching = sum(weights.values())
    energy_mass = Fraction()
    float_mass = Fraction()
    residual_size = n - opening - prizes - 4
    for (hand_energy, deck_energy, hand_float, deck_float), multiplicity in weights.items():
        mass = Fraction(multiplicity, denominator)
        state = EnergyWindow(hand_energy, deck_energy, residual_size)
        energy_mass += mass * attack_ready_probability(state, attack_cost)
        float_mass += mass * attack_and_pivot_ready_probability(
            state, attack_cost, pivots_in_deck=deck_float, pivots_in_hand=hand_float
        )
    return LaunchAttack(
        Fraction(launching, denominator), energy_mass, float_mass, len(weights)
    )
