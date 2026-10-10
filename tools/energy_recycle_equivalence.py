from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations
from math import factorial


@dataclass(frozen=True)
class Outcome:
    """A fully visible material continuation conditional on a chosen mode/cards."""

    mode: str
    chosen: tuple[str, ...]
    hand: tuple[str, ...]
    discard: tuple[str, ...]
    deck_order: tuple[str, ...]
    conditional_probability: Fraction


def _shuffle_outcomes(
    mode: str,
    selected: tuple[str, ...],
    hand: tuple[str, ...],
    discard: tuple[str, ...],
    deck: tuple[str, ...],
) -> set[Outcome]:
    remaining = tuple(card for card in discard if card not in selected)
    contents = deck + selected
    probability = Fraction(1, factorial(len(contents)))
    return {
        Outcome(mode, selected, hand, remaining, ordered, probability)
        for ordered in permutations(contents)
    }


def historical_actions(
    hand: tuple[str, ...],
    discard: tuple[str, ...],
    deck: tuple[str, ...],
    basic_energy: tuple[str, ...],
) -> set[Outcome]:
    """EX-era public-discard 'show 1, or show 3' wording."""
    choices: set[Outcome] = set()
    for shown in basic_energy:
        remaining = tuple(card for card in discard if card != shown)
        choices.add(Outcome("hand", (shown,), hand + (shown,), remaining, deck, Fraction(1)))
    if basic_energy:
        for shown in combinations(basic_energy, min(3, len(basic_energy))):
            choices |= _shuffle_outcomes("deck", shown, hand, discard, deck)
    return choices


def current_actions(
    hand: tuple[str, ...],
    discard: tuple[str, ...],
    deck: tuple[str, ...],
    basic_energy: tuple[str, ...],
) -> set[Outcome]:
    """CES 'Choose 1' wording, resolving numbered choices under the rulebook."""
    choices: set[Outcome] = set()
    if basic_energy:
        for card in basic_energy:
            remaining = tuple(x for x in discard if x != card)
            choices.add(
                Outcome("hand", (card,), hand + (card,), remaining, deck, Fraction(1))
            )
        take = min(3, len(basic_energy))
        for selected in combinations(basic_energy, take):
            choices.update(_shuffle_outcomes("deck", selected, hand, discard, deck))
    return choices


def exhaustively_compare() -> dict[str, int]:
    """Enumerate small distinguishable card-instance states.

    The selected Basic Energy and all unrelated cards have different IDs.
    Discard is public, so explicit 'show' and visible movement into the
    hand/deck expose the same chosen IDs to both players.
    """
    worlds = 0
    outcomes = 0
    for energy_count in range(6):
        basic_energy = tuple(f"E{i}" for i in range(energy_count))
        for other_discard_count in range(3):
            others = tuple(f"X{i}" for i in range(other_discard_count))
            discard = basic_energy + others
            for deck_count in range(3):
                deck = tuple(f"D{i}" for i in range(deck_count))
                for hand_count in range(2):
                    hand = tuple(f"H{i}" for i in range(hand_count))
                    old = historical_actions(hand, discard, deck, basic_energy)
                    current = current_actions(hand, discard, deck, basic_energy)
                    assert old == current, (
                        energy_count, other_discard_count, deck_count,
                        hand_count, old ^ current
                    )
                    assert bool(old) == (energy_count > 0)
                    worlds += 1
                    outcomes += len(old)
    return {"worlds": worlds, "conditional_outcomes": outcomes}
