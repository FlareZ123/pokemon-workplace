"""Accepted-opening mixture for optional pre-Box Nest Ball Prize inspection.

Retains the same 60-card Box-conditional, valid Basic opening and one
natural draw as the preceding Nest Ball Tool-holder policy. A held
Nest Ball may be played before Box, with its payment and Basic holder
effect accounted for. First-action choice is made before observing
hidden Prizes.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from secret_box_gnh_tool_pipeline import State,I,D
from secret_box_k0_bench_bootstrap import counted_visible_hands
from secret_box_nest_ball_k0 import exact_nest_payment_policy
from secret_box_pre_nest_information import optimal_pre_nest_choice


@dataclass(frozen=True)
class PreNestOpeningMix:
    box_first_k0: Fraction
    best_order_k0: Fraction
    clairvoyant_upper: Fraction
    pre_nest_eligible_hand_mass: Fraction
    improvement_hand_mass: Fraction
    improvement_state_count: int
    considered_state_count: int

    @property
    def sequencing_gain(self) -> Fraction:
        return self.best_order_k0-self.box_first_k0

    @property
    def residual_information_gap(self) -> Fraction:
        return self.clairvoyant_upper-self.best_order_k0


def pre_nest_opening_mixture(
    deck_without_box: State, *, total_basic_starters: int = 12,
    prize_count: int = 6,
) -> PreNestOpeningMix:
    """Exact opening-weighted utility of choosing Nest Ball before Box."""
    weighted,denominator=counted_visible_hands(
        deck_without_box,basics=total_basic_starters
    )
    total_box=total_best=total_k1=Fraction(0)
    eligible=improved=0
    improved_states=0

    for (hand,basics),weight in weighted.items():
        unseen=tuple(deck-hand_card for deck,hand_card
                     in zip(deck_without_box,hand))
        unknown_basics=total_basic_starters-basics
        box=exact_nest_payment_policy(
            hand,unseen,visible_basics=basics,
            unknown_basics=unknown_basics,prize_count=prize_count
        )
        best=box.k0_success
        if basics==1 and hand[I]>0:
            eligible+=weight
            choice=optimal_pre_nest_choice(
                hand,unseen,visible_basics=basics,
                unseen_basics=unknown_basics,prizes=prize_count
            )
            assert choice.box_first_k0==box.k0_success
            assert choice.informational_upper_bound==box.clairvoyant_success
            best=choice.optimal_first_action_success
            if best>box.k0_success:
                improved+=weight
                improved_states+=1
                # With 3 inert disposable cards in hand there is a
                # universally dominating Box payment, so an earlier
                # inspection cannot improve this restricted endpoint.
                assert hand[D]<3

        total_box+=weight*box.k0_success
        total_best+=weight*best
        total_k1+=weight*box.clairvoyant_success

    result=PreNestOpeningMix(
        box_first_k0=total_box/denominator,
        best_order_k0=total_best/denominator,
        clairvoyant_upper=total_k1/denominator,
        pre_nest_eligible_hand_mass=Fraction(eligible,denominator),
        improvement_hand_mass=Fraction(improved,denominator),
        improvement_state_count=improved_states,
        considered_state_count=len(weighted),
    )
    assert (result.box_first_k0<=result.best_order_k0<=
            result.clairvoyant_upper)
    return result
