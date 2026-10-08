"""Replayable event-boundary journal for independent play and lock histories.

The caller supplies each validated mechanically relevant board transition. This
layer records it and folds continuous Ability-lock precedence at that boundary.
It cannot infer an omitted intermediate event from endpoint snapshots.
"""
from __future__ import annotations

from dataclasses import dataclass

from ability_lock_causal_state import (
    AbilityLockCausalState,
    advance_lock_state,
    initialize_setup_lock_state,
    initialize_snapshot_lock_state,
)
from board_object_kernel import BoardState
from committed_play_event import CommittedPlayEvent


@dataclass(frozen=True)
class JournalBoundary:
    sequence: int
    event_id: str
    description: str
    player_board: BoardState
    opponent_board: BoardState
    stadium_name: str | None
    committed_play: CommittedPlayEvent | None
    lock_state: AbilityLockCausalState


@dataclass(frozen=True)
class CausalEventJournal:
    initial_player_board: BoardState
    initial_opponent_board: BoardState
    initial_stadium_name: str | None
    first_player_owner: str | None
    initial_lock_state: AbilityLockCausalState
    boundaries: tuple[JournalBoundary, ...] = ()

    @property
    def revision(self) -> int:
        return len(self.boundaries)

    @property
    def lock_state(self) -> AbilityLockCausalState:
        return self.boundaries[-1].lock_state if self.boundaries else self.initial_lock_state

    @property
    def committed_plays(self) -> tuple[CommittedPlayEvent, ...]:
        return tuple(
            boundary.committed_play
            for boundary in self.boundaries
            if boundary.committed_play is not None
        )


def begin_journal(
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_name: str | None = None,
    first_player_owner: str | None = None,
) -> CausalEventJournal:
    player_board.validate()
    opponent_board.validate()
    if first_player_owner is None:
        lock = initialize_snapshot_lock_state(
            player_board, opponent_board, stadium_name=stadium_name,
        )
    else:
        if first_player_owner not in {"player", "opponent"}:
            raise ValueError("first_player_owner must be 'player' or 'opponent'")
        lock = initialize_setup_lock_state(
            player_board, opponent_board, first_player_owner=first_player_owner,
            stadium_name=stadium_name,
        )
    return CausalEventJournal(
        player_board, opponent_board, stadium_name, first_player_owner, lock,
    )


def append_boundary(
    journal: CausalEventJournal,
    *,
    expected_revision: int,
    event_id: str,
    description: str,
    player_board: BoardState,
    opponent_board: BoardState,
    stadium_name: str | None = None,
    committed_play: CommittedPlayEvent | None = None,
) -> CausalEventJournal:
    """Fold exactly one ordered boundary, rejecting stale/duplicate submissions.

    Boards and play events must already have passed their producing kernels'
    legality checks. Recording a boundary does not itself certify event coverage.
    """
    if journal.revision != expected_revision:
        raise ValueError("stale journal revision")
    if not event_id or not description:
        raise ValueError("event_id and description must be nonempty")
    if any(step.event_id == event_id for step in journal.boundaries):
        raise ValueError("duplicate event_id")
    player_board.validate()
    opponent_board.validate()
    lock = advance_lock_state(
        journal.lock_state, player_board, opponent_board, stadium_name=stadium_name,
    )
    step = JournalBoundary(
        journal.revision + 1, event_id, description, player_board, opponent_board,
        stadium_name, committed_play, lock,
    )
    from dataclasses import replace
    return replace(journal, boundaries=journal.boundaries + (step,))


def replay_journal(journal: CausalEventJournal) -> CausalEventJournal:
    """Recompute every intermediate lock state and play event from the log."""
    replayed = begin_journal(
        journal.initial_player_board, journal.initial_opponent_board,
        stadium_name=journal.initial_stadium_name,
        first_player_owner=journal.first_player_owner,
    )
    if replayed.initial_lock_state != journal.initial_lock_state:
        raise AssertionError("initial lock state differs on replay")
    for step in journal.boundaries:
        replayed = append_boundary(
            replayed, expected_revision=replayed.revision, event_id=step.event_id,
            description=step.description, player_board=step.player_board,
            opponent_board=step.opponent_board, stadium_name=step.stadium_name,
            committed_play=step.committed_play,
        )
        if replayed.boundaries[-1] != step:
            raise AssertionError(f"lock or play event divergence at {step.event_id}")
    return replayed
