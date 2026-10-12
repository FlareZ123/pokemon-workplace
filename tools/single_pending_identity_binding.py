"""Bind one latent pending-Prize belief to its physical instance identity.

The single-Prize observer belief intentionally carries group distributions only.
A separate binding retains the source instance ID when physical Prize placement
resolves before observer-side pending evidence finishes resolving.
"""

from __future__ import annotations

from dataclasses import dataclass

from identity_liveness import IdentityReference
from pending_prize_identity_belief import ObserverPendingPrizeBeliefs
from prize_pending_take import PrizePendingTakeState


@dataclass(frozen=True)
class BoundSinglePendingPrizeIdentity:
    instance_id: str
    beliefs: ObserverPendingPrizeBeliefs

    def __post_init__(self) -> None:
        if not self.instance_id:
            raise ValueError("pending instance ID must be non-empty")


def bind_single_pending_prize_identity(
    state: PrizePendingTakeState,
    beliefs: ObserverPendingPrizeBeliefs,
) -> BoundSinglePendingPrizeIdentity:
    """Match a single physical pending Prize with its observer belief state."""

    if len(state.pending) != 1:
        raise ValueError("single pending belief requires exactly one queued Prize")

    for _observer_id, belief in beliefs.beliefs:
        if belief.face_up != state.physical.face_up:
            raise ValueError("belief Prize visibility disagrees with physical state")

    return BoundSinglePendingPrizeIdentity(state.pending[0].instance_id, beliefs)


def single_pending_identity_references(
    state: BoundSinglePendingPrizeIdentity,
) -> tuple[IdentityReference, ...]:
    """Keep exact identity live until the bound pending belief is resolved."""

    return (
        IdentityReference(
            "belief:single_prize_pending",
            state.instance_id,
            "single-pending observer belief still owns this physical instance",
        ),
    )
