"""Committed play-event bridge across existing action-channel kernels."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from forced_supporter_execution import ForcedSupporterState
from stadium_entry_channels import StadiumEntryState
from supporter_play_event_history import SupporterExecutionState
from trainer_play_attempt_budget import QuotaTrainerKind, TrainerAttemptState


class PlayKind(str, Enum):
    SUPPORTER = "supporter"
    STADIUM = "stadium"


class PlayChannel(str, Enum):
    ORDINARY = "ordinary_play"
    FORCED = "forced_play"


@dataclass(frozen=True)
class CommittedPlayEvent:
    kind: PlayKind
    channel: PlayChannel
    turn_owner: str
    card_player: str
    decision_controller: str
    copy_id: str
    card_name: str
    consumed_ordinary_quota: bool

    @property
    def out_of_turn(self) -> bool:
        return self.turn_owner != self.card_player


def from_supporter_execution(
    before: SupporterExecutionState,
    after: SupporterExecutionState,
    *,
    player: str,
) -> CommittedPlayEvent | None:
    if len(after.play_events) != len(before.play_events) + 1:
        return None
    event = after.play_events[-1]
    return CommittedPlayEvent(
        PlayKind.SUPPORTER, PlayChannel.ORDINARY, player, player, player,
        event.copy_id, event.name, True,
    )


def from_trainer_attempt(
    before: TrainerAttemptState,
    after: TrainerAttemptState,
    *,
    player: str,
) -> CommittedPlayEvent | None:
    card = before.pending
    if card is None:
        return None
    if card.kind is QuotaTrainerKind.SUPPORTER:
        committed = after.successful_supporters == before.successful_supporters + 1
        kind = PlayKind.SUPPORTER
    else:
        committed = after.successful_stadium_plays == before.successful_stadium_plays + 1
        kind = PlayKind.STADIUM
    if not committed:
        return None
    return CommittedPlayEvent(
        kind, PlayChannel.ORDINARY, player, player, player,
        card.copy_id, card.name, True,
    )


def from_stadium_entry(
    before: StadiumEntryState,
    after: StadiumEntryState,
    *,
    player: str,
) -> CommittedPlayEvent | None:
    if after.budget.stadium_plays_used != before.budget.stadium_plays_used + 1:
        return None
    card = after.in_play
    if card is None:
        return None
    return CommittedPlayEvent(
        PlayKind.STADIUM, PlayChannel.ORDINARY, player, player, player,
        card.copy_id, card.name, True,
    )


def from_forced_supporter(
    state: ForcedSupporterState,
) -> CommittedPlayEvent | None:
    forced = state.event
    card = state.resolving_supporter
    if forced is None or card is None:
        return None
    return CommittedPlayEvent(
        PlayKind.SUPPORTER, PlayChannel.FORCED, forced.turn_owner,
        forced.card_player, forced.decision_controller, card.copy_id, card.name, False,
    )


def has_play_history(
    events: Iterable[CommittedPlayEvent],
    *,
    player: str,
    kind: PlayKind,
    name_contains: str | None = None,
) -> bool:
    for event in events:
        if event.card_player != player or event.kind is not kind:
            continue
        if name_contains is not None and name_contains not in event.card_name:
            continue
        return True
    return False
