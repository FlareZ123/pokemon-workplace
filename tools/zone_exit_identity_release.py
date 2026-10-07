"""Release preserved zone-exit identities after their liveness obligations end."""

from __future__ import annotations

from collections.abc import Iterable

from identity_liveness import (
    IdentityReference,
    assess_dematerialization,
    dematerialize_if_safe,
)
from identity_materialization import assert_conserved
from stack_knockout_conservation import StackBoardMaterialState


def release_zone_exit_identity_group(
    state: StackBoardMaterialState,
    instance_ids: Iterable[str],
    *,
    references: Iterable[IdentityReference] = (),
) -> StackBoardMaterialState:
    """Atomically collapse one preserved zone-exit identity group.

    Every requested instance must pass the conservative liveness gate before
    any instance is collapsed. This keeps the release step transactional.
    """

    ids = tuple(instance_ids)
    if not ids:
        raise ValueError("instance_ids must be non-empty")
    if len(ids) != len(set(ids)):
        raise ValueError("instance_ids must be unique")

    references = tuple(references)
    assessments = tuple(
        assess_dematerialization(
            state.ledger,
            instance_id,
            references=references,
        )
        for instance_id in ids
    )
    blocked = tuple(row for row in assessments if not row.safe)
    if blocked:
        details = "; ".join(
            f"{row.instance_id}: {', '.join(row.blockers)}"
            for row in blocked
        )
        raise ValueError(f"zone-exit identity group is still live: {details}")

    ledger = state.ledger
    for instance_id in ids:
        ledger = dematerialize_if_safe(
            ledger,
            instance_id,
            references=references,
        )

    assert_conserved(state.ledger, ledger)
    return StackBoardMaterialState(ledger, state.board)
