"""Exact optional paid-source marginal opportunity-cost frontier by legal hand.

An exogenous scalar cost tau is charged only when Quick Ball is chosen.
The source candidate is legal only when both physical Q and disposable F
appear in the observed hand. Pay its two-card cost before observing K.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from multi_action_information_envelope import action_information_envelope
from physical_quick_ball_search_option import (
    action_rows,physical_hands_with_quick_ball,
)


@dataclass(frozen=True)
class SourceCostFrontier:
    weight: Fraction
    source_payable: Fraction
    positive_thresholds: tuple[tuple[Fraction,Fraction],...]
    zero_cost_gain: Fraction
    zero_cost_use_probability: Fraction
    maximum_willingness_to_pay: Fraction
    negative_hand_count: int

    def evaluate(self, extra_cost:Fraction) -> tuple[Fraction,Fraction]:
        """(optimal gain vs never searching, optimal search probability).

        At exact equality delta == extra_cost, choose not to search.
        Every state already incorporates physically consumed Quick Ball + F.
        """
        tau=Fraction(extra_cost)
        if tau<0:raise ValueError('extra source cost must be nonnegative')
        gain=sum((p*(b-tau) for b,p in self.positive_thresholds if b>tau),Fraction())
        selection=sum((p for b,p in self.positive_thresholds if b>tau),Fraction())
        return gain,selection


def quick_ball_cost_frontier(
    *,counts:tuple[int,...]=(12,4,4,4,4,28,4),
    opening_size:int=7,prize_count:int=6,
    opponent_penalties:tuple[Fraction,...],weight:Fraction,
)->SourceCostFrontier:
    """Enumerate each hand's postpayment informed benefit vs prepayment K0.

    Extra cost tau is hypothetical loss of future Quick Ball/filler utility,
    distinct from their already modeled immediate zone transitions. This
    permits transparent sensitivity without inventing future game payoffs.
    """
    weight=Fraction(weight)
    q=tuple(Fraction(v) for v in opponent_penalties)
    if weight<0 or len(q)!=4 or any(not 0<=x<=1 for x in q):
        raise ValueError('invalid opponent readiness or weight')
    _,hands=physical_hands_with_quick_ball(counts,opening_size=opening_size,
                                          prize_count=prize_count)
    d=sum(counts)-opening_size-prize_count-1
    if d<1:raise ValueError('empty old deck')
    buckets:dict[Fraction,Fraction]={}
    payable=Fraction()
    negative=0
    for hand,p in hands.items():
        if not (hand[5] and hand[6]):continue
        payable+=p
        kw=dict(hand=hand,deck_size=d,prizes=prize_count,
                unknown_outs=counts[4]-hand[4],
                opponent_penalties=q,weight=weight)
        baseline=action_information_envelope(action_rows(source_paid=False,**kw))
        paid=action_information_envelope(action_rows(source_paid=True,**kw))
        benefit=paid.observed_value-baseline.best_fixed_value
        if benefit>0:
            buckets[benefit]=buckets.get(benefit,Fraction())+p
        elif benefit<0:
            negative+=1
    buckets_tuple=tuple(sorted(buckets.items()))
    zero_gain=sum((gain*p for gain,p in buckets_tuple),Fraction())
    zero_mass=sum((p for _,p in buckets_tuple),Fraction())
    frontier=SourceCostFrontier(weight,payable,buckets_tuple,zero_gain,zero_mass,
                                buckets_tuple[-1][0] if buckets_tuple else Fraction(),negative)
    assert frontier.evaluate(0)==(zero_gain,zero_mass)
    return frontier
