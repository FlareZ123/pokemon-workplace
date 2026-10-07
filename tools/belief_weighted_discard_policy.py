"""Evaluate continuation-aware discard safety under Prize uncertainty.

For each grouped Prize-composition world, callers instantiate the corresponding
physical zone state and reuse the exact continuation-aware discard policy. The
result is a probability that each exact discard selection still has at least
one endpoint-satisfying continuation.

This keeps three questions separate:

- mechanical discard selection in the current hand;
- world-specific future reachability;
- uncertainty over which Prize world is actual.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

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
from multicopy_zone_state import ZoneCountState
from prize_belief_kernel import PrizeBelief


WorldStateFactory = Callable[[Mapping[str, int]], ZoneCountState]


@dataclass(frozen=True)
class BeliefDiscardSafety:
    """Probability that one exact discard selection has a valid continuation."""

    selection: DiscardSelection
    safety_probability: float


def discard_safety_under_belief(
    belief: PrizeBelief,
    state_for_world: WorldStateFactory,
    candidates: Sequence[DiscardCandidate],
    cost: int,
    continuation: ContinuationGenerator,
    final_requirements: Mapping[str, int],
    *,
    endpoint_zone: str = "hand",
    source_zone: str = "hand",
) -> tuple[BeliefDiscardSafety, ...]:
    """Return continuation-safety probability for every mechanical selection."""

    mass = belief.probability_mass()
    if abs(mass - 1.0) > 1e-9:
        raise ValueError(f"Prize belief must be normalized, got {mass}")

    pool = tuple(candidates)
    all_selections: set[DiscardSelection] = set()
    safe_mass: dict[DiscardSelection, float] = {}

    for prize_counts, probability in belief.state_dicts():
        state = state_for_world(prize_counts)
        mechanical = enumerate_discard_selections(
            state,
            pool,
            cost,
            source_zone=source_zone,
        )
        all_selections.update(mechanical)

        witnesses = continuation_feasible_discards(
            state,
            pool,
            cost,
            continuation,
            final_requirements,
            endpoint_zone=endpoint_zone,
            source_zone=source_zone,
        )
        for selection in feasible_selections(witnesses):
            safe_mass[selection] = (
                safe_mass.get(selection, 0.0)
                + probability
            )

    return tuple(
        BeliefDiscardSafety(
            selection=selection,
            safety_probability=safe_mass.get(selection, 0.0),
        )
        for selection in sorted(
            all_selections,
            key=lambda current: current.counts,
        )
    )
