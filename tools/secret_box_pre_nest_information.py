"""Optional prior Nest Ball deck search: information timing vs Item consumption.

Compare:
  Box-first: commit Secret Box's discard while Prize configuration is K0;
             Box search then reveals the deck.
  Nest-first: spend already-held Nest Ball on a Basic (when searchable),
              reveal the deck, then select Box's cost with K1 knowledge.

The prior Nest Ball cannot also pay Box/Guzma & Hala. Both branches have
identical terminal requirements: A+B+S+E acquired, two Basic holders.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb

from secret_box_gnh_tool_pipeline import (
    State,KINDS,D,I,A,B,G,S,E,P,_pay,
)
from secret_box_nest_ball_bootstrap import continuation_after_box_payment
from secret_box_nest_ball_k0 import exact_nest_payment_policy


KEYS=(I,A,B,G,S,E)


@dataclass(frozen=True)
class PriorNestChoice:
    box_first_k0: Fraction
    nest_first_k0: Fraction
    optimal_first_action_success: Fraction
    informational_upper_bound: Fraction
    world_count: int

    @property
    def gain_from_nest_first(self) -> Fraction:
        return self.optimal_first_action_success-self.box_first_k0

    @property
    def remaining_information_gap(self) -> Fraction:
        return self.informational_upper_bound-self.optimal_first_action_success


@lru_cache(maxsize=None)
def optimal_pre_nest_choice(
    hand: State, unknown: State, *,
    visible_basics: int, unseen_basics: int, prizes: int = 6,
) -> PriorNestChoice:
    """Exact one-choice K0 game with optional Nest Ball-first inspection."""
    if len(hand)!=len(KINDS) or len(unknown)!=len(KINDS):
        raise ValueError("typed hand/deck mismatch")
    if min(hand+unknown)<0 or not 0<=unseen_basics<=unknown[P]:
        raise ValueError("invalid counts")
    if visible_basics<1 or prizes<0 or prizes>sum(unknown):
        raise ValueError("invalid setup/Prize condition")

    first=exact_nest_payment_policy(
        hand,unknown,visible_basics=visible_basics,
        unknown_basics=unseen_basics,prize_count=prizes
    )
    if hand[I]<=0 or visible_basics>=2:
        return PriorNestChoice(
            first.k0_success,Fraction(0),first.k0_success,
            first.clairvoyant_success,0
        )

    hand_after=list(hand)
    hand_after[I]-=1
    after_item=tuple(hand_after)
    post_item_payments=tuple(sorted(set(_pay(after_item,3))))
    if not post_item_payments:
        return PriorNestChoice(
            first.k0_success,Fraction(0),first.k0_success,
            first.clairvoyant_success,0
        )

    starting_box_payments=tuple(sorted(set(_pay(hand,3))))
    if not starting_box_payments:
        raise AssertionError("pre-Nest Box payment should have greater availability")
    unimportant=unknown[D]+unknown[P]-unseen_basics
    denominator=comb(sum(unknown),prizes)
    total=0
    nest_success=0
    omniscient_success=0
    worlds=0

    for key_prizes in product(*(range(min(unknown[t],prizes)+1) for t in KEYS)):
        remaining_prizes=prizes-sum(key_prizes)
        if remaining_prizes<0:
            continue
        factor=1
        for t,k in zip(KEYS,key_prizes):
            factor*=comb(unknown[t],k)
        if not factor:
            continue
        for basic_prized in range(max(0,remaining_prizes-unimportant),
                                  min(unseen_basics,remaining_prizes)+1):
            weight=(
                factor*comb(unseen_basics,basic_prized)*
                comb(unimportant,remaining_prizes-basic_prized)
            )
            if not weight:
                continue
            pool=[0]*len(KINDS)
            for t,k in zip(KEYS,key_prizes):
                pool[t]=unknown[t]-k
            pool=tuple(pool)
            available_basics=unseen_basics-basic_prized

            # Nest-first consumes held Item; playing it inspects full deck.
            # It adds a holder iff an eligible Basic is actually searchable.
            nest_route=(
                available_basics>0 and any(
                    continuation_after_box_payment(
                        paid,pool,initial_holders=visible_basics+1,
                        searchable_basics=available_basics-1
                    )
                    for paid in post_item_payments
                )
            )
            # The omniscient upper bound chooses the action and Box
            # payment after seeing this Prize world.
            box_world=any(
                continuation_after_box_payment(
                    paid,pool,initial_holders=visible_basics,
                    searchable_basics=available_basics
                )
                for paid in starting_box_payments
            )
            nest_success+=weight*bool(nest_route)
            omniscient_success+=weight*(nest_route or box_world)
            total+=weight
            worlds+=1

    assert total==denominator,(total,denominator)
    nest_probability=Fraction(nest_success,denominator)
    option=max(first.k0_success,nest_probability)
    upper=Fraction(omniscient_success,denominator)
    assert upper>=option
    return PriorNestChoice(
        box_first_k0=first.k0_success,
        nest_first_k0=nest_probability,
        optimal_first_action_success=option,
        informational_upper_bound=upper,
        world_count=worlds,
    )
