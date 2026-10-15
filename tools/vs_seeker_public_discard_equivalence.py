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


def _outcomes(
    hand: tuple[str, ...],
    discard: tuple[str, ...],
    deck: tuple[str, ...],
    supporter: frozenset[str],
    *,
    explicit_show: bool,
) -> set[Outcome]:
    """Choose one visible Supporter; public removal identifies it in either text."""
    found: set[Outcome] = set()
    for i, card in enumerate(discard):
        if card.split("#", 1)[0] not in supporter:
            continue
        remaining = discard[:i] + discard[i + 1 :]
        # Both explicit showing and moving one observed face-up card disclose
        # the identity of exactly the retrieved card to the opponent.
        visible = (card,) if explicit_show else (discard[i],)
        found.add(Outcome(card, hand + (card,), remaining, deck, visible))
    return found


def historical_actions(
    hand: tuple[str, ...],
    discard: tuple[str, ...],
    deck: tuple[str, ...],
    supporter: frozenset[str],
) -> set[Outcome]:
    """EX Deoxys / Platinum Rising Rivals: search, show, move to hand."""
    return _outcomes(hand, discard, deck, supporter, explicit_show=True)


def current_actions(
    hand: tuple[str, ...],
    discard: tuple[str, ...],
    deck: tuple[str, ...],
    supporter: frozenset[str],
) -> set[Outcome]:
    """XY Phantom Forces / Roaring Skies: put Supporter from discard to hand."""
    return _outcomes(hand, discard, deck, supporter, explicit_show=False)


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
