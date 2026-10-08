"""Venomoth's Dizzying Wind reuses the verified pre-use Trainer gate.

The official Japanese Q&A resolves the Supporter retry on tails. This bridge
records the attempted card identity without claiming a successful card use.
"""
from __future__ import annotations

from dataclasses import dataclass

from committed_play_event import CommittedPlayEvent, PlayKind, from_trainer_attempt
from trainer_play_attempt_budget import (
    QuotaTrainerKind,
    TrainerAttemptState,
    begin_trainer_attempt,
    fail_quaking_fist_gate,
    pass_quaking_fist_gate,
)


@dataclass(frozen=True)
class FailedTrainerAttempt:
    copy_id: str
    card_name: str
    kind: PlayKind
    player: str
    gate_source: str


@dataclass(frozen=True)
class GatedTrainerResolution:
    after: TrainerAttemptState
    committed_play: CommittedPlayEvent | None
    failed_attempt: FailedTrainerAttempt | None


def failed_trainer_attempt_event(
    before: TrainerAttemptState,
    after: TrainerAttemptState,
    *,
    player: str,
    gate_source: str,
) -> FailedTrainerAttempt:
    """Prove the failed source card was discarded without consuming a quota."""
    card = before.pending
    if card is None or not player or not gate_source:
        raise ValueError("expected identified pending Trainer and gate")
    if (
        after.pending is not None
        or after.hand != before.hand
        or after.discard != before.discard + (card,)
        or after.budget != before.budget
        or after.successful_supporters != before.successful_supporters
        or after.successful_stadium_plays != before.successful_stadium_plays
        or after.stadium_in_play != before.stadium_in_play
    ):
        raise ValueError("not an unchanged-quota failed Trainer attempt")
    return FailedTrainerAttempt(
        card.copy_id, card.name, PlayKind(card.kind.value), player, gate_source,
    )


def resolve_dizzying_wind_supporter(
    before: TrainerAttemptState,
    *,
    copy_id: str,
    heads: bool,
    player: str,
) -> GatedTrainerResolution | None:
    """Execute a bounded Supporter coin gate using shared transaction semantics.

    The card body is modeled as a successful-use transition only on heads.
    """
    attempt = begin_trainer_attempt(before, copy_id)
    if attempt is None:
        return None
    if attempt.pending is None or attempt.pending.kind is not QuotaTrainerKind.SUPPORTER:
        return None
    after = (
        pass_quaking_fist_gate(attempt)
        if heads else fail_quaking_fist_gate(attempt)
    )
    assert after is not None
    if heads:
        event = from_trainer_attempt(attempt, after, player=player)
        assert event is not None
        return GatedTrainerResolution(after, event, None)
    failed = failed_trainer_attempt_event(
        attempt, after, player=player, gate_source="venomoth_dizzying_wind",
    )
    return GatedTrainerResolution(after, None, failed)
