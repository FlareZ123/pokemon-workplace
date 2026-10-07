from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from math import factorial
from typing import Hashable, Iterable


@dataclass(frozen=True)
class PokedexWitness:
    final_prefix: tuple[Hashable, ...]
    observed_count: int


def _reorder_prefix(prefix: tuple[Hashable, ...], count: int) -> set[tuple[Hashable, ...]]:
    if count < 1 or count > len(prefix):
        raise ValueError("count must be between 1 and the available prefix length")

    suffix = prefix[count:]
    return {
        tuple(order) + suffix
        for order in permutations(prefix[:count])
    }


def legacy_pokedex_witnesses(prefix: Iterable[Hashable]) -> tuple[PokedexWitness, ...]:
    """Enumerate old 'look at up to 5' witnesses for the available top prefix."""

    cards = tuple(prefix)[:5]
    if not cards:
        return ()
    return tuple(
        PokedexWitness(final_prefix=final, observed_count=count)
        for count in range(1, len(cards) + 1)
        for final in sorted(_reorder_prefix(cards, count), key=repr)
    )


def current_pokedex_witnesses(prefix: Iterable[Hashable]) -> tuple[PokedexWitness, ...]:
    """Enumerate current fixed-top-five witnesses, truncated by cards available."""

    cards = tuple(prefix)[:5]
    if not cards:
        return ()
    count = len(cards)
    return tuple(
        PokedexWitness(final_prefix=final, observed_count=count)
        for final in sorted(_reorder_prefix(cards, count), key=repr)
    )


def physical_outcomes(witnesses: Iterable[PokedexWitness]) -> frozenset[tuple[Hashable, ...]]:
    return frozenset(witness.final_prefix for witness in witnesses)


def observation_counts_by_outcome(
    witnesses: Iterable[PokedexWitness],
) -> dict[tuple[Hashable, ...], frozenset[int]]:
    grouped: dict[tuple[Hashable, ...], set[int]] = {}
    for witness in witnesses:
        grouped.setdefault(witness.final_prefix, set()).add(witness.observed_count)
    return {
        outcome: frozenset(counts)
        for outcome, counts in grouped.items()
    }


def summarize_distinct_prefix(size: int) -> dict[str, int | bool]:
    if size < 1 or size > 5:
        raise ValueError("size must be between 1 and 5")

    prefix = tuple(range(size))
    legacy = legacy_pokedex_witnesses(prefix)
    current = current_pokedex_witnesses(prefix)
    legacy_outcomes = physical_outcomes(legacy)
    current_outcomes = physical_outcomes(current)
    legacy_obs = observation_counts_by_outcome(legacy)

    lower_information_outcomes = {
        outcome
        for outcome, counts in legacy_obs.items()
        if any(count < size for count in counts)
    }

    return {
        "available_cards": size,
        "legacy_action_witnesses": len(legacy),
        "current_action_witnesses": len(current),
        "legacy_physical_outcomes": len(legacy_outcomes),
        "current_physical_outcomes": len(current_outcomes),
        "physical_outcomes_equal": legacy_outcomes == current_outcomes,
        "expected_physical_outcomes": factorial(size),
        "legacy_outcomes_with_lower_information_witness": len(lower_information_outcomes),
    }
