"""Execute exact typed deck-search choices against exchangeable zone counts.

Demand-first search actions and retrieval-first search actions share the same
physical target-cost vector. This module applies that exact vector to canonical
zone counts while keeping off-board copies exchangeable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from multicopy_zone_state import ZoneCountState
from typed_search_retrieval import TypedRetrievalAction
from typed_search_target_allocator import TargetGroup, TypedTargetAction


@dataclass(frozen=True)
class SearchZoneTarget:
    """Bind one typed searchable target group to a zone-ledger card class."""

    card_class: str
    group: TargetGroup

    def __post_init__(self) -> None:
        if not self.card_class:
            raise ValueError("card_class must be non-empty")


@dataclass(frozen=True)
class SearchZoneMove:
    card_class: str
    amount: int


@dataclass(frozen=True)
class SearchZoneTransition:
    before: ZoneCountState
    after: ZoneCountState
    moves: tuple[SearchZoneMove, ...]


def _apply_target_cost(
    state: ZoneCountState,
    targets: Sequence[SearchZoneTarget],
    target_cost: tuple[int, ...],
    *,
    source_zone: str,
    destination_zone: str,
) -> SearchZoneTransition:
    bound_targets = tuple(targets)

    if not source_zone or not destination_zone:
        raise ValueError("zones must be non-empty")
    if source_zone == destination_zone:
        raise ValueError("source and destination zones must differ")
    if len(target_cost) != len(bound_targets):
        raise ValueError("target_cost length does not match bound targets")
    if any(value < 0 for value in target_cost):
        raise ValueError("target_cost cannot be negative")

    card_classes = tuple(target.card_class for target in bound_targets)
    if len(card_classes) != len(set(card_classes)):
        raise ValueError("bound target card classes must be unique")

    for bound, cost in zip(bound_targets, target_cost):
        if cost > bound.group.copies:
            raise ValueError(
                f"action consumes {cost} copies of {bound.group.name!r}, "
                f"but the target group exposes only {bound.group.copies}"
            )
        available = state.count(bound.card_class, source_zone)
        if cost > available:
            raise ValueError(
                f"action consumes {cost} {bound.card_class!r} from "
                f"{source_zone!r}, but only {available} remain"
            )

    after = state
    moves: list[SearchZoneMove] = []
    for bound, cost in zip(bound_targets, target_cost):
        if cost == 0:
            continue
        after = after.move(
            bound.card_class,
            source_zone,
            destination_zone,
            amount=cost,
        )
        moves.append(SearchZoneMove(bound.card_class, cost))

    classes = set(card_classes)
    classes.update(card_class for card_class, _zone, _count in state.counts)
    classes.update(card_class for card_class, _zone, _count in after.counts)
    for card_class in classes:
        if state.total(card_class) != after.total(card_class):
            raise AssertionError(
                f"card total changed for {card_class!r}: "
                f"{state.total(card_class)} -> {after.total(card_class)}"
            )

    return SearchZoneTransition(
        before=state,
        after=after,
        moves=tuple(moves),
    )


def apply_typed_search_action(
    state: ZoneCountState,
    targets: Sequence[SearchZoneTarget],
    action: TypedTargetAction,
    *,
    source_zone: str = "deck",
    destination_zone: str = "hand",
) -> SearchZoneTransition:
    """Execute a demand-first typed search action."""

    if any(value < 0 for value in action.output):
        raise ValueError("action output cannot be negative")
    if any(value < 0 for value in action.axis_usage):
        raise ValueError("axis usage cannot be negative")

    selected_units = sum(action.target_cost)
    if selected_units != sum(action.axis_usage):
        raise ValueError("target consumption must equal search-axis usage")
    if selected_units != sum(action.output):
        raise ValueError("target consumption must equal supplied demand units")

    return _apply_target_cost(
        state,
        targets,
        action.target_cost,
        source_zone=source_zone,
        destination_zone=destination_zone,
    )


def apply_typed_retrieval_action(
    state: ZoneCountState,
    targets: Sequence[SearchZoneTarget],
    action: TypedRetrievalAction,
    *,
    source_zone: str = "deck",
    destination_zone: str = "hand",
) -> SearchZoneTransition:
    """Execute a retrieval-first action without requiring immediate demand use."""

    if any(value < 0 for value in action.axis_usage):
        raise ValueError("axis usage cannot be negative")
    if sum(action.target_cost) != sum(action.axis_usage):
        raise ValueError("target consumption must equal search-axis usage")

    return _apply_target_cost(
        state,
        targets,
        action.target_cost,
        source_zone=source_zone,
        destination_zone=destination_zone,
    )
