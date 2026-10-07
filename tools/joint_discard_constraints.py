"""Filter exact discard witnesses with cross-card group constraints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    enumerate_discard_selections,
)
from multicopy_zone_state import ZoneCountState


@dataclass(frozen=True)
class DiscardGroupConstraint:
    """Upper bound on the total selected copies across named card classes."""

    card_classes: frozenset[str]
    max_total: int

    def __post_init__(self) -> None:
        if not self.card_classes:
            raise ValueError("card_classes must be non-empty")
        if self.max_total < 0:
            raise ValueError("max_total must be non-negative")


def enumerate_group_constrained_discard_selections(
    state: ZoneCountState,
    candidates: Sequence[DiscardCandidate],
    cost: int,
    constraints: Sequence[DiscardGroupConstraint],
    *,
    source_zone: str = "hand",
) -> tuple[DiscardSelection, ...]:
    """Return exact discard selections satisfying cardwise and group limits."""

    pool = tuple(candidates)
    class_to_index = {
        candidate.card_class: index
        for index, candidate in enumerate(pool)
    }
    if len(class_to_index) != len(pool):
        raise ValueError("candidate card classes must be unique")

    group_constraints = tuple(constraints)
    candidate_classes = frozenset(class_to_index)
    for constraint in group_constraints:
        unknown = constraint.card_classes - candidate_classes
        if unknown:
            raise ValueError(
                f"constraint references non-candidates: {sorted(unknown)!r}"
            )

    selections = enumerate_discard_selections(
        state,
        pool,
        cost,
        source_zone=source_zone,
    )

    def allowed(selection: DiscardSelection) -> bool:
        for constraint in group_constraints:
            selected = sum(
                selection.counts[class_to_index[card_class]]
                for card_class in constraint.card_classes
            )
            if selected > constraint.max_total:
                return False
        return True

    return tuple(selection for selection in selections if allowed(selection))


def maximum_group_constrained_discard_cost(
    state: ZoneCountState,
    candidates: Sequence[DiscardCandidate],
    constraints: Sequence[DiscardGroupConstraint],
    *,
    source_zone: str = "hand",
) -> int:
    """Return the largest exact discard cost allowed by all constraints."""

    pool = tuple(candidates)
    maximum = 0
    for candidate in pool:
        available = state.count(candidate.card_class, source_zone)
        if candidate.max_copies is not None:
            available = min(available, candidate.max_copies)
        maximum += available

    for cost in range(maximum, -1, -1):
        if enumerate_group_constrained_discard_selections(
            state,
            pool,
            cost,
            constraints,
            source_zone=source_zone,
        ):
            return cost
    raise AssertionError("zero-card discard should always be feasible")
