"""Material-state proof harness for search-before-reset dominance.

A constrained search Item can intentionally select zero cards. If an imminent
reset will discard the entire remaining hand and draw a fresh hand, playing the
search Item first with a payment that would otherwise be discarded can preserve
the same unordered material state while adding deck-composition knowledge.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class ResetState:
    hand: tuple[str, ...]
    deck: tuple[str, ...]
    discard: tuple[str, ...] = ()
    bench: tuple[str, ...] = ()
    deck_searched: bool = False


def _remove_one(cards: list[str], target: str) -> None:
    cards.remove(target)


def _draw_named(deck: list[str], draw: tuple[str, ...]) -> None:
    for card in draw:
        _remove_one(deck, card)


def search_then_reset(
    state: ResetState,
    *,
    resetter: str,
    payment: str,
    fresh_draw: tuple[str, ...],
    resetter_already_in_play: bool = False,
) -> ResetState:
    """Resolve zero-target Quick Ball, then a discard-hand/draw reset.

    Deck order is intentionally abstracted away. The Quick Ball search selects
    zero Basic Pokemon, so deck composition is unchanged before the fresh draw.
    """

    hand = list(state.hand)
    deck = list(state.deck)
    discard = list(state.discard)
    bench = list(state.bench)

    if "Quick Ball" not in hand:
        raise ValueError("Quick Ball must be in hand")
    if payment == "Quick Ball":
        raise ValueError("Quick Ball cannot pay its own another-card cost")
    if payment not in hand:
        raise ValueError("payment must be in hand")
    if not resetter_already_in_play and resetter not in hand:
        raise ValueError("resetter must be in hand when it is not already in play")
    if not resetter_already_in_play and payment == resetter:
        raise ValueError("payment must preserve the held resetter")

    _remove_one(hand, "Quick Ball")
    _remove_one(hand, payment)
    discard.extend(("Quick Ball", payment))

    if not resetter_already_in_play:
        _remove_one(hand, resetter)
        bench.append(resetter)

    discard.extend(hand)
    hand.clear()
    _draw_named(deck, fresh_draw)
    hand.extend(fresh_draw)

    return ResetState(
        hand=tuple(hand),
        deck=tuple(deck),
        discard=tuple(discard),
        bench=tuple(bench),
        deck_searched=True,
    )


def reset_first(
    state: ResetState,
    *,
    resetter: str,
    fresh_draw: tuple[str, ...],
    resetter_already_in_play: bool = False,
) -> ResetState:
    """Resolve the same discard-hand/draw reset without first using Quick Ball."""

    hand = list(state.hand)
    deck = list(state.deck)
    discard = list(state.discard)
    bench = list(state.bench)

    if not resetter_already_in_play:
        if resetter not in hand:
            raise ValueError("resetter must be in hand when it is not already in play")
        _remove_one(hand, resetter)
        bench.append(resetter)

    discard.extend(hand)
    hand.clear()
    _draw_named(deck, fresh_draw)
    hand.extend(fresh_draw)

    return ResetState(
        hand=tuple(hand),
        deck=tuple(deck),
        discard=tuple(discard),
        bench=tuple(bench),
        deck_searched=state.deck_searched,
    )


def same_material_state(left: ResetState, right: ResetState) -> bool:
    """Compare zones as multisets while ignoring search-information metadata."""

    return (
        Counter(left.hand) == Counter(right.hand)
        and Counter(left.deck) == Counter(right.deck)
        and Counter(left.discard) == Counter(right.discard)
        and Counter(left.bench) == Counter(right.bench)
    )
