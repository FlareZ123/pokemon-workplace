"""Exact Prize-rescue collapse probabilities conditioned on a valid opening hand.

This extends a setup-Prize rescue model by accounting for the Pokemon TCG mulligan
rule: the accepted opening hand must contain at least one setup-eligible starter.
For ordinary decks these starters are Basic Pokemon; card-text setup exceptions can
be counted as starters when applicable. Repeated reshuffles are equivalent to conditioning a random deck order on that event.
"""

from __future__ import annotations

from itertools import product
from math import comb


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def accepted_opening_probability(
    deck_size: int, starter_cards: int, opening_hand_size: int = 7
) -> float:
    """Return P(a random opening hand contains at least one setup-eligible starter)."""
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must be between 0 and deck_size")
    if not 0 <= opening_hand_size <= deck_size:
        raise ValueError("opening_hand_size must be between 0 and deck_size")
    if opening_hand_size == 0 or starter_cards == 0:
        return 0.0
    return 1.0 - _choose(deck_size - starter_cards, opening_hand_size) / _choose(
        deck_size, opening_hand_size
    )


def _category_sizes(
    deck_size: int,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
) -> tuple[int, int, int, int, int, int]:
    if min(critical_starter, critical_nonstarter, rescue_starter, rescue_nonstarter) < 0:
        raise ValueError("critical and rescue counts must be non-negative")
    if critical_starter + rescue_starter > starter_cards:
        raise ValueError("critical/rescue starter counts exceed total setup-eligible starters")
    if critical_nonstarter + rescue_nonstarter > deck_size - starter_cards:
        raise ValueError("critical/rescue non-starter counts exceed non-starter cards")

    filler_starter = starter_cards - critical_starter - rescue_starter
    filler_nonstarter = (
        deck_size
        - starter_cards
        - critical_nonstarter
        - rescue_nonstarter
    )
    return (
        critical_starter,
        critical_nonstarter,
        rescue_starter,
        rescue_nonstarter,
        filler_starter,
        filler_nonstarter,
    )


def conditioned_prize_state_distribution(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
    opening_hand_size: int = 7,
) -> list[tuple[tuple[int, int, int, int, int, int], float]]:
    """Return exact Prize-category states given an accepted starter-containing start.

    State tuple order is:
    (critical starter, critical non-starter, rescue starter, rescue non-starter,
     filler starter, filler non-starter) cards in the initial Prize cards.
    """
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if not 0 <= prize_count <= deck_size:
        raise ValueError("prize_count must be between 0 and deck_size")
    if opening_hand_size < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")
    if not 0 <= starter_cards <= deck_size:
        raise ValueError("starter_cards must be between 0 and deck_size")

    sizes = _category_sizes(
        deck_size,
        starter_cards,
        critical_starter,
        critical_nonstarter,
        rescue_starter,
        rescue_nonstarter,
    )
    accepted = accepted_opening_probability(deck_size, starter_cards, opening_hand_size)
    if accepted == 0.0:
        raise ValueError("conditioning event has zero probability")

    denominator = _choose(deck_size, prize_count)
    remaining_after_prizes = deck_size - prize_count
    states: list[tuple[tuple[int, int, int, int, int, int], float]] = []

    ranges = [range(min(size, prize_count) + 1) for size in sizes]
    for counts in product(*ranges):
        if sum(counts) != prize_count:
            continue

        ways = 1
        for size, count in zip(sizes, counts):
            ways *= _choose(size, count)
        if ways == 0:
            continue

        starters_prized = counts[0] + counts[2] + counts[4]
        starters_remaining = starter_cards - starters_prized
        accepted_given_state = accepted_opening_probability(
            remaining_after_prizes, starters_remaining, opening_hand_size
        )
        probability = (ways / denominator) * accepted_given_state / accepted
        if probability:
            states.append((counts, probability))

    return states


def collapse_probability_given_valid_start(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
    opening_hand_size: int = 7,
) -> float:
    """Return exact pre-Prize rescue-collapse probability after mulligan conditioning.

    Each rescue copy outside the Prize cards can retrieve one critical Prized card
    before becoming a Prize itself. Collapse occurs when the number of critical
    cards Prized exceeds the number of rescue copies initially outside the Prizes.
    """
    total_rescue = rescue_starter + rescue_nonstarter
    probability = 0.0
    for counts, mass in conditioned_prize_state_distribution(
        deck_size,
        prize_count,
        starter_cards=starter_cards,
        critical_starter=critical_starter,
        critical_nonstarter=critical_nonstarter,
        rescue_starter=rescue_starter,
        rescue_nonstarter=rescue_nonstarter,
        opening_hand_size=opening_hand_size,
    ):
        critical_prized = counts[0] + counts[1]
        rescue_prized = counts[2] + counts[3]
        if critical_prized > total_rescue - rescue_prized:
            probability += mass
    return probability


def any_critical_prized_probability_given_valid_start(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int = 0,
    rescue_nonstarter: int = 0,
    opening_hand_size: int = 7,
) -> float:
    """Return P(at least one modeled critical card is Prized | valid start)."""
    probability = 0.0
    for counts, mass in conditioned_prize_state_distribution(
        deck_size,
        prize_count,
        starter_cards=starter_cards,
        critical_starter=critical_starter,
        critical_nonstarter=critical_nonstarter,
        rescue_starter=rescue_starter,
        rescue_nonstarter=rescue_nonstarter,
        opening_hand_size=opening_hand_size,
    ):
        if counts[0] + counts[1] > 0:
            probability += mass
    return probability


def conditional_collapse_probability_given_valid_start(
    deck_size: int,
    prize_count: int,
    *,
    starter_cards: int,
    critical_starter: int,
    critical_nonstarter: int,
    rescue_starter: int,
    rescue_nonstarter: int,
    opening_hand_size: int = 7,
) -> float:
    """Return P(collapse | any critical Prized, accepted starter-containing start)."""
    any_critical = any_critical_prized_probability_given_valid_start(
        deck_size,
        prize_count,
        starter_cards=starter_cards,
        critical_starter=critical_starter,
        critical_nonstarter=critical_nonstarter,
        rescue_starter=rescue_starter,
        rescue_nonstarter=rescue_nonstarter,
        opening_hand_size=opening_hand_size,
    )
    if any_critical == 0.0:
        return 0.0
    return collapse_probability_given_valid_start(
        deck_size,
        prize_count,
        starter_cards=starter_cards,
        critical_starter=critical_starter,
        critical_nonstarter=critical_nonstarter,
        rescue_starter=rescue_starter,
        rescue_nonstarter=rescue_nonstarter,
        opening_hand_size=opening_hand_size,
    ) / any_critical
