"""Prize-belief updates from repeated Trainers' Mail misses.

This module isolates one singleton that is absent from the player's known hand.
The singleton is either among the face-down Prize cards or in the current deck.
A Trainers' Mail-style observation looks at a fixed number of deck cards and,
for the miss cases modeled here, does not reveal the singleton.

The observed cards are returned to the same-size shuffled deck after each miss.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class MailBelief:
    misses: int
    prize_probability: Fraction
    deck_probability: Fraction
    exact_information_value: Fraction


def posterior_after_misses(
    misses: int,
    *,
    prize_slots: int = 6,
    deck_cards: int = 46,
    look_size: int = 4,
) -> MailBelief:
    """Posterior for a missing singleton after repeated independent misses."""

    if misses < 0:
        raise ValueError("misses must be non-negative")
    if prize_slots < 0:
        raise ValueError("prize_slots must be non-negative")
    if deck_cards <= 0:
        raise ValueError("deck_cards must be positive")
    if not 0 <= look_size <= deck_cards:
        raise ValueError("look_size must be between zero and deck size")

    prize_weight = Fraction(prize_slots, 1)
    deck_weight = Fraction(deck_cards, 1)
    miss_given_deck = Fraction(deck_cards - look_size, deck_cards)

    deck_weight *= miss_given_deck**misses
    normalizer = prize_weight + deck_weight

    prize_probability = prize_weight / normalizer
    deck_probability = deck_weight / normalizer

    # In the stylized binary decision, G&H succeeds if the singleton is in the
    # deck and Gladion succeeds if it is Prized. Exact inspection allows the
    # correct Supporter to be selected in either state.
    exact_information_value = Fraction(1) - max(
        prize_probability,
        deck_probability,
    )

    return MailBelief(
        misses=misses,
        prize_probability=prize_probability,
        deck_probability=deck_probability,
        exact_information_value=exact_information_value,
    )


def first_gladion_preferred_miss(
    *,
    prize_slots: int = 6,
    deck_cards: int = 46,
    look_size: int = 4,
    max_misses: int = 1000,
) -> int | None:
    """Return the first miss count where Prize probability exceeds one half."""

    for misses in range(max_misses + 1):
        belief = posterior_after_misses(
            misses,
            prize_slots=prize_slots,
            deck_cards=deck_cards,
            look_size=look_size,
        )
        if belief.prize_probability > Fraction(1, 2):
            return misses
    return None
