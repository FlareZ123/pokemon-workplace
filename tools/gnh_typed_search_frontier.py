"""Named-category action frontier for a played Guzma & Hala in Aichi Expanded.

The Supporter has already been moved out of hand by the caller.
An optional two-card cost is committed before deck inspection.
Search categories are type-restricted, and each can select zero cards.
This module enumerates legal material actions, not K0 decision policies.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement, product

from tools.aichi_post_gnh_prize_reset import Prepared

STADIUMS = frozenset({"Artazon", "Grand Tree"})
TOOLS = frozenset({
    "Stealthy Hood", "Technical Machine: Evolution", "Counter Gain",
})
SPECIAL_ENERGY = frozenset({"Capture Energy", "Jet Energy", "Memory Energy"})


@dataclass(frozen=True)
class Action:
    paid_with: tuple[str, str] | None
    stadium: str | None
    tool: str | None
    special_energy: str | None


@dataclass
class Outcome:
    action: Action
    hand: Counter[str]
    deck: Counter[str]
    discarded: Counter[str]


def options(state: Prepared, protected: frozenset[str] = frozenset()) -> list[Outcome]:
    """Enumerate the G&H on-play payment and its three later searches."""
    if not state.gnh_access:
        return []

    payments: list[tuple[str, str] | None] = [None]
    names = sorted(name for name, number in state.hand.items()
                   if number > 0 and name not in protected)
    payments.extend((a, b) for a, b in combinations_with_replacement(names, 2)
                    if a != b or state.hand[a] >= 2)

    outcomes: list[Outcome] = []
    for payment in payments:
        held, deck, discarded = state.hand.copy(), state.remaining.copy(), Counter()
        if payment is not None:
            for name in payment:
                held[name] -= 1
                discarded[name] += 1
                if held[name] == 0:
                    del held[name]

        stadium_choices = (None,) + tuple(sorted(name for name in deck
                                                 if name in STADIUMS and deck[name] > 0))
        tool_choices = (None,) if payment is None else (None,) + tuple(
            sorted(name for name in deck if name in TOOLS and deck[name] > 0))
        energy_choices = (None,) if payment is None else (None,) + tuple(
            sorted(name for name in deck if name in SPECIAL_ENERGY and deck[name] > 0))

        for stadium, tool, energy in product(
            stadium_choices, tool_choices, energy_choices
        ):
            next_hand, next_deck = held.copy(), deck.copy()
            for fetched in (stadium, tool, energy):
                if fetched is None:
                    continue
                next_hand[fetched] += 1
                next_deck[fetched] -= 1
                if next_deck[fetched] == 0:
                    del next_deck[fetched]
            outcomes.append(Outcome(
                Action(payment, stadium, tool, energy),
                next_hand, next_deck, discarded.copy(),
            ))
    return outcomes
