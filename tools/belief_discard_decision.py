"""Evaluate exact discard choices before and after perfect Prize information.

The evaluator keeps mechanics outside the utility model. For each Prize world it:

1. instantiates the physical state;
2. enumerates the same exact mechanical discard family;
3. asks the continuation-aware policy which selections reach the endpoint;
4. scores each selection with a caller-supplied world utility;
5. compares one fixed K0 choice against choosing after exact composition is known.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from belief_weighted_discard_policy import WorldStateFactory
from continuation_discard_policy import (
    ContinuationGenerator,
    continuation_feasible_discards,
    feasible_selections,
)
from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    enumerate_discard_selections,
)
from prize_belief_kernel import PrizeBelief


DiscardWorldUtility = Callable[[DiscardSelection, bool], float]


@dataclass(frozen=True)
class BeliefDiscardDecision:
    """Fixed-choice and perfect-information values for one discard deadline."""

    fixed_selection_values: tuple[tuple[DiscardSelection, float], ...]
    best_fixed_selection: DiscardSelection
    fixed_value: float
    exact_information_value: float
    value_of_exact_information: float


def evaluate_discard_decision_under_belief(
    belief: PrizeBelief,
    state_for_world: WorldStateFactory,
    candidates: Sequence[DiscardCandidate],
    cost: int,
    continuation: ContinuationGenerator,
    final_requirements: Mapping[str, int],
    utility: DiscardWorldUtility,
    *,
    endpoint_zone: str = "hand",
    source_zone: str = "hand",
) -> BeliefDiscardDecision:
    """Compare one K0 discard choice with choosing after exact Prize inspection."""

    if abs(belief.probability_mass() - 1.0) > 1e-9:
        raise ValueError("Prize belief must be normalized")

    pool = tuple(candidates)
    expected: dict[DiscardSelection, float] | None = None
    exact_value = 0.0

    for prize_counts, probability in belief.state_dicts():
        state = state_for_world(prize_counts)
        mechanical = tuple(
            enumerate_discard_selections(
                state,
                pool,
                cost,
                source_zone=source_zone,
            )
        )
        if not mechanical:
            raise ValueError("discard decision has no mechanical selections")

        if expected is None:
            expected = {selection: 0.0 for selection in mechanical}
        elif set(mechanical) != set(expected):
            raise ValueError(
                "mechanical discard family changes across Prize worlds"
            )

        witnesses = continuation_feasible_discards(
            state,
            pool,
            cost,
            continuation,
            final_requirements,
            endpoint_zone=endpoint_zone,
            source_zone=source_zone,
        )
        safe = set(feasible_selections(witnesses))

        world_values = {
            selection: float(utility(selection, selection in safe))
            for selection in mechanical
        }
        for selection, value in world_values.items():
            expected[selection] += probability * value
        exact_value += probability * max(world_values.values())

    if expected is None:
        raise ValueError("Prize belief contains no states")

    ordered = tuple(
        sorted(
            expected.items(),
            key=lambda row: row[0].counts,
        )
    )
    best_selection, fixed_value = max(
        ordered,
        key=lambda row: (row[1], tuple(-value for value in row[0].counts)),
    )

    return BeliefDiscardDecision(
        fixed_selection_values=ordered,
        best_fixed_selection=best_selection,
        fixed_value=fixed_value,
        exact_information_value=exact_value,
        value_of_exact_information=exact_value - fixed_value,
    )
