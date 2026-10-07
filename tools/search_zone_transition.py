"""Materialize an exact typed search action into exchangeable zone counts.

A typed search demand profile can alias several distinct physical target choices.
This bridge therefore requires the richer TypedTargetAction, whose target_cost
vector records which searchable target groups were actually consumed.

Deck and hand copies remain exchangeable here. Stable per-copy instance identity
is intentionally not introduced until topology or persistent history requires it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from multicopy_zone_state import ZoneCountState
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


def apply_typed_search_action(
    state: ZoneCountState,
    targets: Sequence[SearchZoneTarget],
    action: TypedTargetAction,
    *,
    source_zone: str = "deck",
    destination_zone: str = "hand",
) -> SearchZoneTransition:
    """Move the exact target copies chosen by one typed search action.

    The target order must be the same order used when the TypedTargetAction was
    produced. Each target binds that allocator position to the semantic card
    class used by ZoneCountState.
    """

    bound_targets = tuple(targets)

    if not source_zone or not destination_zone:
        raise ValueError("zones must be non-empty")
    if source_zone == destination_zone:
        raise ValueError("source and destination zones must differ")
    if len(action.target_cost) != len(bound_targets):
        raise ValueError("target_cost length does not match bound targets")

    card_classes = tuple(target.card_class for target in bound_targets)
    if len(card_classes) != len(set(card_classes)):
        raise ValueError("bound target card classes must be unique")

    if any(value < 0 for value in action.target_cost):
        raise ValueError("target_cost cannot be negative")
    if any(value < 0 for value in action.output):
        raise ValueError("action output cannot be negative")
    if any(value < 0 for value in action.axis_usage):
        raise ValueError("axis usage cannot be negative")

    selected_units = sum(action.target_cost)
    if selected_units != sum(action.axis_usage):
        raise ValueError("target consumption must equal search-axis usage")
    if selected_units != sum(action.output):
        raise ValueError("target consumption must equal supplied demand units")

    for bound, cost in zip(bound_targets, action.target_cost):
        if cost > bound.group.copies:
            raise ValueError(
                f"action consumes {cost} copies of {bound.group.name!r}, "
                f"but the allocator target group exposes only {bound.group.copies}"
            )
        available = state.count(bound.card_class, source_zone)
        if cost > available:
            raise ValueError(
                f"action consumes {cost} {bound.card_class!r} from "
                f"{source_zone!r}, but only {available} remain"
            )

    after = state
    moves: list[SearchZoneMove] = []
    for bound, cost in zip(bound_targets, action.target_cost):
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
