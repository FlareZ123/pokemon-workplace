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
