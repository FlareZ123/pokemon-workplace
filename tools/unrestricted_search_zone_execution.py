"""Conserved execution for unrestricted fixed-count deck searches.

This layer separates physical selected-card count from strategically useful
output. It expects a search-ready aggregate state where searchable cards are in
the ``deck`` zone. For top-deck destinations, ``top_order`` stores the ordered
card classes with index 0 as the next card to draw.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Sequence

from multicopy_zone_state import ZoneCountState
from unrestricted_search_selection import unrestricted_fixed_bounds


@dataclass(frozen=True)
class PhysicalSelection:
    card_class: str
    amount: int
    useful_units: int = 0

    def __post_init__(self) -> None:
        if not self.card_class:
            raise ValueError("card_class must be non-empty")
        if self.amount <= 0:
            raise ValueError("amount must be positive")
        if not 0 <= self.useful_units <= self.amount:
            raise ValueError("useful_units must lie between zero and amount")


@dataclass(frozen=True)
class UnrestrictedSearchZoneExecution:
    before: ZoneCountState
    after: ZoneCountState
    selections: tuple[PhysicalSelection, ...]
    selected_units: int
    useful_units: int
    destination: str
    top_order: tuple[str, ...] = ()


def _assert_conserved(before: ZoneCountState, after: ZoneCountState) -> None:
    classes = {card_class for card_class, _zone, _count in before.counts}
    classes.update(card_class for card_class, _zone, _count in after.counts)
    for card_class in classes:
        if before.total(card_class) != after.total(card_class):
            raise AssertionError(
                f"card total changed for {card_class!r}: "
                f"{before.total(card_class)} -> {after.total(card_class)}"
            )


def execute_unrestricted_fixed_search(
    state: ZoneCountState,
    selections: Sequence[PhysicalSelection],
    *,
    specified_count: int,
    destination: str,
    top_order: Sequence[str] = (),
) -> UnrestrictedSearchZoneExecution:
    """Execute one exact unrestricted search against aggregate deck counts."""

    selected = tuple(selections)
    classes = tuple(row.card_class for row in selected)
    if len(classes) != len(set(classes)):
        raise ValueError("selection card classes must be unique")

    deck_size = sum(
        count for _card_class, zone, count in state.counts if zone == "deck"
    )
    required = unrestricted_fixed_bounds(
        specified_count=specified_count,
        deck_size=deck_size,
    ).minimum
    selected_units = sum(row.amount for row in selected)
    if selected_units != required:
        raise ValueError(
            f"unrestricted search must select exactly {required} physical cards; "
            f"got {selected_units}"
        )

    for row in selected:
        available = state.count(row.card_class, "deck")
        if row.amount > available:
            raise ValueError(
                f"cannot select {row.amount} {row.card_class!r}; "
                f"only {available} remain in deck"
            )

    if destination not in {"hand", "deck_top"}:
        raise ValueError("destination must be 'hand' or 'deck_top'")

    order = tuple(top_order)
    if destination == "hand":
        if order:
            raise ValueError("hand destination cannot carry top_order")
    else:
        if len(order) != selected_units:
            raise ValueError("top_order must contain every selected physical card")
        expected = Counter(
            {row.card_class: row.amount for row in selected}
        )
        if Counter(order) != expected:
            raise ValueError("top_order multiset must match physical selections")

    after = state
    for row in selected:
        after = after.move(
            row.card_class,
            "deck",
            destination,
            amount=row.amount,
        )

    _assert_conserved(state, after)
    return UnrestrictedSearchZoneExecution(
        before=state,
        after=after,
        selections=selected,
        selected_units=selected_units,
        useful_units=sum(row.useful_units for row in selected),
        destination=destination,
        top_order=order,
    )
