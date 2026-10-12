"""Track match-local materialization IDs across release and zone movement.

IdentityLedger checks duplicate currently materialized instance IDs. A released
instance disappears from that ledger; without a separate lifetime record, its
identifier can be reused and accidentally match a stale semantic reference.

This wrapper guards a *closed transition path*: callers must continue passing
the returned provenance state instead of reconstructing it from the bare ledger.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from identity_liveness import IdentityReference, dematerialize_if_safe
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    materialize,
    move_instance,
)


@dataclass(frozen=True)
class IdentityProvenanceState:
    ledger: IdentityLedger
    ever_issued: frozenset[str]

    def __post_init__(self) -> None:
        live = {row.instance_id for row in self.ledger.instances}
        missing = live - self.ever_issued
        if missing:
            raise ValueError(
                f"live instance IDs missing from provenance: {sorted(missing)}"
            )


def begin_identity_provenance(
    ledger: IdentityLedger,
    *,
    known_prior_ids: Iterable[str] = (),
) -> IdentityProvenanceState:
    """Start tracking; supply all prior released IDs when adopting old state."""

    issued = frozenset(
        (*known_prior_ids, *(row.instance_id for row in ledger.instances))
    )
    if not issued or all(issued):
        return IdentityProvenanceState(ledger, issued)
    raise ValueError("issued instance IDs must be non-empty")


def materialize_unique(
    state: IdentityProvenanceState,
    *,
    card_class: str,
    card_name: str,
    source_zone: str,
    instance_id: str,
) -> IdentityProvenanceState:
    """Materialize only a never-before-issued match-local physical ID."""

    if instance_id in state.ever_issued:
        raise ValueError(
            f"physical instance ID was already issued: {instance_id!r}"
        )
    next_ledger = materialize(
        state.ledger,
        card_class=card_class,
        card_name=card_name,
        source_zone=source_zone,
        instance_id=instance_id,
    )
    assert_conserved(state.ledger, next_ledger)
    return IdentityProvenanceState(
        next_ledger,
        state.ever_issued | {instance_id},
    )


def move_instance_preserving_provenance(
    state: IdentityProvenanceState,
    instance_id: str,
    destination_zone: str,
    *,
    attached_to: str | None = None,
    board_object_id: str | None = None,
) -> IdentityProvenanceState:
    """Move an already tracked instance without resetting its identity epoch."""

    next_ledger = move_instance(
        state.ledger,
        instance_id,
        destination_zone,
        attached_to=attached_to,
        board_object_id=board_object_id,
    )
    assert_conserved(state.ledger, next_ledger)
    return IdentityProvenanceState(next_ledger, state.ever_issued)


def dematerialize_preserving_provenance(
    state: IdentityProvenanceState,
    instance_id: str,
    *,
    references: Iterable[IdentityReference] = (),
) -> IdentityProvenanceState:
    """Release a safe instance while retaining its identifier as a tombstone."""

    next_ledger = dematerialize_if_safe(
        state.ledger,
        instance_id,
        references=references,
    )
    return IdentityProvenanceState(next_ledger, state.ever_issued)
