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
from committed_play_event import CommittedPlayEvent, PlayKind, has_play_history



@dataclass(frozen=True)
class UnmaterializedPlay:
    """Card class/name and copy count known, physical instance identities unknown."""
    player: str
    kind: PlayKind
    card_name: str
    copies: int

    def __post_init__(self) -> None:
        if not self.player or not self.card_name or self.copies < 1:
            raise ValueError("unmaterialized play needs player, card and positive count")


@dataclass(frozen=True)
class JournalBoundary:
    sequence: int
    event_id: str
    description: str
    player_board: BoardState
    opponent_board: BoardState
    stadium_name: str | None
    play_batch: tuple[CommittedPlayEvent, ...]
    lock_state: AbilityLockCausalState
    play_record_complete: bool = True
    unmaterialized_plays: tuple[UnmaterializedPlay, ...] = ()

    @property
    def committed_play(self) -> CommittedPlayEvent | None:
        return self.play_batch[0] if len(self.play_batch) == 1 else None


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
            event
            for boundary in self.boundaries
            for event in boundary.play_batch
        )

    @property
    def play_history_complete(self) -> bool:
        """Whether exact physical copy IDs are recorded at every boundary."""
        return all(boundary.play_record_complete for boundary in self.boundaries)

    @property
    def occurrence_history_complete(self) -> bool:
        """Whether all submitted boundaries identify every play's name and kind."""
        return all(
            boundary.play_record_complete or bool(boundary.unmaterialized_plays)
            for boundary in self.boundaries
        )

    @property
    def unmaterialized_plays(self) -> tuple[UnmaterializedPlay, ...]:
        return tuple(
            event
            for boundary in self.boundaries
            for event in boundary.unmaterialized_plays
        )

    def queried_play(
        self,
        *,
        player: str,
        kind: PlayKind,
        name_contains: str | None = None,
    ) -> bool | None:
        """Occurrence exists, absent, or cannot be decided from source evidence."""
        if has_play_history(
            self.committed_plays, player=player, kind=kind,
            name_contains=name_contains,
        ):
            return True
        if any(
            event.player == player and event.kind is kind
            and (name_contains is None or name_contains in event.card_name)
            for event in self.unmaterialized_plays
        ):
            return True
        return False if self.occurrence_history_complete else None


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
    committed_plays: tuple[CommittedPlayEvent, ...] = (),
    play_record_complete: bool = True,
    unmaterialized_plays: tuple[UnmaterializedPlay, ...] = (),
) -> CausalEventJournal:
    """Fold exactly one ordered boundary, rejecting stale/duplicate submissions.

    Boards and play events must already have passed their producing kernels'
    legality checks. Recording a boundary does not itself certify event coverage.
    """
    if journal.revision != expected_revision:
        raise ValueError("stale journal revision")
    if play_record_complete and unmaterialized_plays:
        raise ValueError("unmaterialized plays require partial physical identity coverage")
    if not play_record_complete and (committed_play is not None or committed_plays):
        raise ValueError("partial play capture cannot claim committed cards")
    if committed_play is not None and committed_plays:
        raise ValueError("choose a single play or a play batch")
    batch = (committed_play,) if committed_play is not None else committed_plays
    if len({event.copy_id for event in batch}) != len(batch):
        raise ValueError("duplicate physical card in play batch")
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
        stadium_name, batch, lock, play_record_complete, unmaterialized_plays,
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
            committed_plays=step.play_batch,
            play_record_complete=step.play_record_complete,
            unmaterialized_plays=step.unmaterialized_plays,
        )
        if replayed.boundaries[-1] != step:
            raise AssertionError(f"lock or play event divergence at {step.event_id}")
    return replayed
