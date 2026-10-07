"""Atomic Battle Compressor deck-to-discard Item transaction.

Battle Compressor Team Flare Gear:
"Search your deck for up to 3 cards and discard them. Shuffle your deck afterward."

This count-state adapter preserves the Item play gate, resolving-Trainer zone,
exact selected card classes, and per-class conservation. Deck order/shuffle
randomization belongs to a separate physical deck-top layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from discard_cost_witness import (
    DiscardCandidate,
    DiscardSelection,
    apply_discard_selection,
)
from trainer_search_transaction import (
    RESOLVING_TRAINER_ZONE,
    TrainerSearchExecutionState,
)


@dataclass(frozen=True)
class BattleCompressorTransaction:
    before: TrainerSearchExecutionState
    after: TrainerSearchExecutionState
    selection: DiscardSelection

    @property
    def cards_compressed(self) -> int:
        return self.selection.cost


def execute_battle_compressor(
    state: TrainerSearchExecutionState,
    *,
    action_card_class: str = "battle_compressor",
    candidates: Sequence[DiscardCandidate],
    selection: DiscardSelection,
) -> BattleCompressorTransaction:
    """Move 1-3 selected deck cards to discard and discard the played Item."""

    if not state.channels.item_play:
        raise ValueError("Item play is locked")
    if state.zones.count(action_card_class, "hand") < 1:
        raise ValueError("Battle Compressor is not in hand")
    if any(
        zone == RESOLVING_TRAINER_ZONE
        for _card_class, zone, _count in state.zones.counts
    ):
        raise ValueError("state already contains a resolving Trainer")
    if not 1 <= selection.cost <= 3:
        raise ValueError("Battle Compressor must select between 1 and 3 cards")

    working = state.zones.move(
        action_card_class,
        "hand",
        RESOLVING_TRAINER_ZONE,
    )
    available = {
        candidate.card_class: working.count(candidate.card_class, "deck")
        for candidate in candidates
    }
    for candidate, count in zip(candidates, selection.counts, strict=True):
        if count > available[candidate.card_class]:
            raise ValueError(
                f"selected too many deck copies of {candidate.card_class!r}"
            )

    compressed = apply_discard_selection(
        working,
        candidates,
        selection,
        source_zone="deck",
        destination_zone="discard",
    ).after
    after_zones = compressed.move(
        action_card_class,
        RESOLVING_TRAINER_ZONE,
        "discard",
    )

    classes = {
        card_class for card_class, _zone, _count in state.zones.counts
    } | {
        card_class for card_class, _zone, _count in after_zones.counts
    }
    for card_class in classes:
        if state.zones.total(card_class) != after_zones.total(card_class):
            raise AssertionError(f"card total changed for {card_class!r}")

    return BattleCompressorTransaction(
        before=state,
        after=TrainerSearchExecutionState(
            zones=after_zones,
            budget=state.budget,
            channels=state.channels,
        ),
        selection=selection,
    )
