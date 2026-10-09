"""Exact natural initial-Prize event for Greedy Dice + Dream Ball + Jirachi.

The 60-card population contains one each G, D and J (J is Basic),
B other Basics, and 57-B inert non-Basics. An opening hand of seven
must contain a Basic to be accepted; six face-down Prizes are set.
The first supplied KO awards exactly two chosen Prize slots.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import comb


@dataclass(frozen=True)
class NaturalPrizeBurst:
    other_basics: int
    accepted_opening: Fraction
    event_before_opening_condition: Fraction
    event_given_accepted_opening: Fraction
    four_prize_burst_given_accepted_opening: Fraction


def analyze(other_basics: int) -> NaturalPrizeBurst:
    if not 1 <= other_basics <= 57:
        raise ValueError("other_basics outside 1..57")

    # Exactly G and D occupy the selected two face-down Prize positions,
    # in either order. J occupies one of the four other Prize slots.
    event = Fraction(2 * 4, 60 * 59 * 58)

    # Given that exact three-card Prize event, J is unavailable as an
    # opening Basic, so accepted hand needs one of the B other Basics.
    opening_given_event = 1 - Fraction(
        comb(57 - other_basics, 7),
        comb(57, 7),
    )
    accepted = 1 - Fraction(
        comb(59 - other_basics, 7),
        comb(60, 7),
    )
    event_given_opening = event * opening_given_event / accepted

    # Independent combinatorial count: choose opener of seven with at
    # least one other Basic from the 57 cards outside the three specified
    # physical Prize locations, and compare to all accepted opener hands.
    legal_other_openers = comb(57, 7) - comb(57 - other_basics, 7)
    all_openers_after_event = comb(57, 7)
    independently = event * Fraction(legal_other_openers, all_openers_after_event) / accepted
    assert event_given_opening == independently

    # Greedy heads (1/2) and player selects J's unknown physical
    # position uniformly from the four eligible remaining slots (1/4).
    # J then takes one more Prize through Wish Upon a Star, conditional
    # on an available Bench slot and applicable E-31 owner order.
    burst = event_given_opening / 8
    return NaturalPrizeBurst(
        other_basics,
        accepted,
        event,
        event_given_opening,
        burst,
    )


def main() -> None:
    expected_8 = Fraction(
        8, 60 * 59 * 58
    ) * Fraction(
        comb(57, 7) - comb(49, 7),
        comb(57, 7),
    ) / (
        1 - Fraction(comb(51, 7), comb(60, 7))
    )
    for basics in (4, 8, 12, 16):
        r = analyze(basics)
        assert r.event_before_opening_condition == Fraction(8, 60*59*58)
        assert r.four_prize_burst_given_accepted_opening * 8 == r.event_given_accepted_opening
        if basics == 8:
            assert r.event_given_accepted_opening == expected_8
        print(
            f"B={basics}: G,D awarded + J remaining | legal opener = "
            f"{float(r.event_given_accepted_opening):.9%}; "
            f"4-Prize burst | legal opener = "
            f"{float(r.four_prize_burst_given_accepted_opening):.9%}"
        )
    print("Natural six-Prize initial assignment: exact ratios verified")


if __name__ == "__main__":
    main()
