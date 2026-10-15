from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations, product
from math import factorial


@dataclass(frozen=True)
class Outcome:
    """Chosen Basic Energy and conditional post-shuffle continuation."""

    chosen: str | None
    hand: tuple[str, ...]
    deck: tuple[str, ...]
    public_reveal: tuple[str, ...]
    probability: Fraction


def historical_actions(
    hand: tuple[str, ...],
    deck: tuple[str, ...],
    basic_energy: frozenset[str],
) -> set[Outcome]:
    """Search, show, take, and shuffle. A restricted search may fail to find."""
    found: set[Outcome] = set()
    eligible: tuple[str | None, ...] = (None,) + tuple(
        c for c in deck if c in basic_energy
    )
    for selected in eligible:
        remaining = tuple(c for c in deck if c != selected) if selected else deck
        p = Fraction(1, factorial(len(remaining)))
        for shuffled in permutations(remaining):
            shown = (selected,) if selected else ()
            taken = hand + shown
            found.add(Outcome(selected, taken, shuffled, shown, p))
    return found


def current_actions(
    hand: tuple[str, ...],
    deck: tuple[str, ...],
    basic_energy: frozenset[str],
) -> set[Outcome]:
    """Find at most one eligible card, reveal it, then shuffle the remainder."""
    found: set[Outcome] = set()
    for selected_index in range(-1, len(deck)):
        if selected_index != -1 and deck[selected_index] not in basic_energy:
            continue
        available = list(deck)
        revealed: tuple[str, ...] = ()
        if selected_index >= 0:
            revealed = (available.pop(selected_index),)
        for shuffled in permutations(available):
            probability = Fraction(1, factorial(len(available)))
            found.add(
                Outcome(
                    revealed[0] if revealed else None,
                    hand + revealed,
                    shuffled,
                    revealed,
                    probability,
                )
            )
    return found


def exhaustively_compare() -> dict[str, int]:
    """Unique physical cards, varying search domains and known current hand."""
    worlds = outcomes = 0
    for size in range(6):
        for types in product(("E", "X"), repeat=size):
            deck = tuple(f"{kind}{i}" for i, kind in enumerate(types))
            basic = frozenset(card for card in deck if card.startswith("E"))
            for hand in ((), ("H",)):
                old = historical_actions(hand, deck, basic)
                new = current_actions(hand, deck, basic)
                assert old == new, (hand, deck, old ^ new)
                assert all(row.probability > 0 for row in old)
                assert all(len(row.deck) + len(row.public_reveal) == len(deck) for row in old)
                worlds += 1
                outcomes += len(old)
    return {"worlds": worlds, "conditional_outcomes": outcomes}
