from __future__ import annotations

from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Outcome:
    """Material and opponent-visible result of one Item use."""

    chosen: str
    hand: tuple[str, ...]
    discard: tuple[str, ...]
    deck: tuple[str, ...]
    revealed_to_opponent: tuple[str, ...]


def historical_actions(
    hand: tuple[str, ...],
    discard: tuple[str, ...],
    deck: tuple[str, ...],
    supporter: frozenset[str],
) -> set[Outcome]:
    """Old wording: search the public pile, show one Supporter, return it."""
    choices: set[Outcome] = set()
    for index, shown in enumerate(discard):
        if shown.partition("#")[0] not in supporter:
            continue
        choices.add(
            Outcome(
                shown,
                hand + (shown,),
                discard[:index] + discard[index + 1 :],
                deck,
                (shown,),  # Explicit reveal from a public zone.
            )
        )
    return choices


def current_actions(
    hand: tuple[str, ...],
    discard: tuple[str, ...],
    deck: tuple[str, ...],
    supporter: frozenset[str],
) -> set[Outcome]:
    """XY wording: physically move any one Supporter from public discard."""
    choices: set[Outcome] = set()
    for selected in discard:
        if selected.partition("#")[0] not in supporter:
            continue
        new_discard = list(discard)
        new_discard.remove(selected)
        new_hand = list(hand)
        new_hand.append(selected)
        observed_departure = (selected,)
        choices.add(
            Outcome(
                selected,
                tuple(new_hand),
                tuple(new_discard),
                deck,
                observed_departure,
            )
        )
    return choices


def exhaustively_compare() -> dict[str, int]:
    """Public-discard model with unique instances, duplicates, and no Supporters."""
    symbols = ("S0", "S1", "I0", "P0")
    supporter = frozenset(("S0", "S1"))
    worlds = transitions = playable_worlds = 0
    for n in range(7):
        for card_types in product(symbols, repeat=n):
            discard = tuple(f"{card_type}#{i}" for i, card_type in enumerate(card_types))
            for hand in ((), ("H0",), ("H0", "H1")):
                for deck in ((), ("D0",)):
                    old = historical_actions(hand, discard, deck, supporter)
                    new = current_actions(hand, discard, deck, supporter)
                    assert old == new, (hand, discard, deck, old ^ new)
                    expected = any(c.split("#", 1)[0] in supporter for c in discard)
                    assert bool(old) == expected
                    assert all(o.deck == deck for o in old)
                    assert all(o.revealed_to_opponent == (o.chosen,) for o in old)
                    worlds += 1
                    transitions += len(old)
                    playable_worlds += bool(old)
    return {
        "worlds": worlds,
        "playable_worlds": playable_worlds,
        "conditional_outcomes": transitions,
    }
