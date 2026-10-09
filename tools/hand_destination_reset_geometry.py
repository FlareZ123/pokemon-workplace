"""Exact one-step singleton exposure under full-hand redraw destinations.

The model is deliberately conditional on a legal redraw with a fixed draw count,
no intervention between old-hand disposition and drawing, and exchangeable deck
order. It does not infer legal action availability or full-game winning chances.
"""

from __future__ import annotations

from fractions import Fraction

DESTINATIONS = ("discard", "shuffle_into_deck", "bottom_deck")
TARGET_ZONES = ("deck", "retained_hand", "spent_hand")


def singleton_hit_probability(
    *, deck_size: int, hand_size: int, draw_count: int,
    hand_destination: str, target_zone: str, spent_hand_cards: int = 0,
) -> Fraction:
    """Probability the new draw contains a specific singleton.

    deck_size: deck cards before replacement (excluding old hand and source).
    hand_size: old hand BEFORE an optional pre-action consumes any hand cards.
    spent_hand_cards: hand cards moved outside the replacement by a pre-action.
    target_zone: deck, retained_hand, or spent_hand, AFTER the pre-action.

    The bottom_deck category places the randomized surviving old hand BELOW the
    previous deck, whose positions are exchangeable unless otherwise modeled.
    Draws are capped to remaining available cards for this one-step projection.
    """
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in (deck_size, hand_size, draw_count, spent_hand_cards)):
        raise TypeError("sizes and counts must be integers")
    if deck_size < 1 or hand_size < 0 or draw_count < 0 or not 0 <= spent_hand_cards <= hand_size:
        raise ValueError("invalid deck/hand/draw/spend sizes")
    if hand_destination not in DESTINATIONS or target_zone not in TARGET_ZONES:
        raise ValueError("unknown destination or target zone")
    surviving_hand = hand_size - spent_hand_cards
    if target_zone == "retained_hand" and surviving_hand < 1:
        raise ValueError("a retained-hand target requires at least one surviving hand card")
    if target_zone == "spent_hand" and spent_hand_cards < 1:
        raise ValueError("a spent-hand target requires at least one spent hand card")
    if target_zone == "spent_hand":
        return Fraction(0)
    if hand_destination == "shuffle_into_deck":
        total = deck_size + surviving_hand
        return Fraction(min(draw_count, total), total)
    if target_zone == "deck":
        return Fraction(min(draw_count, deck_size), deck_size)
    if hand_destination == "discard":
        return Fraction(0)
    # A bottom-deck target is not reached until the preexisting deck is exhausted.
    return Fraction(min(max(draw_count - deck_size, 0), surviving_hand), surviving_hand)


def pre_action_delta(*, deck_size: int, hand_size: int, draw_count: int,
                     hand_destination: str, target_initial_zone: str,
                     spent_hand_cards: int, spend_target: bool = False) -> Fraction:
    """Difference in target exposure: pre-action first minus reset immediately."""
    if target_initial_zone not in ("deck", "hand"):
        raise ValueError("target_initial_zone must be deck or hand")
    original_zone = "deck" if target_initial_zone == "deck" else "retained_hand"
    before = singleton_hit_probability(
        deck_size=deck_size, hand_size=hand_size, draw_count=draw_count,
        hand_destination=hand_destination, target_zone=original_zone,
    )
    after_zone = "spent_hand" if spend_target else original_zone
    after = singleton_hit_probability(
        deck_size=deck_size, hand_size=hand_size, draw_count=draw_count,
        hand_destination=hand_destination, target_zone=after_zone,
        spent_hand_cards=spent_hand_cards,
    )
    return after - before
