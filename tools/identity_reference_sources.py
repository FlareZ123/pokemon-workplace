"""Derive liveness references from exact deck and Prize topology."""

from __future__ import annotations

from identity_liveness import IdentityReference
from prize_pending_take import PrizePendingTakeState
from top_prize_physical_bridge import TopPrizePhysicalState


def top_prize_identity_references(
    state: TopPrizePhysicalState,
) -> tuple[IdentityReference, ...]:
    """Name every instance whose exact identity is part of top/Prize topology."""

    rows = [
        IdentityReference(
            "deck_top",
            state.top_instance_id,
            "exact top-deck identity remains part of deck topology",
        )
    ]
    rows.extend(
        IdentityReference(
            f"prize_slot:{position}",
            instance_id,
            "exact Prize identity remains bound to a physical Prize position",
        )
        for position, instance_id in enumerate(state.prize_instance_ids)
    )
    return tuple(rows)


def pending_prize_identity_references(
    state: PrizePendingTakeState,
) -> tuple[IdentityReference, ...]:
    """Name exact top, remaining Prize slots, and pending Prize queue entries."""

    rows = list(top_prize_identity_references(state.physical))
    rows.extend(
        IdentityReference(
            f"prize_pending:{position}",
            pending.instance_id,
            "exact Prize identity remains in the pending Prize-resolution queue",
        )
        for position, pending in enumerate(state.pending)
    )
    return tuple(rows)
