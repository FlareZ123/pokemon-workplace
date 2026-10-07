"""Physical deck-search/shuffle boundary for a materialized top card."""

from __future__ import annotations

from dataclasses import dataclass

from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    dematerialize,
    materialize,
    move_instance,
    put_in_play_instance,
)
from top_prize_physical_bridge import TopPrizePhysicalState


@dataclass(frozen=True)
class SearchableDeckPhysicalState:
    """Physical state while deck order is intentionally not represented."""

    ledger: IdentityLedger
    prize_instance_ids: tuple[str, ...]
    face_up: tuple[bool, ...]

    def __post_init__(self) -> None:
        if len(self.prize_instance_ids) != len(self.face_up):
            raise ValueError("face_up must align with Prize positions")
        if any(row.zone == "deck_top" for row in self.ledger.instances):
            raise ValueError("searchable deck state must not retain deck_top")
        for instance_id in self.prize_instance_ids:
            if self.ledger.instance(instance_id).zone != "prize":
                raise ValueError("Prize instances must remain in prize")


def open_deck_for_search(
    physical: TopPrizePhysicalState,
) -> SearchableDeckPhysicalState:
    """Return the materialized top card to the unordered searchable deck."""

    top_id = physical.top_instance_id
    top_rows = [
        row.instance_id
        for row in physical.ledger.instances
        if row.zone == "deck_top"
    ]
    if top_rows != [top_id]:
        raise ValueError("physical state must contain exactly one deck_top instance")

    ledger = move_instance(
        physical.ledger,
        top_id,
        "deck",
    )
    ledger = dematerialize(ledger, top_id)
    assert_conserved(physical.ledger, ledger)

    return SearchableDeckPhysicalState(
        ledger,
        physical.prize_instance_ids,
        physical.face_up,
    )


def search_deck_card_to_play(
    state: SearchableDeckPhysicalState,
    *,
    card_class: str,
    card_name: str,
    instance_id: str,
    board_object_id: str,
) -> SearchableDeckPhysicalState:
    """Materialize one exact deck class and place that card into play."""

    before = state.ledger
    ledger = materialize(
        before,
        card_class=card_class,
        card_name=card_name,
        source_zone="deck",
        instance_id=instance_id,
    )
    ledger = put_in_play_instance(
        ledger,
        instance_id,
        board_object_id,
    )
    assert_conserved(before, ledger)

    return SearchableDeckPhysicalState(
        ledger,
        state.prize_instance_ids,
        state.face_up,
    )


def finish_shuffle_with_sampled_top(
    state: SearchableDeckPhysicalState,
    *,
    card_class: str,
    card_name: str,
    instance_id: str,
) -> TopPrizePhysicalState:
    """Materialize one sampled post-shuffle top card."""

    before = state.ledger
    ledger = materialize(
        before,
        card_class=card_class,
        card_name=card_name,
        source_zone="deck",
        instance_id=instance_id,
    )
    ledger = move_instance(
        ledger,
        instance_id,
        "deck_top",
    )
    assert_conserved(before, ledger)

    return TopPrizePhysicalState(
        ledger,
        instance_id,
        state.prize_instance_ids,
        state.face_up,
    )
