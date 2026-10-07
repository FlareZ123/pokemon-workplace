"""Rank exact Pokémon TCG discard witnesses after feasibility filtering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from discard_cost_witness import DiscardCandidate, DiscardSelection
from joint_discard_constraints import (
    DiscardGroupConstraint,
    enumerate_group_constrained_discard_selections,
)
from multicopy_zone_state import ZoneCountState


@dataclass(frozen=True)
class RankedDiscardSelection:
    selection: DiscardSelection
    desirability: float


def rank_discard_selections(
    state: ZoneCountState,
    candidates: Sequence[DiscardCandidate],
    cost: int,
    constraints: Sequence[DiscardGroupConstraint],
    desirability_by_class: Mapping[str, float],
    *,
    source_zone: str = "hand",
) -> tuple[RankedDiscardSelection, ...]:
    """Return feasible witnesses ordered by descending additive desirability."""

    pool = tuple(candidates)
    scores = tuple(float(desirability_by_class[c.card_class]) for c in pool)
    if any(score < 0.0 or score > 1.0 for score in scores):
        raise ValueError("discard desirability scores must be in [0, 1]")

    selections = enumerate_group_constrained_discard_selections(
        state,
        pool,
        cost,
        constraints,
        source_zone=source_zone,
    )
    ranked = [
        RankedDiscardSelection(
            selection=selection,
            desirability=sum(
                count * score
                for count, score in zip(selection.counts, scores)
            ),
        )
        for selection in selections
    ]
    return tuple(
        sorted(
            ranked,
            key=lambda entry: (-entry.desirability, entry.selection.counts),
        )
    )
