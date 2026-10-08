"""Concrete Nest Ball Item-output bridge for Box -> G&H two-Tool acquisition.

For a narrow turn-state, the Box's Item output is a Nest Ball (I) that
can be played to put one Basic from deck directly onto Bench. That
consumes the Item, making it unavailable for subsequent G&H discard
payment. Both acquired Tools must have distinct eligible free holders.
"""
from __future__ import annotations

from functools import lru_cache

from secret_box_gnh_tool_pipeline import (
    KINDS, State, D, I, A, B, G, S, E, P,
    _pay, _box_choices, _fetch, _gnh_choices,
)


def _terminal(hand: State, holders: int, required_holders: int) -> bool:
    return (
        holders >= required_holders
        and all(hand[index] for index in (A, B, S, E))
    )


@lru_cache(maxsize=None)
def nest_ball_tool_bootstrap(
    hand: State, deck: State, *, initial_holders: int,
    searchable_basics: int, required_holders: int = 2,
    supporter_available: bool = True,
) -> bool:
    """Can Box-first searches acquire two Tools with distinct compatible holders?

    Box is already held outside the hand; all included physical card copies
    are in either known hand or searchable deck. Searchable Basics are a
    separate deck category which the Nest Ball can put directly on Bench.
    No Prize uncertainty, Item lock, Bench fullness or attached Tools.
    """
    if len(hand) != len(KINDS) or len(deck) != len(KINDS):
        raise ValueError("invalid typed card vector")
    if min(hand + deck) < 0 or min(initial_holders,searchable_basics,required_holders)<0:
        raise ValueError("invalid quantity")

    return any(
        continuation_after_box_payment(
            paid, deck, initial_holders=initial_holders,
            searchable_basics=searchable_basics,
            required_holders=required_holders,
            supporter_available=supporter_available,
        )
        for paid in _pay(hand, 3)
    )



@lru_cache(maxsize=None)
def continuation_after_box_payment(
    hand: State, deck: State, *, initial_holders: int,
    searchable_basics: int, required_holders: int = 2,
    supporter_available: bool = True,
) -> bool:
    """Optimize postpayment Box + Nest Ball + G&H with a known searchable deck."""
    for box_picks in _box_choices(deck):
        box_hand, rest = _fetch(hand, deck, box_picks)

        nest_actions = [(box_hand,initial_holders)]
        if (box_hand[I] > 0 and searchable_basics > 0
                and initial_holders < required_holders):
            after_nest = list(box_hand)
            after_nest[I] -= 1
            nest_actions.append((tuple(after_nest),initial_holders+1))

        for prepared, holders in nest_actions:
            if _terminal(prepared,holders,required_holders):
                return True
            if not supporter_available or not prepared[G]:
                continue
            played = list(prepared)
            played[G] -= 1
            after_supporter = tuple(played)
            for gnh_picks in _gnh_choices(rest, False):
                acquired,_ = _fetch(after_supporter, rest, gnh_picks)
                if _terminal(acquired,holders,required_holders):
                    return True
            for paid in _pay(after_supporter, 2):
                for gnh_picks in _gnh_choices(rest, True):
                    acquired,_ = _fetch(paid,rest,gnh_picks)
                    if _terminal(acquired,holders,required_holders):
                        return True
    return False


def minimum_starting_disposables(
    *, stadiums: int, item_available: bool, holders: int,
    searchable_basics: int,
) -> int | None:
    """Canonical one-G&H, two-Tool, one-Special-Energy test."""
    from secret_box_gnh_tool_pipeline import counts

    deck=counts(I=int(item_available),A=1,B=1,G=1,S=stadiums,E=1)
    for d in range(3,9):
        if nest_ball_tool_bootstrap(
            counts(D=d,P=1),deck,initial_holders=holders,
            searchable_basics=searchable_basics):
            return d
    return None
