"""Filter and rank exact discard witnesses by future continuation feasibility.

A current hand can make a required copy look protected even when a legal later
search can restore the same card class before the endpoint deadline. This module
keeps exact discard selection separate from continuation planning:

1. enumerate mechanically possible discard witnesses;
2. ask a caller-supplied continuation generator to execute future legal actions;
3. retain only witnesses whose resulting state satisfies the endpoint;
4. optionally rank those future-feasible witnesses with DCI-style desirability.

The continuation generator owns the actual game semantics. It may run Trainer
transactions, attacks, recovery effects, turn advances, or another validated
state-transition layer. This module only defines the policy seam.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass

from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    enumerate_discard_selections,
)
from multicopy_zone_state import ZoneCountState


ContinuationGenerator = Callable[
    [ZoneCountState, DiscardSelection],
    Iterable[tuple[str, ZoneCountState]],
]


@dataclass(frozen=True)
class ContinuationDiscardWitness:
    """One discard selection with one endpoint-satisfying continuation."""

    selection: DiscardSelection
    continuation_label: str
    final_state: ZoneCountState


@dataclass(frozen=True)
class RankedContinuationDiscard:
    """Continuation-feasible witness with additive discard desirability."""

    witness: ContinuationDiscardWitness
    desirability: float


def _endpoint_satisfied(
    state: ZoneCountState,
    requirements: Mapping[str, int],
    *,
    zone: str,
) -> bool:
    if not zone:
        raise ValueError("endpoint zone must be non-empty")
    return all(
        required >= 0 and state.count(card_class, zone) >= required
        for card_class, required in requirements.items()
    )


def continuation_feasible_discards(
    state: ZoneCountState,
    candidates: Sequence[DiscardCandidate],
    cost: int,
    continuation: ContinuationGenerator,
    final_requirements: Mapping[str, int],
    *,
    endpoint_zone: str = "hand",
    source_zone: str = "hand",
) -> tuple[ContinuationDiscardWitness, ...]:
    """Return exact discard selections that have a legal endpoint continuation.

    The input state is the state in which the discard decision is being made.
    The continuation callable receives that same state plus the exact selection.
    It is responsible for executing the discard inside the relevant game action,
    so effects with a resolving card, ordering rules, or other atomic semantics
    do not have to be approximated here.
    """

    if cost < 0:
        raise ValueError("cost must be non-negative")
    if any(required < 0 for required in final_requirements.values()):
        raise ValueError("final requirements must be non-negative")

    selections = enumerate_discard_selections(
        state,
        candidates,
        cost,
        source_zone=source_zone,
    )
    witnesses: list[ContinuationDiscardWitness] = []
    seen: set[tuple[tuple[int, ...], str, ZoneCountState]] = set()

    for selection in selections:
        for label, final_state in continuation(state, selection):
            if not label:
                raise ValueError("continuation labels must be non-empty")
            if not _endpoint_satisfied(
                final_state,
                final_requirements,
                zone=endpoint_zone,
            ):
                continue
            key = (selection.counts, label, final_state)
            if key in seen:
                continue
            seen.add(key)
            witnesses.append(
                ContinuationDiscardWitness(
                    selection=selection,
                    continuation_label=label,
                    final_state=final_state,
                )
            )

    return tuple(
        sorted(
            witnesses,
            key=lambda witness: (
                witness.selection.counts,
                witness.continuation_label,
                witness.final_state.counts,
            ),
        )
    )


def feasible_selections(
    witnesses: Sequence[ContinuationDiscardWitness],
) -> tuple[DiscardSelection, ...]:
    """Project continuation witnesses to unique exact discard selections."""

    unique = {
        witness.selection
        for witness in witnesses
    }
    return tuple(sorted(unique, key=lambda selection: selection.counts))


def rank_continuation_discards(
    witnesses: Sequence[ContinuationDiscardWitness],
    candidates: Sequence[DiscardCandidate],
    desirability_by_class: Mapping[str, float],
) -> tuple[RankedContinuationDiscard, ...]:
    """Rank future-feasible witnesses after continuation filtering.

    Scalar desirability remains an objective over already-valid witnesses. It
    cannot make an endpoint-infeasible discard legal.
    """

    pool = tuple(candidates)
    scores = tuple(
        float(desirability_by_class[candidate.card_class])
        for candidate in pool
    )
    if any(score < 0.0 or score > 1.0 for score in scores):
        raise ValueError("discard desirability scores must be in [0, 1]")

    ranked = []
    for witness in witnesses:
        if len(witness.selection.counts) != len(pool):
            raise ValueError("selection length does not match candidates")
        desirability = sum(
            count * score
            for count, score in zip(
                witness.selection.counts,
                scores,
                strict=True,
            )
        )
        ranked.append(
            RankedContinuationDiscard(
                witness=witness,
                desirability=desirability,
            )
        )

    return tuple(
        sorted(
            ranked,
            key=lambda entry: (
                -entry.desirability,
                entry.witness.selection.counts,
                entry.witness.continuation_label,
            ),
        )
    )
