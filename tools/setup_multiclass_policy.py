"""Exact setup conditioning with identity-specific optional-starter classes."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from itertools import product
from math import comb

OptionalHandPolicy = Callable[[tuple[int, ...]], float]


def _choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return comb(n, k)


def _validate(
    deck_size: int,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    opening_hand_size: int,
) -> tuple[int, ...]:
    groups = tuple(optional_group_sizes)
    if deck_size <= 0:
        raise ValueError("deck_size must be positive")
    if forced_starters < 0 or any(size < 0 for size in groups):
        raise ValueError("card counts must be non-negative")
    if forced_starters + sum(groups) > deck_size:
        raise ValueError("starter counts exceed deck size")
    if not 0 <= opening_hand_size <= deck_size:
        raise ValueError("opening_hand_size must be between 0 and deck_size")
    return groups


def opening_acceptance_multiclass(
    deck_size: int,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    optional_policy: OptionalHandPolicy,
    *,
    opening_hand_size: int = 7,
) -> float:
    """Return exact per-attempt acceptance under an optional-hand policy.

    `optional_policy` is called only for hands containing zero forced starters.
    Its tuple argument gives the number drawn from each optional group. The
    policy returns an acceptance probability from 0 through 1.
    """
    groups = _validate(
        deck_size, forced_starters, optional_group_sizes, opening_hand_size
    )
    other_cards = deck_size - forced_starters - sum(groups)
    denominator = _choose(deck_size, opening_hand_size)
    acceptance_weight = 0.0

    ranges = [range(min(size, opening_hand_size) + 1) for size in groups]
    for forced_in_hand in range(min(forced_starters, opening_hand_size) + 1):
        for optional_counts in product(*ranges):
            other_in_hand = opening_hand_size - forced_in_hand - sum(optional_counts)
            if not 0 <= other_in_hand <= other_cards:
                continue
            ways = _choose(forced_starters, forced_in_hand) * _choose(
                other_cards, other_in_hand
            )
            for size, count in zip(groups, optional_counts):
                ways *= _choose(size, count)
            if ways == 0:
                continue

            if forced_in_hand > 0:
                keep_probability = 1.0
            else:
                keep_probability = float(optional_policy(optional_counts))
                if not 0.0 <= keep_probability <= 1.0:
                    raise ValueError("optional_policy must return a value between 0 and 1")
            acceptance_weight += ways * keep_probability

    return acceptance_weight / denominator


def expected_mulligans_multiclass(
    deck_size: int,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    optional_policy: OptionalHandPolicy,
    *,
    opening_hand_size: int = 7,
) -> float:
    """Return expected failed hands before acceptance under a stationary policy."""
    accepted = opening_acceptance_multiclass(
        deck_size,
        forced_starters,
        optional_group_sizes,
        optional_policy,
        opening_hand_size=opening_hand_size,
    )
    if accepted == 0.0:
        raise ValueError("opening can never be accepted under this policy")
    return (1.0 - accepted) / accepted


def conditioned_prize_multiclass_distribution(
    deck_size: int,
    prize_count: int,
    *,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    optional_policy: OptionalHandPolicy,
    opening_hand_size: int = 7,
) -> list[tuple[tuple[int, ...], float]]:
    """Return exact Prize-class counts given an accepted opening.

    State order is forced starters, each optional group in caller order, then
    ordinary other cards.
    """
    groups = _validate(
        deck_size, forced_starters, optional_group_sizes, opening_hand_size
    )
    if prize_count < 0 or opening_hand_size + prize_count > deck_size:
        raise ValueError("opening hand and Prize cards must fit in the deck")

    total_acceptance = opening_acceptance_multiclass(
        deck_size,
        forced_starters,
        groups,
        optional_policy,
        opening_hand_size=opening_hand_size,
    )
    if total_acceptance == 0.0:
        raise ValueError("conditioning event has zero probability")

    other_cards = deck_size - forced_starters - sum(groups)
    category_sizes = (forced_starters, *groups, other_cards)
    denominator = _choose(deck_size, prize_count)
    states: list[tuple[tuple[int, ...], float]] = []
    ranges = [range(min(size, prize_count) + 1) for size in category_sizes]

    for prize_counts in product(*ranges):
        if sum(prize_counts) != prize_count:
            continue
        ways = 1
        for size, count in zip(category_sizes, prize_counts):
            ways *= _choose(size, count)
        if ways == 0:
            continue

        remaining_forced = forced_starters - prize_counts[0]
        remaining_groups = tuple(
            size - count for size, count in zip(groups, prize_counts[1:-1])
        )
        acceptance_given_state = opening_acceptance_multiclass(
            deck_size - prize_count,
            remaining_forced,
            remaining_groups,
            optional_policy,
            opening_hand_size=opening_hand_size,
        )
        mass = (ways / denominator) * acceptance_given_state / total_acceptance
        if mass:
            states.append((prize_counts, mass))
    return states


def specific_class_card_prize_probability(
    deck_size: int,
    prize_count: int,
    *,
    forced_starters: int,
    optional_group_sizes: Sequence[int],
    optional_policy: OptionalHandPolicy,
    class_index: int,
    opening_hand_size: int = 7,
) -> float:
    """Return the Prize probability of one labeled card in a class.

    Class index 0 is forced starters, 1..m are optional groups, and m+1 is the
    ordinary other-card class.
    """
    groups = tuple(optional_group_sizes)
    category_sizes = (
        forced_starters,
        *groups,
        deck_size - forced_starters - sum(groups),
    )
    if not 0 <= class_index < len(category_sizes):
        raise ValueError("class_index is out of range")
    class_size = category_sizes[class_index]
    if class_size <= 0:
        raise ValueError("requested class contains no cards")

    expected_prized = sum(
        counts[class_index] * mass
        for counts, mass in conditioned_prize_multiclass_distribution(
            deck_size,
            prize_count,
            forced_starters=forced_starters,
            optional_group_sizes=groups,
            optional_policy=optional_policy,
            opening_hand_size=opening_hand_size,
        )
    )
    return expected_prized / class_size
