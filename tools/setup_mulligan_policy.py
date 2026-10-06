"""Exact opening/Prize probabilities with optional setup-card mulligan policy.

`forced_starters` are cards whose presence makes the opening non-mulliganable
under the ordinary setup rule, such as legally placeable Basic Pokemon.
`optional_starters` are cards whose text lets the player accept an otherwise
Basic-less hand by putting that card into the Active Spot during setup.

`optional_only_acceptance` is the probability of keeping a hand that contains
no forced starter and at least one optional starter. Values 0 and 1 represent
the two deterministic boundary policies; intermediate values are useful as a
reduced randomized-policy sensitivity model.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Literal

SetupClass = Literal["forced", "optional", "other"]


@dataclass(frozen=True)
class OpeningAcceptance:
    forced_present: float
    optional_only: float
    rejected: float
    accepted: float


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _validate(
    deck_size: int,
    forced_starters: int,
    optional_starters: int,
    opening_hand_size: int,
    optional_only_acceptance: float,
) -> None:
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if min(forced_starters, optional_starters) < 0:
        raise ValueError("starter counts must be non-negative")
    if forced_starters + optional_starters > deck_size:
        raise ValueError("starter counts exceed deck size")
    if not 0 <= opening_hand_size <= deck_size:
        raise ValueError("opening_hand_size must be between 0 and deck_size")
    if not 0.0 <= optional_only_acceptance <= 1.0:
        raise ValueError("optional_only_acceptance must be between 0 and 1")


def opening_acceptance(
    deck_size: int,
    forced_starters: int,
    optional_starters: int,
    *,
    opening_hand_size: int = 7,
    optional_only_acceptance: float = 1.0,
) -> OpeningAcceptance:
    """Return exact per-attempt opening acceptance components."""
    _validate(
        deck_size,
        forced_starters,
        optional_starters,
        opening_hand_size,
        optional_only_acceptance,
    )
    denominator = _choose(deck_size, opening_hand_size)
    if denominator == 0:
        return OpeningAcceptance(0.0, 0.0, 1.0, 0.0)

    no_forced = _choose(deck_size - forced_starters, opening_hand_size) / denominator
    no_forced_or_optional = (
        _choose(deck_size - forced_starters - optional_starters, opening_hand_size)
        / denominator
    )
    forced_present = 1.0 - no_forced
    optional_only_available = no_forced - no_forced_or_optional
    optional_only = optional_only_acceptance * optional_only_available
    accepted = forced_present + optional_only
    return OpeningAcceptance(
        forced_present=forced_present,
        optional_only=optional_only,
        rejected=1.0 - accepted,
        accepted=accepted,
    )


def expected_mulligans_before_acceptance(
    deck_size: int,
    forced_starters: int,
    optional_starters: int,
    *,
    opening_hand_size: int = 7,
    optional_only_acceptance: float = 1.0,
) -> float:
    """Return expected failed opening hands before the first accepted hand."""
    accepted = opening_acceptance(
        deck_size,
        forced_starters,
        optional_starters,
        opening_hand_size=opening_hand_size,
        optional_only_acceptance=optional_only_acceptance,
    ).accepted
    if accepted == 0.0:
        raise ValueError("opening can never be accepted under this policy")
    return (1.0 - accepted) / accepted


def mulligan_count_probability(
    deck_size: int,
    forced_starters: int,
    optional_starters: int,
    failed_mulligans: int,
    *,
    opening_hand_size: int = 7,
    optional_only_acceptance: float = 1.0,
) -> float:
    """Return P(exactly `failed_mulligans` failed hands before acceptance)."""
    if failed_mulligans < 0:
        raise ValueError("failed_mulligans must be non-negative")
    accepted = opening_acceptance(
        deck_size,
        forced_starters,
        optional_starters,
        opening_hand_size=opening_hand_size,
        optional_only_acceptance=optional_only_acceptance,
    ).accepted
    if accepted == 0.0:
        raise ValueError("opening can never be accepted under this policy")
    return (1.0 - accepted) ** failed_mulligans * accepted


def mulligan_tail_probability(
    deck_size: int,
    forced_starters: int,
    optional_starters: int,
    minimum_failed_mulligans: int,
    *,
    opening_hand_size: int = 7,
    optional_only_acceptance: float = 1.0,
) -> float:
    """Return P(at least `minimum_failed_mulligans` failed hands before acceptance)."""
    if minimum_failed_mulligans < 0:
        raise ValueError("minimum_failed_mulligans must be non-negative")
    accepted = opening_acceptance(
        deck_size,
        forced_starters,
        optional_starters,
        opening_hand_size=opening_hand_size,
        optional_only_acceptance=optional_only_acceptance,
    ).accepted
    if accepted == 0.0:
        raise ValueError("opening can never be accepted under this policy")
    return (1.0 - accepted) ** minimum_failed_mulligans


def conditioned_prize_class_distribution(
    deck_size: int,
    prize_count: int,
    *,
    forced_starters: int,
    optional_starters: int,
    opening_hand_size: int = 7,
    optional_only_acceptance: float = 1.0,
) -> list[tuple[tuple[int, int, int], float]]:
    """Return P((forced, optional, other) Prize counts | accepted opening)."""
    _validate(
        deck_size,
        forced_starters,
        optional_starters,
        opening_hand_size,
        optional_only_acceptance,
    )
    if prize_count < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")

    total_acceptance = opening_acceptance(
        deck_size,
        forced_starters,
        optional_starters,
        opening_hand_size=opening_hand_size,
        optional_only_acceptance=optional_only_acceptance,
    ).accepted
    if total_acceptance == 0.0:
        raise ValueError("conditioning event has zero probability")

    other_cards = deck_size - forced_starters - optional_starters
    denominator = _choose(deck_size, prize_count)
    remaining_size = deck_size - prize_count
    states: list[tuple[tuple[int, int, int], float]] = []

    for forced_prized in range(min(forced_starters, prize_count) + 1):
        max_optional = min(optional_starters, prize_count - forced_prized)
        for optional_prized in range(max_optional + 1):
            other_prized = prize_count - forced_prized - optional_prized
            if not 0 <= other_prized <= other_cards:
                continue
            ways = (
                _choose(forced_starters, forced_prized)
                * _choose(optional_starters, optional_prized)
                * _choose(other_cards, other_prized)
            )
            if ways == 0:
                continue
            acceptance_given_state = opening_acceptance(
                remaining_size,
                forced_starters - forced_prized,
                optional_starters - optional_prized,
                opening_hand_size=opening_hand_size,
                optional_only_acceptance=optional_only_acceptance,
            ).accepted
            mass = (ways / denominator) * acceptance_given_state / total_acceptance
            if mass:
                states.append(((forced_prized, optional_prized, other_prized), mass))
    return states


def specific_card_prize_probability(
    deck_size: int,
    prize_count: int,
    *,
    forced_starters: int,
    optional_starters: int,
    card_class: SetupClass,
    opening_hand_size: int = 7,
    optional_only_acceptance: float = 1.0,
) -> float:
    """Return the Prize probability of one labeled card in a setup class."""
    class_sizes = {
        "forced": forced_starters,
        "optional": optional_starters,
        "other": deck_size - forced_starters - optional_starters,
    }
    size = class_sizes[card_class]
    if size <= 0:
        raise ValueError(f"no cards in requested class: {card_class}")
    index = {"forced": 0, "optional": 1, "other": 2}[card_class]
    expected_prized = sum(
        counts[index] * mass
        for counts, mass in conditioned_prize_class_distribution(
            deck_size,
            prize_count,
            forced_starters=forced_starters,
            optional_starters=optional_starters,
            opening_hand_size=opening_hand_size,
            optional_only_acceptance=optional_only_acceptance,
        )
    )
    return expected_prized / size
