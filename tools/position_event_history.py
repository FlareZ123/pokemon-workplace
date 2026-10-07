"""Turn-scoped physical position events derived from conserved board states."""

from __future__ import annotations

from dataclasses import dataclass

from board_object_kernel import BoardState


ACTIVE = "active"
BENCH = "bench"


@dataclass(frozen=True)
class PositionEvent:
    turn_player_id: str
    board_owner_id: str
    turn_index: int
    object_id: str
    from_position: str
    to_position: str

    def __post_init__(self) -> None:
        if not self.turn_player_id or not self.board_owner_id or not self.object_id:
            raise ValueError("position event identifiers must be non-empty")
        if self.turn_index < 0:
            raise ValueError("turn_index must be non-negative")
        if {self.from_position, self.to_position} != {ACTIVE, BENCH}:
            raise ValueError("position event must cross Active/Bench")


@dataclass(frozen=True)
class CompletedTurnPositions:
    player_id: str
    turn_index: int
    events: tuple[PositionEvent, ...]


@dataclass(frozen=True)
class TurnPositionHistory:
    current_player: str
    turn_index: int = 0
    current_events: tuple[PositionEvent, ...] = ()
    last_completed_turns: tuple[CompletedTurnPositions, ...] = ()

    def __post_init__(self) -> None:
        if not self.current_player:
            raise ValueError("current_player must be non-empty")
        if self.turn_index < 0:
            raise ValueError("turn_index must be non-negative")
        if any(
            event.turn_player_id != self.current_player
            or event.turn_index != self.turn_index
            for event in self.current_events
        ):
            raise ValueError("current events must belong to the current turn")
        players = [row.player_id for row in self.last_completed_turns]
        if len(players) != len(set(players)):
            raise ValueError("only one completed turn record per player is retained")

    def last_turn_for(self, player_id: str) -> CompletedTurnPositions | None:
        return next(
            (row for row in self.last_completed_turns if row.player_id == player_id),
            None,
        )


def _position(board: BoardState, object_id: str) -> str | None:
    if object_id == board.active_id:
        return ACTIVE
    if object_id in board.bench_ids:
        return BENCH
    return None


def derive_position_events(
    before: BoardState,
    after: BoardState,
    *,
    turn_player_id: str,
    board_owner_id: str,
    turn_index: int,
) -> tuple[PositionEvent, ...]:
    """Return Active/Bench crossings for physical objects present in both states."""

    before_ids = {row.object_id for row in before.objects}
    after_ids = {row.object_id for row in after.objects}
    shared = before_ids & after_ids

    events: list[PositionEvent] = []
    for object_id in sorted(shared):
        old = _position(before, object_id)
        new = _position(after, object_id)
        if old is None or new is None or old == new:
            continue
        events.append(
            PositionEvent(
                turn_player_id=turn_player_id,
                board_owner_id=board_owner_id,
                turn_index=turn_index,
                object_id=object_id,
                from_position=old,
                to_position=new,
            )
        )
    return tuple(events)


def record_board_transition(
    history: TurnPositionHistory,
    *,
    board_owner_id: str,
    before: BoardState,
    after: BoardState,
) -> TurnPositionHistory:
    events = derive_position_events(
        before,
        after,
        turn_player_id=history.current_player,
        board_owner_id=board_owner_id,
        turn_index=history.turn_index,
    )
    return TurnPositionHistory(
        current_player=history.current_player,
        turn_index=history.turn_index,
        current_events=history.current_events + events,
        last_completed_turns=history.last_completed_turns,
    )


def moved_bench_to_active_this_turn(
    history: TurnPositionHistory,
    *,
    board_owner_id: str,
    object_id: str,
) -> bool:
    return any(
        event.board_owner_id == board_owner_id
        and event.object_id == object_id
        and event.from_position == BENCH
        and event.to_position == ACTIVE
        for event in history.current_events
    )


def moved_bench_to_active_during_last_turn(
    history: TurnPositionHistory,
    *,
    turn_player_id: str,
    board_owner_id: str,
    object_id: str | None = None,
) -> bool:
    completed = history.last_turn_for(turn_player_id)
    if completed is None:
        return False
    return any(
        event.board_owner_id == board_owner_id
        and (object_id is None or event.object_id == object_id)
        and event.from_position == BENCH
        and event.to_position == ACTIVE
        for event in completed.events
    )


def advance_position_turn(
    history: TurnPositionHistory,
    *,
    next_player: str,
) -> TurnPositionHistory:
    if not next_player:
        raise ValueError("next_player must be non-empty")

    completed = CompletedTurnPositions(
        player_id=history.current_player,
        turn_index=history.turn_index,
        events=history.current_events,
    )
    by_player = {row.player_id: row for row in history.last_completed_turns}
    by_player[history.current_player] = completed

    return TurnPositionHistory(
        current_player=next_player,
        turn_index=history.turn_index + 1,
        current_events=(),
        last_completed_turns=tuple(by_player[key] for key in sorted(by_player)),
    )
