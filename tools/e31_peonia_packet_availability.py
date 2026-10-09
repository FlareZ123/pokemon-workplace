"""Exact natural-draw access to the four-singleton E-31 Peonia packet.

A deck contains one each of Peonia, Greedy Dice, Dream Ball, Jirachi Prism
Star, B alternative Basic starters, and 56-B inert non-Basic cards.
Seven cards are drawn initially and one normal draw follows. No search,
additional draw, or card recovery is modeled. We require a non-Jirachi
Basic in the initial seven so Jirachi can remain in hand for Peonia.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class PacketRate:
    other_basics: int
    accepted_openings: Fraction
    unconditional_packet: Fraction
    conditioned_packet: Fraction


def probability_packet(other_basics: int) -> PacketRate:
    """Exact probability given a legal starting hand, including Jirachi.

    The legal-opening condition counts nine Basics when other_basics=8:
    the eight alternative starters plus the target Jirachi itself. In the
    event being measured, Jirachi must not be forced into the Active Spot.
    """
    if not 1 <= other_basics <= 56:
        raise ValueError("other_basics must be within 1..56")
    filler = 56 - other_basics

    accepted = Fraction(
        comb(60, 7) - comb(59 - other_basics, 7),
        comb(60, 7),
    )
    # Four distinguished singleton packet cards occur among the first eight.
    raw_packet = Fraction(comb(56, 4), comb(60, 8))

    # Independent exact derivation: count (unordered 7-card opener, 8th draw).
    # x=4 special packet cards in opener, or x=3 and one missing card is drawn.
    good_pairs = 0
    for basics in range(1, 4):
        if basics <= other_basics:
            good_pairs += (
                comb(other_basics, basics)
                * comb(filler, 3 - basics)
                * 53
            )
    for basics in range(1, 5):
        if basics <= other_basics:
            good_pairs += (
                4 * comb(other_basics, basics)
                * comb(filler, 4 - basics)
            )
    denominator = (
        comb(60, 7) - comb(59 - other_basics, 7)
    ) * 53
    enumerated = Fraction(good_pairs, denominator)

    # Different derivation: condition on the four distinguished cards
    # occupying uniformly one of the C(8,4) positions in first eight.
    # Exactly 3 or 4 non-packet slots lie in opening seven, each with
    # probability 1/2. At least one must contain an alternative Basic.
    def no_alternative_basic(sample: int) -> Fraction:
        if filler < sample:
            return Fraction(0)
        return Fraction(comb(filler, sample), comb(56, sample))

    success_given_packet = 1 - (
        no_alternative_basic(3) + no_alternative_basic(4)
    ) / 2
    conditioned = raw_packet * success_given_packet / accepted
    assert enumerated == conditioned

    return PacketRate(
        other_basics,
        accepted,
        raw_packet,
        conditioned,
    )


def main() -> None:
    expected = {
        4: Fraction(45608, 647586489),
        8: Fraction(310828, 3583221615),
        12: Fraction(153944, 1557792483),
        16: Fraction(1024560, 9380544359),
    }
    for basics, exact in expected.items():
        result = probability_packet(basics)
        assert result.conditioned_packet == exact
        print(
            f"other Basics={basics}: legal opening={float(result.accepted_openings):.8%}; "
            f"packet among 8 draws | legal start={float(exact):.8%}; "
            f"1 in {1/float(exact):,.0f}"
        )
    b8 = probability_packet(8)
    assert b8.unconditional_packet == Fraction(14, 97527)
    assert b8.conditioned_packet < b8.unconditional_packet
    print("Natural-draw Peonia packet: independent exact enumerations agree")


if __name__ == "__main__":
    main()
