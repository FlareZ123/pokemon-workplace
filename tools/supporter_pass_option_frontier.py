"""Endogenous Supporter cancellation in the K0/K1 own/opponent projection."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from action_information_weight_frontier import (
    LinearFrontier, evaluate_linear_choice, exact_linear_frontier,
)
from multi_action_information_envelope import ActionEnvelope
from prize_three_supporter_choice import ThreeSupporterResult, three_supporter_choice
from supporter_opponent_tradeoff_frontier import OpponentReadiness, opponent_next_draw_readiness


@dataclass(frozen=True)
class PassSupporterModel:
    own: ThreeSupporterResult
    opponent: OpponentReadiness
    states: tuple[tuple[Fraction,dict[str,tuple[Fraction,Fraction]]],...]

    def evaluate(self, weight: Fraction) -> ActionEnvelope:
        return evaluate_linear_choice(self.states,weight)

    def frontier(self) -> LinearFrontier:
        return exact_linear_frontier(self.states)


def build_pass_option_model(
    *, own_deck_size:int, own_prizes_hidden:int, own_unknown_outs:int,
    own_hand_size:int, own_hand_outs:int,
    opponent_deck_size:int, opponent_prizes_hidden:int,
    opponent_unknown_outs:int, opponent_hand_size:int, opponent_hand_outs:int,
) -> PassSupporterModel:
    """Include a no-Supporter option with the old target still held in hand.

    For each Supporter, own payoff is new-hand out access. For Pass, it is
    known old-hand out readiness. Opponent readiness is after their next
    ordinary draw. Pass leaves their old hand unchanged, as Research does.
    This evaluates terminal access at a common snapshot; effects of any
    other actions on either turn are excluded.
    """
    own=three_supporter_choice(
        deck_size=own_deck_size,prizes_hidden=own_prizes_hidden,
        unknown_outs=own_unknown_outs,hand_size=own_hand_size,
        hand_outs=own_hand_outs,prize_draw_count=own_prizes_hidden,
        opponent_hand_size=opponent_hand_size)
    opponent=opponent_next_draw_readiness(
        deck_size=opponent_deck_size,prizes_hidden=opponent_prizes_hidden,
        unknown_outs=opponent_unknown_outs,hand_size=opponent_hand_size,
        hand_outs=opponent_hand_outs)
    q=opponent.as_tuple()
    hold=Fraction(int(own_hand_outs>0))
    states=tuple((p,{
        "Iono":(i,q[0]),
        "N":(n,q[1]),
        "Professor's Research":(r,q[2]),
        "Pass":(hold,q[2]),
    }) for _,p,i,n,r in own.rows)
    return PassSupporterModel(own,opponent,states)
