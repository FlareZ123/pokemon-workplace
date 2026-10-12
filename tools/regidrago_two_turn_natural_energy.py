"""Exact natural two-attachment Energy source access for Regidrago VSTAR.

Apex Dragon costs Grass Grass Fire. Double Dragon Energy supplies any
two Energy types to a Dragon Pokémon. By own turn two, two attachments
pay this cost if the naturally seen cards include at least one Double
Dragon plus one Double Dragon/Grass/Fire Energy. The player must have
one of them by own turn one. Basic-valid seven-card starts are required.
Six uniform Prizes can be marginalized by exchangeability, because
only natural draws are considered, and no search or acceleration occurs.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class Exposure:
    accepted_opening: Fraction
    ready_given_valid_opening: Fraction
    ready_unconditional: Fraction


def calculate(
    deck_size: int, opening: int, starters: int,
    double_dragon: int, other_usable_energy: int,
) -> Exposure:
    if (deck_size <= opening+1 or opening < 1 or starters < 1
            or min(double_dragon, other_usable_energy) < 0
            or starters+double_dragon+other_usable_energy > deck_size):
        raise ValueError("Invalid card counts")

    others = deck_size-starters-double_dragon-other_usable_energy
    divisor = comb(deck_size, opening)
    accepted = ready = Fraction()
    for s in range(1,min(opening,starters)+1):
        for d in range(min(opening-s,double_dragon)+1):
            for e in range(min(opening-s-d,other_usable_energy)+1):
                filler = opening-s-d-e
                if filler > others:
                    continue
                weight = Fraction(
                    comb(starters,s)*comb(double_dragon,d)
                    *comb(other_usable_energy,e)*comb(others,filler),divisor)
                accepted += weight
                rest = [starters-s,double_dragon-d,
                        other_usable_energy-e,others-filler]
                for first,c in enumerate(rest):
                    if not c:
                        continue
                    p1 = Fraction(c,deck_size-opening)
                    rest[first] -= 1
                    for second,c2 in enumerate(rest):
                        if not c2:
                            continue
                        d_total=d+int(first==1)+int(second==1)
                        total=d_total+e+int(first==2)+int(second==2)
                        if d_total>=1 and total>=2:
                            ready += weight*p1*Fraction(c2,deck_size-opening-1)
                    rest[first] += 1
    return Exposure(accepted,ready/accepted,ready)
