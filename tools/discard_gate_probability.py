"""Exact opening-hand probabilities for discard-gated cards.

The model partitions a deck into three disjoint classes:

* copies of the action card;
* cards currently acceptable to discard; and
* all remaining cards.

It answers a deliberately narrow question: if hand_size cards are sampled
without replacement, how often is at least one copy of the action present and
the hand contains enough acceptable discard fodder to pay its cost?

This is a compositional stress test, not a complete Pokemon TCG turn simulator.
"""

from __future__ import annotations

from math import comb


def _validate(
    deck_size: int,
    action_copies: int,
    disposable_copies: int,
    hand_size: int,
    discard_cost: int,
) -> None:
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= action_copies <= deck_size:
        raise ValueError("action_copies must be between 0 and deck_size")
    if not 0 <= disposable_copies <= deck_size - action_copies:
        raise ValueError("disposable_copies must fit outside action_copies")
    if not 0 <= hand_size <= deck_size:
        raise ValueError("hand_size must be between 0 and deck_size")
    if discard_cost < 0:
        raise ValueError("discard_cost must be non-negative")


def present_probability(deck_size: int, action_copies: int, hand_size: int) -> float:
    """Return P(at least one action copy is in the sampled hand)."""
    _validate(deck_size, action_copies, 0, hand_size, 0)
    if action_copies == 0 or hand_size == 0:
        return 0.0
    return 1.0 - comb(deck_size - action_copies, hand_size) / comb(deck_size, hand_size)


def playable_probability(
    deck_size: int,
    action_copies: int,
    disposable_copies: int,
    hand_size: int,
    discard_cost: int,
    *,
    spare_actions_disposable: bool = False,
) -> float:
    """Return the exact probability that the discard-gated action is playable.

    disposable_copies is the number of non-action cards that are acceptable
    discard targets in the modeled state. When spare_actions_disposable is
    true, every action copy beyond the one being played also counts as fodder.
    """
    _validate(deck_size, action_copies, disposable_copies, hand_size, discard_cost)
    if action_copies == 0 or hand_size == 0:
        return 0.0

    protected_copies = deck_size - action_copies - disposable_copies
    denominator = comb(deck_size, hand_size)
    favorable = 0

    for actions_in_hand in range(1, min(action_copies, hand_size) + 1):
        max_disposable = min(disposable_copies, hand_size - actions_in_hand)
        for disposable_in_hand in range(max_disposable + 1):
            protected_in_hand = hand_size - actions_in_hand - disposable_in_hand
            if protected_in_hand < 0 or protected_in_hand > protected_copies:
                continue

            available_fodder = disposable_in_hand
            if spare_actions_disposable:
                available_fodder += actions_in_hand - 1
            if available_fodder < discard_cost:
                continue

            favorable += (
                comb(action_copies, actions_in_hand)
                * comb(disposable_copies, disposable_in_hand)
                * comb(protected_copies, protected_in_hand)
            )

    return favorable / denominator


def conditional_payability(
    deck_size: int,
    action_copies: int,
    disposable_copies: int,
    hand_size: int,
    discard_cost: int,
    *,
    spare_actions_disposable: bool = False,
) -> float:
    """Return P(playable | at least one action copy is present)."""
    present = present_probability(deck_size, action_copies, hand_size)
    if present == 0.0:
        return 0.0
    return playable_probability(
        deck_size,
        action_copies,
        disposable_copies,
        hand_size,
        discard_cost,
        spare_actions_disposable=spare_actions_disposable,
    ) / present


def minimum_disposable_for_threshold(
    deck_size: int,
    action_copies: int,
    hand_size: int,
    discard_cost: int,
    threshold: float,
    *,
    spare_actions_disposable: bool = False,
) -> int | None:
    """Find the smallest disposable pool meeting a conditional threshold."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    _validate(deck_size, action_copies, 0, hand_size, discard_cost)

    for disposable_copies in range(deck_size - action_copies + 1):
        if conditional_payability(
            deck_size,
            action_copies,
            disposable_copies,
            hand_size,
            discard_cost,
            spare_actions_disposable=spare_actions_disposable,
        ) >= threshold:
            return disposable_copies
    return None
