"""Exact two-turn Beheeyem + Triple Acceleration Energy packet recycling.

The two Elgyem and anchor Basic are already established by T1 in a conditioned
board scenario. The six other T2 hand cards are uniformly drawn from the 57
non-board cards, six Prizes from the remainder, and T3 has one natural draw.
A T2 Mysterious Noise recycles its evolved stack (one Elgyem, one Beheeyem)
plus attached TAE into the deck before the T3 draw.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class PacketOutcomes:
    first_attack: Fraction
    two_attacks_recycled: Fraction
    two_attacks_discard_counterfactual: Fraction


def exact_packet_outcomes(beheeyem: int, tae: int) -> PacketOutcomes:
    """Exact conditioned packet probabilities for one first and second attack."""
    if not 1 <= beheeyem <= 4 or not 1 <= tae <= 4:
        raise ValueError("The benchmark models one to four copies of each card")

    # Original 60: three fixed ready board Basics + this 57-card pool.
    # Nine natural cards total by own T2, three of which were the board Basics.
    pool = 57
    hand_count = 6
    prizes = 6
    unseen_after_hand = pool - hand_count
    deck_before_attack = unseen_after_hand - prizes
    deck_after_recycle = deck_before_attack + 3
    filler = pool - beheeyem - tae
    first = recycled = discarded = Fraction(0)

    for b in range(min(beheeyem, hand_count) + 1):
        for t in range(min(tae, hand_count - b) + 1):
            rest = hand_count - b - t
            if rest > filler:
                continue
            weight = Fraction(
                comb(beheeyem, b) * comb(tae, t) * comb(filler, rest),
                comb(pool, hand_count),
            )
            if b < 1 or t < 1:
                continue

            first += weight
            if b >= 2 and t >= 2:
                # One more packet remains in hand after the T2 attack.
                p_recycled = p_discarded = Fraction(1)
            elif b >= 2:
                # T2 spends the hand's sole TAE. The recycled copy is a new
                # T3 out, alongside unprized copies remaining in the deck.
                unprized_other = Fraction(
                    (tae - t) * deck_before_attack, unseen_after_hand
                )
                p_recycled = (1 + unprized_other) / deck_after_recycle
                p_discarded = Fraction(tae - t, unseen_after_hand)
            elif t >= 2:
                # Symmetric case: T3 must naturally draw Beheeyem.
                unprized_other = Fraction(
                    (beheeyem - b) * deck_before_attack, unseen_after_hand
                )
                p_recycled = (1 + unprized_other) / deck_after_recycle
                p_discarded = Fraction(beheeyem - b, unseen_after_hand)
            else:
                # One consumed Beheeyem and one consumed TAE would both
                # need to be reacquired: one natural draw cannot do that.
                p_recycled = p_discarded = Fraction(0)
            recycled += weight * p_recycled
            discarded += weight * p_discarded

    return PacketOutcomes(first, recycled, discarded)
