"""Resolution-order choice for one simultaneous Prize-taking batch."""

from __future__ import annotations

from dataclasses import dataclass

from prize_pending_take import PrizePendingTakeState


@dataclass(frozen=True)
class PendingPrizeBatchOrder:
    """Track unresolved siblings from one simultaneous Prize award."""

    state: PrizePendingTakeState
    unresolved_batch_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.unresolved_batch_ids:
            raise ValueError("simultaneous Prize batch must contain at least one card")
        if len(self.unresolved_batch_ids) != len(set(self.unresolved_batch_ids)):
            raise ValueError("batch instance IDs must be unique")

        pending_ids = {row.instance_id for row in self.state.pending}
        missing = set(self.unresolved_batch_ids) - pending_ids
        if missing:
            raise ValueError(
                "unresolved batch instances must still be pending: "
                f"{sorted(missing)}"
            )

    @classmethod
    def from_staged(
        cls,
        state: PrizePendingTakeState,
    ) -> "PendingPrizeBatchOrder":
        """Open an order-choice context after one simultaneous award is staged."""

        return cls(
            state,
            tuple(row.instance_id for row in state.pending),
        )

    def choose_next(self, instance_id: str) -> PrizePendingTakeState:
        """Move one unresolved sibling to the queue head when no nested work blocks it."""

        if instance_id not in self.unresolved_batch_ids:
            raise ValueError("chosen instance is not an unresolved member of this Prize batch")

        index = next(
            (
                index
                for index, row in enumerate(self.state.pending)
                if row.instance_id == instance_id
            ),
            None,
        )
        if index is None:
            raise ValueError("chosen batch instance is no longer pending")

        blocking = [
            row.instance_id
            for row in self.state.pending[:index]
            if row.instance_id not in self.unresolved_batch_ids
        ]
        if blocking:
            raise ValueError(
                "nested or foreign pending Prize work must resolve before "
                "returning to this simultaneous batch"
            )

        chosen = self.state.pending[index]
        pending = (
            (chosen,)
            + self.state.pending[:index]
            + self.state.pending[index + 1 :]
        )
        return PrizePendingTakeState(self.state.physical, pending)

    def advance_after_resolution(
        self,
        state: PrizePendingTakeState,
        *,
        resolved_instance_id: str,
    ) -> "PendingPrizeBatchOrder | None":
        """Remove one completed sibling while preserving nested queue barriers."""

        if resolved_instance_id not in self.unresolved_batch_ids:
            raise ValueError("resolved instance is not part of this Prize batch")

        resolved = state.physical.ledger.instance(resolved_instance_id)
        if resolved.zone in {"prize_pending", "resolving_trainer"}:
            raise ValueError("chosen Prize card has not finished resolving")

        remaining = tuple(
            instance_id
            for instance_id in self.unresolved_batch_ids
            if instance_id != resolved_instance_id
        )
        if not remaining:
            return None
        return PendingPrizeBatchOrder(state, remaining)

    def rebind(self, state: PrizePendingTakeState) -> "PendingPrizeBatchOrder":
        """Carry the same sibling-choice context after nested work advances."""

        return PendingPrizeBatchOrder(state, self.unresolved_batch_ids)
