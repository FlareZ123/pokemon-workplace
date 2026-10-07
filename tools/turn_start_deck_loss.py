"""Turn-start deck-loss eligibility over canonical physical deck size."""

from __future__ import annotations

from dataclasses import dataclass

from deck_search_shuffle_topology import SearchableDeckPhysicalState
from identity_materialization import IdentityLedger
from physical_deck_projection import (
    ExactTopDrawTransition,
    draw_exact_top_to_hand,
    physical_deck_size,
)
from top_prize_physical_bridge import TopPrizePhysicalState


def deck_empty_for_turn_start_loss(ledger: IdentityLedger) -> bool:
    """Return whether no physical card remains available in the deck."""

    return physical_deck_size(ledger) == 0


@dataclass(frozen=True)
class TurnStartExactDraw:
    draw: ExactTopDrawTransition

    @property
    def after(self) -> SearchableDeckPhysicalState:
        return self.draw.after


def resolve_exact_top_turn_start_draw(
    state: TopPrizePhysicalState,
) -> TurnStartExactDraw | None:
    """Draw the exact materialized top card when the physical deck is nonempty."""

    if deck_empty_for_turn_start_loss(state.ledger):
        return None
    return TurnStartExactDraw(draw_exact_top_to_hand(state))
