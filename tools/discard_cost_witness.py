"""Enumerate and execute exact card selections for discard costs.

A scalar discardable-card capacity can prove feasibility without being enough
to mutate a canonical hand state. Different card-class selections can satisfy
the same discard requirement and leave different future hands.

This module keeps off-board copies exchangeable by card class and records an
exact count vector for each legal discard selection.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Sequence

from multicopy_zone_state import ZoneCountState


@dataclass(frozen=True)
class DiscardCandidate:
    card_class: str
    max_copies: int | None = None

    def __post_init__(self) -> None:
        if not self.card_class:
            raise ValueError("card_class must be non-empty")
        if self.max_copies is not None and self.max_copies < 0:
            raise ValueError("max_copies must be non-negative")


@dataclass(frozen=True)
class DiscardSelection:
    counts: tuple[int, ...]

    @property
    def cost(self) -> int:
        return sum(self.counts)


@dataclass(frozen=True)
class DiscardTransition:
    before: ZoneCountState
    after: ZoneCountState
    selection: DiscardSelection


def enumerate_discard_selections(
    state: ZoneCountState,
    candidates: Sequence[DiscardCandidate],
    cost: int,
    *,
    source_zone: str = "hand",
) -> tuple[DiscardSelection, ...]:
    """Return every exact card-class count vector satisfying the discard cost."""

    if cost < 0:
        raise ValueError("cost must be non-negative")
    if not source_zone:
        raise ValueError("source_zone must be non-empty")

    pool = tuple(candidates)
    classes = tuple(candidate.card_class for candidate in pool)
    if len(classes) != len(set(classes)):
        raise ValueError("candidate card classes must be unique")

    limits = []
    for candidate in pool:
        available = state.count(candidate.card_class, source_zone)
        if candidate.max_copies is not None:
            available = min(available, candidate.max_copies)
        limits.append(available)

    selections = [
        DiscardSelection(tuple(counts))
        for counts in product(*(range(limit + 1) for limit in limits))
        if sum(counts) == cost
    ]
    return tuple(sorted(selections, key=lambda selection: selection.counts))


def apply_discard_selection(
    state: ZoneCountState,
    candidates: Sequence[DiscardCandidate],
    selection: DiscardSelection,
    *,
    source_zone: str = "hand",
    destination_zone: str = "discard",
) -> DiscardTransition:
    """Move the selected copies and verify per-card-class conservation."""

    pool = tuple(candidates)
    if len(selection.counts) != len(pool):
        raise ValueError("selection length does not match candidates")
    if not source_zone or not destination_zone:
        raise ValueError("zones must be non-empty")
    if source_zone == destination_zone:
        raise ValueError("source and destination zones must differ")
    if any(count < 0 for count in selection.counts):
        raise ValueError("selection counts cannot be negative")

    classes = tuple(candidate.card_class for candidate in pool)
    if len(classes) != len(set(classes)):
        raise ValueError("candidate card classes must be unique")

    after = state
    for candidate, count in zip(pool, selection.counts):
        if count == 0:
            continue
        if candidate.max_copies is not None and count > candidate.max_copies:
            raise ValueError(
                f"selection exceeds allowed copies of {candidate.card_class!r}"
            )
        after = after.move(
            candidate.card_class,
            source_zone,
            destination_zone,
            amount=count,
        )

    all_classes = {
        card_class
        for card_class, _zone, _count in state.counts
    } | {
        card_class
        for card_class, _zone, _count in after.counts
    }
    for card_class in all_classes:
        if state.total(card_class) != after.total(card_class):
            raise AssertionError(
                f"card total changed for {card_class!r}: "
                f"{state.total(card_class)} -> {after.total(card_class)}"
            )

    return DiscardTransition(
        before=state,
        after=after,
        selection=selection,
    )
