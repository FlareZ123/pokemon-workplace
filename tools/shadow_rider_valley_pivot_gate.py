"""Exact singleton Dimension Valley and Float Stone access after direct Radiant launch.

The singleton Valley is exchangeable with the 30 non-core cards grouped in
the direct-launch enumerator, so its conditional zone probability is exact.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import comb, prod

from tools.shadow_rider_direct_launch_attack import COUNTS, allocations, choose
from tools.shadow_rider_post_launch_energy import (
    EnergyWindow, attack_and_pivot_ready_probability, attack_ready_probability,
)


@lru_cache(None)
def dual_card_draw_probability(
    energy_in_hand: int, energy_in_deck: int, deck_size: int,
    pivot_in_hand: int, pivot_in_deck: int,
    stadium_in_hand: int, stadium_in_deck: int,
    energy_cost: int, *,
    require_pivot: bool = True,
    require_stadium: bool = True,
) -> Fraction:
    """Exact chance after two conditionally payable draw-two Underworld Doors."""
    if min(energy_in_hand, energy_in_deck, pivot_in_hand, pivot_in_deck,
           stadium_in_hand, stadium_in_deck, energy_cost) < 0:
        raise ValueError("negative inventory")
    if energy_in_deck + pivot_in_deck + stadium_in_deck > deck_size:
        raise ValueError("inventory exceeds deck")
    states: dict[tuple[int, ...], Fraction] = {
        (energy_in_hand, pivot_in_hand, stadium_in_hand, energy_in_deck,
         pivot_in_deck, stadium_in_deck, deck_size, 0): Fraction(1),
    }
    for _ in range(2):
        next_states: dict[tuple[int, ...], Fraction] = defaultdict(Fraction)
        for (he, hp, hs, de, dp, ds, n, attached), mass in states.items():
            if he == 0:
                next_states[(he, hp, hs, de, dp, ds, n, attached)] += mass
                continue
            drawn = min(2, n)
            for a in range(drawn + 1):
                for b in range(drawn - a + 1):
                    for c in range(drawn - a - b + 1):
                        remaining = drawn - a - b - c
                        if a > de or b > dp or c > ds or remaining > n - de - dp - ds:
                            continue
                        probability = Fraction(
                            comb(de, a) * comb(dp, b) * comb(ds, c)
                            * comb(n-de-dp-ds, remaining), comb(n, drawn),
                        )
                        key = (
                            he - 1 + a, hp + b, hs + c, de - a, dp - b, ds - c,
                            n - drawn, attached + 1,
                        )
                        next_states[key] += mass * probability
        states = next_states
    assert sum(states.values(), Fraction()) == 1
    return sum(
        (mass for (he, hp, hs, _, _, _, _, attached), mass in states.items()
         if attached + int(he > 0) >= energy_cost
         and (hp > 0 or not require_pivot)
         and (hs > 0 or not require_stadium)),
        Fraction(),
    )


@dataclass(frozen=True)
class DirectValley:
    launch: Fraction
    cost_three_with_pivot: Fraction
    cost_two_with_valley: Fraction
    cost_two_with_valley_and_pivot: Fraction
    either_cost_with_pivot: Fraction
    cost_three_with_valley_and_pivot: Fraction
    residual_states: int


def exact_direct_valley(
    *,
    counts: tuple[int, int, int, int, int, int] = COUNTS,
    opening: int = 7,
    prizes: int = 6,
) -> DirectValley:
    """Count direct launch, two Energy modes, Float and actual Valley access.

    As in the source deck, the neutral class has exactly one Dimension Valley.
    On the following turn, Stadium permission and the Float retreat are assumed
    legal; the opponent is assumed not to disrupt the Bench/Abilities.
    """
    n = sum(counts)
    if min(counts) < 0 or counts[0] != 1 or counts[4] != 1 or counts[5] < 1:
        raise ValueError("requires exactly one Radiant, Float and Valley")
    if opening <= 0 or prizes < 0 or n - opening - prizes < 5:
        raise ValueError("insufficient residual deck")
    accepted = choose(n, opening) - choose(n-counts[0]-counts[1], opening)
    denominator = (
        accepted * choose(n-opening, prizes)
        * (n-opening-prizes) * (n-opening-prizes-3)
    )
    grouped: dict[tuple[int, ...], int] = defaultdict(int)
    for hand in allocations(opening, counts):
        if not hand[1]:
            continue
        ways_hand = prod(choose(c, x) for c, x in zip(counts, hand))
        remaining = tuple(c-x for c, x in zip(counts, hand))
        for prize in allocations(prizes, remaining):
            ways_prize = prod(choose(c, x) for c, x in zip(remaining, prize))
            unseen = tuple(c-x for c, x in zip(remaining, prize))
            for first, copies in enumerate(unseen):
                if not copies or not (hand[0] or first == 0):
                    continue
                after_first = list(unseen)
                after_first[first] -= 1
                if after_first[2] < 2:
                    continue
                after_first[2] -= 2
                weight = ways_hand * ways_prize * copies
                for second, available in enumerate(after_first):
                    if not available:
                        continue
                    after_second = list(after_first)
                    after_second[second] -= 1
                    key = (
                        hand[3] + (first == 3) + (second == 3), after_second[3],
                        hand[4] + (first == 4) + (second == 4), after_second[4],
                        hand[5] + (first == 5) + (second == 5), after_second[5],
                        prize[5],
                    )
                    grouped[key] += weight * available
    launch = Fraction(sum(grouped.values()), denominator)
    with_pivot_three = Fraction()
    with_valley_two = Fraction()
    with_valley_two_pivot = Fraction()
    with_valley_three_pivot = Fraction()
    residual_deck = n - opening - prizes - 4
    for (he, de, hp, dp, neutral_hand, neutral_deck, _), ways in grouped.items():
        mass = Fraction(ways, denominator)
        window = EnergyWindow(he, de, residual_deck)
        three_pivot = attack_and_pivot_ready_probability(
            window, 3, pivots_in_deck=dp, pivots_in_hand=hp,
        )
        with_pivot_three += mass * three_pivot
        p_stadium_held = Fraction(neutral_hand, counts[5])
        p_stadium_in_deck = Fraction(neutral_deck, counts[5])
        two_held = attack_ready_probability(window, 2)
        two_pivot_held = attack_and_pivot_ready_probability(
            window, 2, pivots_in_deck=dp, pivots_in_hand=hp,
        )
        if neutral_deck:
            two_deck = dual_card_draw_probability(
                he, de, residual_deck, hp, dp, 0, 1, 2,
                require_pivot=False,
            )
            two_pivot_deck = dual_card_draw_probability(
                he, de, residual_deck, hp, dp, 0, 1, 2,
            )
            three_pivot_deck = dual_card_draw_probability(
                he, de, residual_deck, hp, dp, 0, 1, 3,
            )
        else:
            two_deck = two_pivot_deck = three_pivot_deck = Fraction()
        with_valley_two += mass * (
            p_stadium_held * two_held + p_stadium_in_deck * two_deck
        )
        with_valley_two_pivot += mass * (
            p_stadium_held * two_pivot_held
            + p_stadium_in_deck * two_pivot_deck
        )
        with_valley_three_pivot += mass * (
            p_stadium_held * three_pivot
            + p_stadium_in_deck * three_pivot_deck
        )
    either = with_pivot_three + with_valley_two_pivot - with_valley_three_pivot
    assert with_pivot_three <= either <= launch
    return DirectValley(
        launch, with_pivot_three, with_valley_two,
        with_valley_two_pivot, either, with_valley_three_pivot, len(grouped),
    )
