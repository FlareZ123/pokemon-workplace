"""Exact maximal Ticket-top-five thinning uplift in natural Aichi held-spare states.

One synthetic Ticket replaces a non-Basic first-turn-neutral TechSlot.
After a Basic-valid opener and a natural draw, require Jirachi in opener,
natural G&H, exactly one TM and one Jet held, spare copies plus a
searchable Artazon and the Ticket in the deck. Assume G&H can be paid
with two strategically expendable hand cards, and Jirachi has an
unused legal Stellar Wish after G&H. The computed gain is an optimistic
upper bound for this specific direct Wish target-access channel.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb

from tools.aichi_held_spare_gnh_opportunity import exact as opportunity


def choose(n: int, k: int) -> int:
    return comb(n,k) if 0 <= k <= n else 0


@dataclass(frozen=True)
class TicketLift:
    opportunity_mass: Fraction
    ticket_searchable_mass: Fraction
    ticket_searchable_given_opportunity: Fraction
    conditional_access_gain: Fraction
    accepted_start_access_gain: Fraction


def exact(
    n: int = 60, opener: int = 7, prizes: int = 6,
    basics: int = 14, gnh: int = 4, artazon: int = 2,
    stellar_cards: int = 5,
) -> TicketLift:
    base = opportunity(n,opener,prizes,basics,gnh,artazon)
    residual = n-1-gnh-2-2-artazon-1
    if basics > residual+1:
        raise ValueError("Ticket must be separate from Basic starters")
    observed = opener
    unseen = n-1-observed
    initial_deck = unseen-prizes
    if not (1 <= stellar_cards <= initial_deck-3):
        raise ValueError("Not enough cards after three named searches")

    numerator = Fraction(0)
    for held_gnh in range(1,gnh+1):
        for held_artazon in range(artazon):
            filler_seen = observed-held_gnh-2-held_artazon
            visible_ways = (
                choose(gnh,held_gnh)*choose(2,1)**2*
                choose(artazon,held_artazon)*choose(residual,filler_seen)
            )
            art_left = artazon-held_artazon
            other_unseen = unseen-2-art_left-1
            prize_ways = sum(
                choose(art_left,j)*choose(other_unseen,prizes-j)
                for j in range(art_left)
            )
            numerator += (
                Fraction(opener,n)*Fraction(visible_ways,choose(n-1,observed))*
                Fraction(prize_ways,choose(unseen,prizes)) /
                base.accepted_probability
            )

    conditional_gain = (Fraction(stellar_cards,initial_deck-3)
                        - Fraction(stellar_cards,initial_deck-1))
    assert numerator <= base.probability
    return TicketLift(
        base.probability,
        numerator,
        numerator/base.probability if base.probability else Fraction(0),
        conditional_gain,
        numerator*conditional_gain,
    )
