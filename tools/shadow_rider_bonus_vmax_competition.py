"""Exact paired first-bonus-draw gains and losses for a VMAX deck-search goal.

A second observed card can improve the held search resources but may remove
one of the final two deck-resident Shadow Rider Calyrex VMAX targets.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from tools.shadow_rider_dual_entry_launch import ShadowRiderDualEntry
from tools.shadow_rider_stone_dual_entry import ShadowRiderStoneDualEntry


@dataclass(frozen=True)
class BonusDrawOutcome:
    before: Fraction
    after: Fraction
    gain: Fraction
    loss: Fraction

    @property
    def net(self) -> Fraction:
        return self.after-self.before


def transition(model:ShadowRiderDualEntry, *, stone:bool,
               payment:str='energy', bonus_before:int=0,
               v_hosts:int=3)->BonusDrawOutcome:
    """Coupled outcome when one bonus card is inserted before natural draw.

    The before-hand and after-hand use the same initial seven, Prize cards,
    and card order. They differ by exposing precisely the second card after
    Prizes. Search feasibility is upward-closed in held cards except when
    the extra drawn VMAX depletes the final two deck targets.
    """
    if model.required_vmax!=2:
        raise ValueError('two in-deck VMAX targets required')
    deck_left=model.deck_size-model.opening_size-model.prizes-1-bonus_before
    if deck_left<=0:
        raise ValueError('bonus draw exceeds deck')

    def p(number:int,needed:int)->Fraction:
        line=ShadowRiderDualEntry(
            deck_size=model.deck_size, opening_size=model.opening_size,
            prizes=model.prizes, other_basics=model.other_basics,
            lele=model.lele, vmax=model.vmax, treasure=model.treasure,
            quick_ball=model.quick_ball, heavy_ball=model.heavy_ball,
            energy=model.energy, required_vmax=needed,
        )
        if stone:
            return sum(ShadowRiderStoneDualEntry(base=line,v_hosts=v_hosts)
                       .probability(number,payment=payment))
        return line.probability(number,payment=payment)

    before=p(bonus_before,2)
    after=p(bonus_before+1,2)
    at_least_three=p(bonus_before,3)
    exactly_two=before-at_least_three
    loss=exactly_two*Fraction(2,deck_left)
    gain=after-before+loss
    assert gain>=0 and loss>=0
    return BonusDrawOutcome(before,after,gain,loss)
