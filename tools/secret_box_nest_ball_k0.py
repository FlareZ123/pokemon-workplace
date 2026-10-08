"""Pre-search hidden-Prize K0 policy with executable Nest Ball Basic bootstrap.

Models exactly when hidden Prizes contain the remaining eligible Basic
copies as well as Item/Tool/G&H/Stadium/Special Energy targets.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb

from secret_box_gnh_tool_pipeline import D,I,A,B,G,S,E,P,KINDS,State,_pay
from secret_box_k0_payment import (
    PaymentInformationResult,evaluate_hidden_prize_payment,
)
from secret_box_nest_ball_bootstrap import continuation_after_box_payment
from secret_box_k0_bench_bootstrap import counted_visible_hands


SEARCHABLE = (I,A,B,G,S,E)


@lru_cache(maxsize=None)
def exact_nest_payment_policy(
    visible_hand: State, unknown_cards: State, *,
    visible_basics: int, unknown_basics: int,
    prize_count: int = 6,
) -> PaymentInformationResult:
    """K0 vs K1 given observed holders and split hidden Basic/filler Prizes.

    No Box/Supporter lock; one Nest Ball Item may create one Bench holder.
    Box is in the known seven-card opener, omitted from counted hand.
    """
    if len(visible_hand)!=len(KINDS) or len(unknown_cards)!=len(KINDS):
        raise ValueError("typed deck/hand mismatch")
    if min(visible_hand+unknown_cards) < 0:
        raise ValueError("negative cards")
    if not 0 <= unknown_basics <= unknown_cards[P]:
        raise ValueError("unknown Basic count exceeds protected unseen pool")
    if visible_basics < 1:
        raise ValueError("expected an already started Basic")
    if not 0 <= prize_count <= sum(unknown_cards):
        raise ValueError("Prize count exceeds unknown pool")
    # With two holders already available, Nest Ball cannot improve this
    # acquisition endpoint; reuse the established six-category solver.
    if visible_basics >= 2:
        return evaluate_hidden_prize_payment(visible_hand,unknown_cards,
                                              prize_count=prize_count)

    payments=tuple(sorted(set(_pay(visible_hand,3))))
    if not payments:
        return PaymentInformationResult(Fraction(0),Fraction(0),(),0)
    opaque=unknown_cards[D]+unknown_cards[P]-unknown_basics
    denominator=comb(sum(unknown_cards),prize_count)
    wins=[0]*len(payments)
    clairvoyant=0
    total=0
    worlds=0

    for prize_targets in product(*(range(min(unknown_cards[t],prize_count)+1)
                                   for t in SEARCHABLE)):
        spent_targets=sum(prize_targets)
        if spent_targets>prize_count:
            continue
        target_weight=1
        for t,k in zip(SEARCHABLE,prize_targets):
            target_weight*=comb(unknown_cards[t],k)
        if not target_weight:
            continue

        remain_basics=prize_count-spent_targets
        for basic_prizes in range(max(0,remain_basics-opaque),
                                  min(unknown_basics,remain_basics)+1):
            weight=(target_weight * comb(unknown_basics,basic_prizes) *
                    comb(opaque,remain_basics-basic_prizes))
            if not weight:
                continue
            deck=[0]*len(KINDS)
            for t,k in zip(SEARCHABLE,prize_targets):
                deck[t]=unknown_cards[t]-k
            deck=tuple(deck)
            basics_after_prizes=unknown_basics-basic_prizes
            outcomes=[
                continuation_after_box_payment(
                    payment,deck,initial_holders=visible_basics,
                    searchable_basics=basics_after_prizes
                )
                for payment in payments
            ]
            for j,success in enumerate(outcomes):
                wins[j]+=weight*success
            clairvoyant+=weight*any(outcomes)
            total+=weight
            worlds+=1
    assert total==denominator,(total,denominator)
    best=max(wins)
    return PaymentInformationResult(
        clairvoyant_success=Fraction(clairvoyant,denominator),
        k0_success=Fraction(best,denominator),
        best_paid_hands=tuple(
            payment for payment,score in zip(payments,wins) if score==best
        ),
        prize_worlds=worlds,
    )


@dataclass(frozen=True)
class NestOpeningResult:
    k0_success: Fraction
    k1_success: Fraction
    visible_states: int
    one_holder_probability: Fraction
    incremental_k0_vs_two_visible: Fraction
    incremental_k1_vs_two_visible: Fraction

    @property
    def information_gap(self) -> Fraction:
        return self.k1_success - self.k0_success


def nest_ball_opening_mixture(
    deck_without_box: State, *, total_basic_starters: int = 12,
    prize_count: int = 6,
) -> NestOpeningResult:
    """Exact K0/K1 Box-first goal requiring 2 eligible holders, with Nest Ball."""
    from secret_box_k0_bench_bootstrap import holder_qualified_k0

    distribution, denominator = counted_visible_hands(
        deck_without_box, basics=total_basic_starters,
    )
    k0=k1=Fraction(0)
    single_mass=0
    for (hand, visible_basics),weight in distribution.items():
        if visible_basics == 1:
            single_mass+=weight
        unknown=tuple(total-held for total,held in zip(deck_without_box,hand))
        r=exact_nest_payment_policy(
            hand,unknown,visible_basics=visible_basics,
            unknown_basics=total_basic_starters-visible_basics,
            prize_count=prize_count,
        )
        k0+=weight*r.k0_success
        k1+=weight*r.clairvoyant_success

    strict=holder_qualified_k0(
        deck_without_box,basics=total_basic_starters,min_holders=2,
        prize_count=prize_count,
    )
    return NestOpeningResult(
        k0_success=k0/denominator,
        k1_success=k1/denominator,
        visible_states=len(distribution),
        one_holder_probability=Fraction(single_mass,denominator),
        incremental_k0_vs_two_visible=k0/denominator-strict.k0_joint_success,
        incremental_k1_vs_two_visible=k1/denominator-strict.k1_joint_success,
    )
