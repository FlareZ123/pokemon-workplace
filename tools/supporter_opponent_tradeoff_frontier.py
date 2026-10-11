"""Exact tradeoff between own redraw access and opponent's next-draw readiness.

The opponent's unseen Prize composition is marginalized before the player
chooses. Observing one's own K1 deck composition never observes their Prizes.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb

from hand_return_payment_frontier import hit_probability
from multi_action_information_envelope import ActionEnvelope, action_information_envelope
from prize_three_supporter_choice import ThreeSupporterResult, three_supporter_choice

ACTIONS = ("Iono", "N", "Professor's Research")


@dataclass(frozen=True)
class OpponentReadiness:
    iono: Fraction
    n: Fraction
    research: Fraction

    def as_tuple(self) -> tuple[Fraction, Fraction, Fraction]:
        return self.iono, self.n, self.research


@dataclass(frozen=True)
class WeightedSupporter:
    weight: Fraction
    payoff: ActionEnvelope
    own: ThreeSupporterResult
    opponent: OpponentReadiness


@dataclass(frozen=True)
class ExactFrontier:
    candidates: tuple[Fraction, ...]
    peak_weight: Fraction
    peak_value: Fraction
    peak_policy: tuple[str, ...]


def opponent_next_draw_readiness(
    *, deck_size: int, prizes_hidden: int, unknown_outs: int,
    hand_size: int, hand_outs: int,
) -> OpponentReadiness:
    """At least one specified out at the opponent's next turn's start.

    Opponent presently has prizes_hidden remaining Prizes, of which all are
    unseen; the next turn draws one additional card after Iono/N redraws of
    prizes_hidden. If we use Research, their old hand is retained and they
    draw only the normal next-turn card. Ignore other opponent actions.
    """
    values=(deck_size,prizes_hidden,unknown_outs,hand_size,hand_outs)
    if any(type(x) is not int for x in values):
        raise TypeError("counts must be integers")
    if (not 1<=prizes_hidden<=6 or deck_size<=prizes_hidden
            or not 0<=unknown_outs<=deck_size+prizes_hidden
            or not 0<=hand_outs<=hand_size):
        raise ValueError("invalid next-draw model or insufficient original deck")
    probabilities=[]
    for k in range(max(0,unknown_outs-prizes_hidden),min(deck_size,unknown_outs)+1):
        p=Fraction(comb(deck_size,k)*comb(prizes_hidden,unknown_outs-k),
                   comb(deck_size+prizes_hidden,unknown_outs))
        m=prizes_hidden+1
        iono=hit_probability(deck_size,k,m)
        n=hit_probability(deck_size+hand_size,k+hand_outs,m)
        research=Fraction(1) if hand_outs else hit_probability(deck_size,k,1)
        probabilities.append((p,iono,n,research))
    return OpponentReadiness(*(
        sum((r[0]*r[i] for r in probabilities),Fraction()) for i in (1,2,3)
    ))


def weighted_supporter_choice(
    *, weight: Fraction, opponent: OpponentReadiness,
    own: ThreeSupporterResult,
) -> WeightedSupporter:
    """Own immediate out hit minus weight * opponent next-turn readiness.

    Opponent hidden Prize count is averaged in OpponentReadiness; do not
    reveal it when optimizing across our own observable hidden K states.
    """
    weight=Fraction(weight)
    if weight<0:
        raise ValueError("disruption weight must be nonnegative")
    q=opponent.as_tuple()
    payoff=action_information_envelope((p, {
        a: self_out-weight*opponent_out
        for a,self_out,opponent_out in zip(ACTIONS,(i,n,r),q)
    }) for _,p,i,n,r in own.rows)
    return WeightedSupporter(weight,payoff,own,opponent)


def candidate_weight_frontier(
    *, opponent: OpponentReadiness, own: ThreeSupporterResult,
) -> ExactFrontier:
    """Exact nonnegative decision-line intersections and true peak V.

    Each observation-conditioned payoff and each prior-fixed mean is affine
    in weight, so V is continuous and piecewise affine. Every change of
    maximizing action must be at an enumerated pairwise intersection;
    therefore the maximum over the nonnegative axis occurs at a candidate.
    If there are no candidate crossings, V is constant on that axis.
    """
    q=opponent.as_tuple()
    rows=own.rows
    mean=tuple(sum((p*pay[i] for _,p,*pay in rows),Fraction()) for i in range(3))
    pairwise=set([Fraction(0)])
    for payoff in [mean]+[tuple(row[2:]) for row in rows]:
        for i,j in combinations(range(3),2):
            dq=q[i]-q[j]
            if dq:
                t=Fraction(payoff[i]-payoff[j],dq)
                if t>=0:
                    pairwise.add(t)
    thresholds=tuple(sorted(pairwise))
    choices=[weighted_supporter_choice(weight=t,opponent=opponent,own=own)
             for t in thresholds]
    peak=max(c.payoff.information_value for c in choices)
    first=next(c for c in choices if c.payoff.information_value==peak)
    return ExactFrontier(thresholds,first.weight,peak,
                         first.payoff.optimal_after_observation)
