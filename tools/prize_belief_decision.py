"""Evaluate strategic line choices under an arbitrary grouped Prize belief."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from prize_belief_kernel import PrizeBelief
from prize_information_value import Line, line_available


@dataclass(frozen=True)
class BeliefDecisionResult:
    """Fixed-policy and exact-information values under the current belief."""

    fixed_line_values: tuple[tuple[str, float], ...]
    best_fixed_line: str
    fixed_value: float
    exact_information_value: float
    value_of_exact_information: float


def evaluate_under_belief(
    group_sizes: Mapping[str, int],
    lines: Sequence[Line],
    belief: PrizeBelief,
) -> BeliefDecisionResult:
    """Compare committing now with choosing after exact Prize inspection.

    The current belief may be an initial prior, a partial posterior, or a
    distribution created by a Prize-zone mutation.
    """
    if not lines:
        raise ValueError("lines must contain at least one strategic line")
    if set(group_sizes) != set(belief.groups):
        raise ValueError("group_sizes and belief groups must match exactly")

    for group, size in group_sizes.items():
        if size < 0:
            raise ValueError("group sizes must be non-negative")
        index = belief.groups.index(group)
        if any(state[index] > size for state, _ in belief.masses):
            raise ValueError(f"belief contains too many Prized copies for group {group}")

    state_rows = belief.state_dicts()
    fixed_values: list[tuple[str, float]] = []

    for line in lines:
        expected = 0.0
        for state, probability in state_rows:
            if line_available(line, state, group_sizes):
                expected += probability * line.utility
        fixed_values.append((line.name, expected))

    best_index = max(range(len(lines)), key=lambda index: fixed_values[index][1])
    best_line_name, fixed_value = fixed_values[best_index]

    exact_information_value = 0.0
    for state, probability in state_rows:
        best_realized = max(
            [0.0]
            + [
                line.utility
                for line in lines
                if line_available(line, state, group_sizes)
            ]
        )
        exact_information_value += probability * best_realized

    return BeliefDecisionResult(
        fixed_line_values=tuple(fixed_values),
        best_fixed_line=best_line_name,
        fixed_value=fixed_value,
        exact_information_value=exact_information_value,
        value_of_exact_information=exact_information_value - fixed_value,
    )
