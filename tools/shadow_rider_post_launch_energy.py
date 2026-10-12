"""Exact conditional post-Radiant Shadow Rider Calyrex VMAX attack-Energy probability.

Assume a Benched Psychic VMAX target, live Underworld Door sources, uniformly
shuffled deck, no other draws, and an independently available legal promotion.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class EnergyWindow:
    hand_energy: int
    deck_energy: int
    deck_size: int
    doors: int = 2
    cards_per_draw: int = 2
    manual_attachment: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.deck_energy <= self.deck_size:
            raise ValueError("deck Energy count must fit the deck")
        if min(self.hand_energy, self.doors, self.cards_per_draw) < 0:
            raise ValueError("hand count, Ability count and draw size must be nonnegative")


def hypergeometric(energy: int, size: int, drawn: int, hits: int) -> Fraction:
    """Exact probability of hits Psychic Energy in a draw batch."""
    if not (0 <= hits <= energy and 0 <= drawn - hits <= size - energy):
        return Fraction(0)
    return Fraction(comb(energy, hits) * comb(size - energy, drawn - hits), comb(size, drawn))


def attack_ready_probability(window: EnergyWindow, cost: int) -> Fraction:
    """Chance to place at least cost Energy onto one Benched VMAX by this turn.

    Save the normal hand attachment for last. Spending hand Energy on an early
    ordinary attachment cannot improve the Ability's draw opportunities.
    """
    if cost < 0:
        raise ValueError("attack cost must be nonnegative")
    states: dict[tuple[int, int, int, int], Fraction] = {
        (window.hand_energy, window.deck_energy, window.deck_size, 0): Fraction(1)
    }
    for _ in range(window.doors):
        next_states: dict[tuple[int, int, int, int], Fraction] = {}
        for (hand, deck_energy, deck_size, attached), probability in states.items():
            if hand == 0:
                key = (hand, deck_energy, deck_size, attached)
                next_states[key] = next_states.get(key, Fraction()) + probability
                continue
            count = min(window.cards_per_draw, deck_size)
            for hits in range(count + 1):
                chance = hypergeometric(deck_energy, deck_size, count, hits)
                if chance == 0:
                    continue
                key = (hand - 1 + hits, deck_energy - hits, deck_size - count, attached + 1)
                next_states[key] = next_states.get(key, Fraction()) + probability * chance
        states = next_states
    assert sum(states.values(), Fraction()) == 1
    return sum((
        probability for (hand, _, _, attached), probability in states.items()
        if attached + int(window.manual_attachment and hand > 0) >= cost
    ), Fraction())


def attack_and_pivot_ready_probability(
    window: EnergyWindow, cost: int, *, pivots_in_deck: int, pivots_in_hand: int = 0
) -> Fraction:
    """Joint chance of attack Energy and a Float Stone-like pivot card.

    The pivot is assumed to be a playable Tool sufficient to retreat the
    starting Active Pokémon after charging. Locks, occupied Tool slots,
    promotion restrictions and alternate pivot routes are not modeled.
    """
    if cost < 0 or pivots_in_hand < 0 or not 0 <= pivots_in_deck <= window.deck_size - window.deck_energy:
        raise ValueError("invalid cost or pivot counts")
    states = {(window.hand_energy, pivots_in_hand, window.deck_energy,
               pivots_in_deck, window.deck_size, 0): Fraction(1)}
    for _ in range(window.doors):
        following = {}
        for (hand, pivots, e, p, n, attached), mass in states.items():
            if not hand:
                key = (hand, pivots, e, p, n, attached)
                following[key] = following.get(key, Fraction()) + mass
                continue
            drawn = min(window.cards_per_draw, n)
            for de in range(drawn + 1):
                for dp in range(drawn - de + 1):
                    other = drawn - de - dp
                    if de > e or dp > p or other > n - e - p:
                        continue
                    chance = Fraction(
                        comb(e, de) * comb(p, dp) * comb(n - e - p, other),
                        comb(n, drawn),
                    )
                    key = (hand - 1 + de, pivots + dp, e - de, p - dp,
                           n - drawn, attached + 1)
                    following[key] = following.get(key, Fraction()) + mass * chance
        states = following
    assert sum(states.values(), Fraction()) == 1
    return sum(
        (mass for (h, pivot_h, _, _, _, attached), mass in states.items()
         if attached + int(window.manual_attachment and h > 0) >= cost and pivot_h > 0),
        Fraction(),
    )
