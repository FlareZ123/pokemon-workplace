"""Union exact-identity owners at a physical/belief transition boundary.

A Prize instance can finish physical hand placement before every observer has
resolved a pending latent identity. Both independently owned references must be
consulted before that instance can be collapsed into an exchangeable count.
"""

from __future__ import annotations

from collections.abc import Iterable

from identity_liveness import IdentityReference
from identity_materialization import IdentityLedger
from identity_reference_sources import (
    pending_prize_belief_identity_references,
    pending_prize_identity_references,
    top_prize_identity_references,
)
from pending_prize_batch_identity_belief import ObserverPendingPrizeBatchBeliefs
from prize_pending_take import PrizePendingTakeState
from top_prize_physical_bridge import TopPrizePhysicalState


def collect_composite_identity_references(
    ledger: IdentityLedger,
    *,
    top_prize: TopPrizePhysicalState | None = None,
    pending_prize: PrizePendingTakeState | None = None,
    pending_beliefs: ObserverPendingPrizeBatchBeliefs | None = None,
    effect_references: Iterable[IdentityReference] = (),
) -> tuple[IdentityReference, ...]:
    """Collect all represented owners, rejecting stale and contradictory inputs.

    The caller supplies the current ledger. It may supply both top_prize and
    pending_prize if they refer to the same ledger generation. Beliefs may lag
    physical Prize resolution because the card's exact ID can remain a latent
    variable even after it enters hand. Such a lag is an intended live owner,
    rather than an inconsistency to discard.

    This is a conservative collector for the owners explicitly passed by its
    caller. A complete match engine must pass every active effect/history owner.
    """

    sources: list[tuple[IdentityReference, ...]] = []

    if top_prize is not None:
        if top_prize.ledger != ledger:
            raise ValueError("top_prize uses a stale or different identity ledger")
        sources.append(top_prize_identity_references(top_prize))

    if pending_prize is not None:
        if pending_prize.physical.ledger != ledger:
            raise ValueError("pending_prize uses a stale or different identity ledger")
        sources.append(pending_prize_identity_references(pending_prize))

    if pending_beliefs is not None:
        sources.append(pending_prize_belief_identity_references(pending_beliefs))

    sources.append(tuple(effect_references))

    by_id: dict[str, IdentityReference] = {}
    for source in sources:
        for reference in source:
            try:
                ledger.instance(reference.instance_id)
            except KeyError as exc:
                raise ValueError(
                    f"reference {reference.reference_id!r} points to "
                    f"absent instance {reference.instance_id!r}"
                ) from exc

            previous = by_id.get(reference.reference_id)
            if previous is not None:
                if previous != reference:
                    raise ValueError(
                        f"conflicting owners of reference_id "
                        f"{reference.reference_id!r}"
                    )
                continue
            by_id[reference.reference_id] = reference

    return tuple(by_id.values())
