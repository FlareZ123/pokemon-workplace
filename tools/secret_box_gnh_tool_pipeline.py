"""Exact bounded Box-first Secret Box -> Guzma & Hala Tool acquisition.

Secret Box is already held; its cost is three cards. G&H may be played
afterward if a Supporter action remains. Every searched category has one
physical output slot. Expendable hand types may pay costs; P is protected.
The endpoint is acquired cards in hand, not subsequently attaching/playing.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product
from typing import Iterable

KINDS = ("D", "I", "A", "B", "G", "S", "E", "P")
D, I, A, B, G, S, E, P = range(len(KINDS))
State = tuple[int, ...]


def counts(**named: int) -> State:
    """Typed card quantities (D=fodder, I=Item, A/B=Tools, G=G&H, S=Stadium, E=Special Energy, P=protected)."""
    if set(named) - set(KINDS) or any(v < 0 for v in named.values()):
        raise ValueError("unknown or negative card count")
    return tuple(named.get(k, 0) for k in KINDS)


def _pay(hand: State, cost: int) -> Iterable[State]:
    """Enumerate physical payment subsets; P cannot be spent."""
    if sum(hand[:-1]) < cost:
        return
    for payment in product(*(range(min(hand[j], cost) + 1) for j in range(P))):
        if sum(payment) == cost:
            yield tuple(hand[j] - payment[j] if j < P else hand[j] for j in range(len(KINDS)))


def _fetch(hand: State, deck: State, choice: tuple[int, ...]) -> tuple[State, State]:
    new_hand, new_deck = list(hand), list(deck)
    for t in choice:
        new_hand[t] += 1
        new_deck[t] -= 1
    return tuple(new_hand), tuple(new_deck)


def _box_choices(deck: State) -> Iterable[tuple[int, ...]]:
    items = ((), (I,)) if deck[I] else ((),)
    tools = [()] + [(t,) for t in (A, B) if deck[t]]
    supporters = ((), (G,)) if deck[G] else ((),)
    stadiums = ((), (S,)) if deck[S] else ((),)
    for item, tool, supporter, stadium in product(items, tools, supporters, stadiums):
        yield item + tool + supporter + stadium


def _gnh_choices(deck: State, boost: bool) -> Iterable[tuple[int, ...]]:
    stadiums = ((), (S,)) if deck[S] else ((),)
    tools = [()] + ([(t,) for t in (A, B) if deck[t]] if boost else [])
    energies = ((), (E,)) if boost and deck[E] else ((),)
    for stadium, tool, energy in product(stadiums, tools, energies):
        yield stadium + tool + energy


def _goal(hand: State, keep_item: bool) -> bool:
    goals = (A, B, S, E, I) if keep_item else (A, B, S, E)
    return all(hand[t] for t in goals)


@lru_cache(maxsize=None)
def feasible(
    hand: State,
    deck: State,
    *,
    require_item: bool = False,
    supporter_available: bool = True,
) -> bool:
    """Existential legal Box-first sequence to both Tools, a Stadium, Special Energy.

    Box is implicit and held outside hand; modeled deck counts exclude Prizes.
    No opponent lock, other Trainer action, or intervening natural draw.
    """
    if len(hand) != len(KINDS) or len(deck) != len(KINDS) or min(hand + deck) < 0:
        raise ValueError("invalid count vectors")
    for after_box_payment in _pay(hand, 3):
        for picks in _box_choices(deck):
            box_hand, box_deck = _fetch(after_box_payment, deck, picks)
            if _goal(box_hand, require_item):
                return True
            if not supporter_available or not box_hand[G]:
                continue
            after_gnh = list(box_hand)
            after_gnh[G] -= 1
            after_gnh = tuple(after_gnh)
            for picks in _gnh_choices(box_deck, False):
                acquired, _ = _fetch(after_gnh, box_deck, picks)
                if _goal(acquired, require_item):
                    return True
            for after_payment in _pay(after_gnh, 2):
                for picks in _gnh_choices(box_deck, True):
                    acquired, _ = _fetch(after_payment, box_deck, picks)
                    if _goal(acquired, require_item):
                        return True
    return False


def minimum_fodder(
    *, item_copies: int, stadium_copies: int,
    require_item: bool = False, supporter_available: bool = True,
) -> int | None:
    """Canonical test: Box and one protected Basic in hand; A/B/G/E in deck."""
    deck = counts(I=item_copies, A=1, B=1, G=1, S=stadium_copies, E=1)
    for d in range(3, 9):
        if feasible(counts(D=d, P=1), deck, require_item=require_item,
                    supporter_available=supporter_available):
            return d
    return None
