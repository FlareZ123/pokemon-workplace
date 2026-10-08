"""Exact accepted-opening sequencing value as Nest Ball redundancy changes.

Keep a physical 60-card illustrative composition and twelve protected
eligible Basic starters. Vary copies of Nest Ball (the Box Item output)
and disposable filler in exchange for protected nonstarter cards.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from secret_box_gnh_tool_pipeline import counts
from secret_box_pre_nest_opening_mix import pre_nest_opening_mixture


@dataclass(frozen=True)
class NestDensityRow:
    disposable_copies: int
    nest_ball_copies: int
    box_first: Fraction
    choose_order: Fraction
    clairvoyant_upper: Fraction
    eligible_hand_mass: Fraction
    advantage_hand_mass: Fraction
    advantage_state_count: int

    @property
    def advantage(self) -> Fraction:
        return self.choose_order-self.box_first


def scan_nest_density(
    configurations: tuple[tuple[int,int],...]=(
        (10,1),(10,2),(10,3),
        (20,1),(20,2),(20,3),(20,4),
        (30,2),
    )
) -> tuple[NestDensityRow,...]:
    out=[]
    for disposable,items in configurations:
        protected=51-disposable-items
        if items<1 or disposable<0 or protected<12:
            raise ValueError("invalid 60-card composition")
        typed=counts(
            D=disposable,I=items,A=2,B=1,G=2,S=2,E=1,
            P=protected
        )
        assert 1+sum(typed)==60
        result=pre_nest_opening_mixture(
            typed,total_basic_starters=12,prize_count=6
        )
        out.append(NestDensityRow(
            disposable,items,
            result.box_first_k0,result.best_order_k0,
            result.clairvoyant_upper,result.pre_nest_eligible_hand_mass,
            result.improvement_hand_mass,result.improvement_state_count,
        ))
    return tuple(out)
