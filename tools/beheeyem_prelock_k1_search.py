"""Exact paid Ultra Ball full-deck-search feasibility before Beheeyem Item lock.

Opponent deck is an illustrative 60-card physical partition: Basics12,
Ultra Ball U4, neutral disposable F32 and other12 (Ace4/Judge4/X4).
A valid seven-card Basic opener is required; six original Prize cards
are set, then k_pre draws and s_pre random Prize awards enter hand.
An Ultra Ball can search the deck and grant K1 information if held and
if two *other* neutral filler cards can pay its discard cost. Assume
the player uses it before Mysterious Noise locks Item plays.

The engine computes state supply, not the strategic benefit of actually
spending the Item, its search output or the conditional Prize information.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import comb

from beheeyem_physical_tutor import choose


@lru_cache(maxsize=None)
def search_window_probabilities(
    prelock_draws: int,prizes_earned_prelock: int=0,
    basics: int=12,ultra_balls: int=4,disposable: int=32
) -> dict[str,Fraction]:
    """Conditional probabilities of held U, payable U and unpayable U."""
    if not (0 <= prelock_draws <= 47 and
            0 <= prizes_earned_prelock <= 6 and
            0 <= basics <= 60 and 0 <= ultra_balls <= 4 and
            basics+ultra_balls <= 60 and
            0 <= disposable <= 60-basics-ultra_balls):
        raise ValueError("Invalid categories or draw window")
    h=7+prelock_draws+prizes_earned_prelock
    if h>60:
        raise ValueError("Physical sample exceeds deck size")
    other=60-basics-ultra_balls-disposable
    valid7=comb(60,7)-choose(60-basics,7)
    if not valid7:
        raise ValueError("No valid Basic opening")
    denominator=comb(60,h)*comb(h,7)*valid7
    visible=payable=unpayable=Fraction()
    total=Fraction()
    for b in range(min(basics,h)+1):
        opener_valid=comb(h,7)-choose(h-b,7)
        if not opener_valid:
            continue
        for u in range(min(ultra_balls,h-b)+1):
            for f in range(min(disposable,h-b-u)+1):
                o=h-b-u-f
                ways=(choose(basics,b)*choose(ultra_balls,u)*
                      choose(disposable,f)*choose(other,o))
                if not ways:
                    continue
                w=Fraction(ways*opener_valid*comb(60,7),denominator)
                total+=w
                if u:
                    visible+=w
                    if f>=2:
                        payable+=w
                    else:
                        unpayable+=w
    assert total==1
    assert visible==payable+unpayable
    return {
        "seen_U":visible,
        "paid_search_feasible":payable,
        "seen_but_cannot_pay":unpayable
    }


@lru_cache(maxsize=None)
def missed_under_item_lock(
    before_draws: int,locked_draws: int,earned_prelock: int=0
) -> dict[str,Fraction]:
    """Counterfactual postlock supply minus K1 usable before lock.

    Assumes no intervening card spending or return/retrieval, so categories
    accumulate monotonically but postlock Ultra Ball cannot be played.
    """
    if before_draws+locked_draws>47:
        raise ValueError("Drawing too many distinct cards")
    before=search_window_probabilities(before_draws,earned_prelock)
    after=search_window_probabilities(
        before_draws+locked_draws,earned_prelock
    )
    return {
        "K1_before_lock":before["paid_search_feasible"],
        "K1_if_items_remained_playable":after["paid_search_feasible"],
        "extra_supply_denied_by_lock":(
            after["paid_search_feasible"]-before["paid_search_feasible"]
        ),
        "unpayable_early_U":before["seen_but_cannot_pay"]
    }
