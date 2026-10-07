"""Physical deck-size projection and exact materialized top draw."""

from __future__ import annotations

from dataclasses import dataclass

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from identity_materialization import assert_conserved, move_instance
from physical_zone_count import physical_zone_count
from top_prize_physical_bridge import TopPrizePhysicalState


def physical_deck_size(ledger) -> int:
    """Count unordered deck cards plus the materialized top relation."""

    return (
        physical_zone_count(ledger, "deck")
        + physical_zone_count(ledger, "deck_top")
    )


@dataclass(frozen=True)
class ExactTopDrawTransition:
    before: TopPrizePhysicalState
    after: SearchableDeckPhysicalState
    drawn_instance_id: str


def draw_exact_top_to_hand(
    state: TopPrizePhysicalState,
) -> ExactTopDrawTransition:
    """Move the exact materialized top card into hand."""

    before_size = physical_deck_size(state.ledger)
    if before_size <= 0:
        raise ValueError("cannot draw from an empty deck")

    ledger = move_instance(
        state.ledger,
        state.top_instance_id,
        "hand",
    )
    assert_conserved(state.ledger, ledger)
    after = SearchableDeckPhysicalState(
        ledger,
        state.prize_instance_ids,
        state.face_up,
    )
    if physical_deck_size(after.ledger) != before_size - 1:
        raise AssertionError("drawing top must reduce physical deck size by one")

    return ExactTopDrawTransition(
        before=state,
        after=after,
        drawn_instance_id=state.top_instance_id,
    )
