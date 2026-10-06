"""Exact value-of-information calculations for initial Prize knowledge.

The model starts from the player's currently unknown card set after setup. A
standard seven-card opening with no additional known non-Prize cards leaves 53
cards whose split between the deck and six Prize cards is unknown.

Cards are partitioned into named groups. A strategic line can require at least
some number of unprized copies from one or more groups. The model compares:

* K0: commit to one line before the first full deck search reveals which cards
  are Prized;
* K1: after that search, choose the best available line for the realized Prize
  state.

This isolates the decision value of Prize information. It does not model the
cost of performing the search or the gameplay value of the lines themselves
unless utilities are supplied explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import comb
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Line:
    """A line whose utility is realized only when all requirements are met."""

    name: str
    requirements: tuple[tuple[str, int], ...]
    utility: float = 1.0


@dataclass(frozen=True)
class PrizeInformationResult:
    """Summary of K0 precommitment versus K1 adaptive choice."""

    fixed_line_values: tuple[tuple[str, float], ...]
    best_k0_line: str
    k0_value: float
    k1_value: float
    information_value: float
    improvement_state_probability: float


def _validate_population(group_sizes: Mapping[str, int], unknown_cards: int, prize_count: int) -> None:
    if unknown_cards <= 0:
        raise ValueError("unknown_cards must be positive")
    if not 0 <= prize_count <= unknown_cards:
        raise ValueError("prize_count must be between 0 and unknown_cards")
    if not group_sizes:
        raise ValueError("group_sizes must contain at least one named group")
    if any(not name for name in group_sizes):
        raise ValueError("group names must be non-empty")
    if any(size < 0 for size in group_sizes.values()):
        raise ValueError("group sizes must be non-negative")
    if sum(group_sizes.values()) > unknown_cards:
        raise ValueError("group sizes cannot exceed unknown_cards")


def _validate_lines(group_sizes: Mapping[str, int], lines: Sequence[Line]) -> None:
    if not lines:
        raise ValueError("lines must contain at least one strategic line")

    seen_names: set[str] = set()
    for line in lines:
        if not line.name:
            raise ValueError("line names must be non-empty")
        if line.name in seen_names:
            raise ValueError(f"duplicate line name: {line.name}")
        seen_names.add(line.name)

        if line.utility < 0:
            raise ValueError("line utility must be non-negative")

        seen_groups: set[str] = set()
        for group, min_available in line.requirements:
            if group not in group_sizes:
                raise ValueError(f"unknown requirement group: {group}")
            if group in seen_groups:
                raise ValueError(f"duplicate requirement group in line {line.name}: {group}")
            seen_groups.add(group)
            if not 0 <= min_available <= group_sizes[group]:
                raise ValueError(
                    f"required available copies for {group} must be between 0 and {group_sizes[group]}"
                )


def prize_state_probabilities(
    group_sizes: Mapping[str, int],
    unknown_cards: int = 53,
    prize_count: int = 6,
) -> list[tuple[dict[str, int], float]]:
    """Return every grouped Prize state and its exact combinatorial probability.

    The state dictionary records how many copies from each named group are
    Prized. All unmodeled cards are pooled into one filler category.
    """
    _validate_population(group_sizes, unknown_cards, prize_count)

    names = tuple(group_sizes)
    sizes = tuple(group_sizes[name] for name in names)
    filler = unknown_cards - sum(sizes)
    denominator = comb(unknown_cards, prize_count)

    states: list[tuple[dict[str, int], float]] = []
    ranges = [range(size + 1) for size in sizes]

    for prized_counts in product(*ranges):
        modeled_prized = sum(prized_counts)
        filler_prized = prize_count - modeled_prized
        if not 0 <= filler_prized <= filler:
            continue

        ways = comb(filler, filler_prized)
        for size, prized in zip(sizes, prized_counts):
            ways *= comb(size, prized)

        if ways:
            states.append(
                (
                    dict(zip(names, prized_counts)),
                    ways / denominator,
                )
            )

    return states


def line_available(line: Line, state: Mapping[str, int], group_sizes: Mapping[str, int]) -> bool:
    """Return whether all required unprized copies remain available."""
    return all(
        group_sizes[group] - state[group] >= min_available
        for group, min_available in line.requirements
    )


def evaluate_prize_information(
    group_sizes: Mapping[str, int],
    lines: Sequence[Line],
    unknown_cards: int = 53,
    prize_count: int = 6,
) -> PrizeInformationResult:
    """Compare a K0 fixed choice with the K1 state-adaptive optimum.

    Each line yields its supplied utility when available and zero otherwise.
    K0 must select one line before seeing the Prize state. K1 may select the
    highest-utility available line after the Prize state becomes known.
    """
    _validate_population(group_sizes, unknown_cards, prize_count)
    _validate_lines(group_sizes, lines)
    states = prize_state_probabilities(group_sizes, unknown_cards, prize_count)

    fixed_values: list[tuple[str, float]] = []
    for line in lines:
        value = sum(
            probability * (line.utility if line_available(line, state, group_sizes) else 0.0)
            for state, probability in states
        )
        fixed_values.append((line.name, value))

    best_index = max(range(len(lines)), key=lambda index: fixed_values[index][1])
    best_line = lines[best_index]
    k0_value = fixed_values[best_index][1]

    k1_value = 0.0
    improvement_state_probability = 0.0

    for state, probability in states:
        fixed_realized = best_line.utility if line_available(best_line, state, group_sizes) else 0.0
        adaptive_realized = max(
            [0.0]
            + [
                line.utility
                for line in lines
                if line_available(line, state, group_sizes)
            ]
        )
        k1_value += probability * adaptive_realized
        if adaptive_realized > fixed_realized:
            improvement_state_probability += probability

    return PrizeInformationResult(
        fixed_line_values=tuple(fixed_values),
        best_k0_line=best_line.name,
        k0_value=k0_value,
        k1_value=k1_value,
        information_value=k1_value - k0_value,
        improvement_state_probability=improvement_state_probability,
    )
