"""Compose Prize replacement decisions with physical and observer transitions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from physical_pending_prize_batch_bridge import (
    PhysicalPendingBatchBeliefs,
    resolve_physical_next_pending_batch,
)
from prize_destination_overrides import (
    PrizeDestinationDecision,
    PrizeDestinationOverride,
    decide_prize_destination,
)
from prize_position_belief import PrizeGroup


@dataclass(frozen=True)
class PendingPrizeOverrideObserverDecision:
    decision: PrizeDestinationDecision
    after: PhysicalPendingBatchBeliefs | None

    @property
    def resolved(self) -> bool:
        return self.after is not None


def resolve_pending_override_with_observers(
    state: PhysicalPendingBatchBeliefs,
    overrides: Iterable[PrizeDestinationOverride],
    *,
    actor_id: str,
    group_by_card_class: Mapping[str, PrizeGroup],
    chosen_effect_id: str | None = None,
    ordinary_destination: str = "hand",
) -> PendingPrizeOverrideObserverDecision:
    """Resolve one queued Prize only once its destination is determined.

    Ordering authority belongs to the caller. For Lost Block plus Billowing
    Smoke, official guidance grants the choice to the Prize-taking player.
    """
    if not state.pending.pending:
        raise ValueError("no pending Prize remains")
    state.observers.belief_for(actor_id)
    decision = decide_prize_destination(
        overrides,
        ordinary_destination=ordinary_destination,
        chosen_effect_id=chosen_effect_id,
    )
    if decision.destination_zone is None:
        return PendingPrizeOverrideObserverDecision(decision, None)
    after = resolve_physical_next_pending_batch(
        state,
        actor_id=actor_id,
        destination_zone=decision.destination_zone,
        group_by_card_class=group_by_card_class,
    )
    return PendingPrizeOverrideObserverDecision(decision, after)
