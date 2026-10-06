"""Exact pre-search Prize belief updates from visible non-Prize cards.

Before the player has searched the deck, the exact Prize identities are unknown.
The uncertainty is still conditioned by cards already known to be outside the
Prize cards, such as the accepted opening hand and subsequent ordinary draws.

Given only those observations and no additional deck-order information, the
Prize cards are uniformly distributed among the remaining unseen card
identities. This module exposes the resulting hypergeometric belief state.
"""

from __future__ import annotations

from math import comb


def _validate(
    deck_size: int,
    prize_count: int,
    visible_nonprize_cards: int,
    group_copies: int,
    visible_group_copies: int,
) -> None:
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if not 0 <= visible_nonprize_cards <= deck_size - prize_count:
        raise ValueError("visible_nonprize_cards leaves too few cards for the Prize cards")
    if not 0 <= group_copies <= deck_size:
        raise ValueError("group_copies must be between 0 and deck_size")
    if not 0 <= visible_group_copies <= group_copies:
        raise ValueError("visible_group_copies must be between 0 and group_copies")
    if visible_group_copies > visible_nonprize_cards:
        raise ValueError("visible_group_copies cannot exceed visible_nonprize_cards")

    remaining_group = group_copies - visible_group_copies
    unknown_cards = deck_size - visible_nonprize_cards
    if remaining_group > unknown_cards:
        raise ValueError("remaining group copies cannot exceed the unknown-card population")


def group_prize_distribution(
    group_copies: int,
    visible_group_copies: int = 0,
    visible_nonprize_cards: int = 7,
    deck_size: int = 60,
    prize_count: int = 6,
) -> list[tuple[int, float]]:
    """Return P(X=x) for the number of group copies currently in the Prizes.

    The visible cards are assumed known to be outside the Prize cards. Cards
    already taken from the Prizes should therefore not be included in
    visible_nonprize_cards.
    """
    _validate(
        deck_size,
        prize_count,
        visible_nonprize_cards,
        group_copies,
        visible_group_copies,
    )

    unknown_cards = deck_size - visible_nonprize_cards
    remaining_group = group_copies - visible_group_copies
    other_unknown = unknown_cards - remaining_group
    denominator = comb(unknown_cards, prize_count)

    rows: list[tuple[int, float]] = []
    minimum = max(0, prize_count - other_unknown)
    maximum = min(remaining_group, prize_count)

    for prized_group in range(minimum, maximum + 1):
        ways = comb(remaining_group, prized_group) * comb(
            other_unknown,
            prize_count - prized_group,
        )
        rows.append((prized_group, ways / denominator))

    return rows


def singleton_prized_probability(
    visible: bool = False,
    visible_nonprize_cards: int = 7,
    deck_size: int = 60,
    prize_count: int = 6,
) -> float:
    """Return the current Prize probability for one specific singleton card."""
    visible_group_copies = 1 if visible else 0
    distribution = group_prize_distribution(
        group_copies=1,
        visible_group_copies=visible_group_copies,
        visible_nonprize_cards=visible_nonprize_cards,
        deck_size=deck_size,
        prize_count=prize_count,
    )
    return sum(probability for prized, probability in distribution if prized == 1)


def prize_only_line_failure_probability(
    group_copies: int,
    minimum_unprized_needed: int = 1,
    visible_group_copies: int = 0,
    visible_nonprize_cards: int = 7,
    deck_size: int = 60,
    prize_count: int = 6,
) -> float:
    """Return the probability that Prizing leaves too few unprized group copies.

    This measures only Prize availability. It does not assert that visible or
    unprized copies are in a usable zone at the required game time.
    """
    if not 0 <= minimum_unprized_needed <= group_copies:
        raise ValueError("minimum_unprized_needed must be between 0 and group_copies")

    distribution = group_prize_distribution(
        group_copies=group_copies,
        visible_group_copies=visible_group_copies,
        visible_nonprize_cards=visible_nonprize_cards,
        deck_size=deck_size,
        prize_count=prize_count,
    )

    return sum(
        probability
        for prized, probability in distribution
        if group_copies - prized < minimum_unprized_needed
    )
