"""Cross-player promotion ordering after simultaneous non-Knock-Out zone exits."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from promotion_pending_conservation import PromotionPendingState
from stack_knockout_conservation import StackBoardMaterialState
from stack_zone_exit_conservation import leave_play_before_promotion


class ZoneExitStage(str, Enum):
    AFTER_EXIT = "after_exit"
    PROMOTION = "promotion"
    TERMINAL = "terminal"


@dataclass(frozen=True)
class CrossPlayerZoneExitContext:
    """Two post-exit player states plus effect-defined promotion order."""

    players: tuple[tuple[str, PromotionPendingState], ...]
    first_player_id: str
    stage: ZoneExitStage = ZoneExitStage.AFTER_EXIT

    def __post_init__(self) -> None:
        if len(self.players) != 2:
            raise ValueError("Pokemon TCG context requires exactly two players")
        ids = tuple(player_id for player_id, _state in self.players)
        if len(set(ids)) != 2 or any(not player_id for player_id in ids):
            raise ValueError("player IDs must be two distinct non-empty values")
        if self.first_player_id not in ids:
            raise ValueError("first_player_id must identify one player")

    def state_for(self, player_id: str) -> PromotionPendingState:
        for current_id, state in self.players:
            if current_id == player_id:
                return state
        raise KeyError(player_id)


def prepare_simultaneous_active_exit(
    players: tuple[tuple[str, StackBoardMaterialState], ...],
    *,
    pokemon_destination: str,
    attachment_destination: str,
    first_player_id: str,
    preserve_identity: bool = False,
) -> CrossPlayerZoneExitContext | None:
    """Remove both current Active Pokemon before any replacement is chosen."""

    if len(players) != 2:
        return None
    ids = tuple(player_id for player_id, _state in players)
    if len(set(ids)) != 2 or first_player_id not in ids:
        return None

    pending_players: list[tuple[str, PromotionPendingState]] = []
    for player_id, state in players:
        if state.board is None:
            return None
        active_id = state.board.active_id
        moved = leave_play_before_promotion(
            state,
            active_id,
            pokemon_destination=pokemon_destination,
            attachment_destination=attachment_destination,
            preserve_identity=preserve_identity,
        )
        if moved is None:
            return None
        pending_players.append((player_id, moved.state))

    return CrossPlayerZoneExitContext(
        tuple(pending_players),
        first_player_id,
    )


def advance_after_exit(
    context: CrossPlayerZoneExitContext,
    *,
    game_continues: bool,
) -> CrossPlayerZoneExitContext | None:
    """Open effect-defined promotions only after terminal-state evaluation."""

    if context.stage != ZoneExitStage.AFTER_EXIT:
        return None
    return replace(
        context,
        stage=(
            ZoneExitStage.PROMOTION
            if game_continues
            else ZoneExitStage.TERMINAL
        ),
    )


def promotion_order(
    context: CrossPlayerZoneExitContext,
) -> tuple[str, ...]:
    requiring = tuple(
        player_id
        for player_id, state in context.players
        if state.requires_promotion
    )
    if len(requiring) <= 1:
        return requiring
    if context.first_player_id not in requiring:
        return requiring
    other = next(
        player_id
        for player_id in requiring
        if player_id != context.first_player_id
    )
    return (context.first_player_id, other)


def next_promotion_player(
    context: CrossPlayerZoneExitContext,
) -> str | None:
    if context.stage != ZoneExitStage.PROMOTION:
        return None
    for player_id in promotion_order(context):
        if context.state_for(player_id).requires_promotion:
            return player_id
    return None


def choose_promotion(
    context: CrossPlayerZoneExitContext,
    *,
    player_id: str,
    pokemon_id: str,
) -> CrossPlayerZoneExitContext | None:
    """Apply exactly the next legal effect-ordered replacement choice."""

    if next_promotion_player(context) != player_id:
        return None

    chosen = context.state_for(player_id).with_active(pokemon_id)
    if chosen is None:
        return None

    players = tuple(
        (
            current_id,
            chosen if current_id == player_id else current_state,
        )
        for current_id, current_state in context.players
    )
    return replace(context, players=players)


def finalize_promotions(
    context: CrossPlayerZoneExitContext,
) -> tuple[tuple[str, StackBoardMaterialState], ...] | None:
    if context.stage != ZoneExitStage.PROMOTION:
        return None
    if next_promotion_player(context) is not None:
        return None

    resolved: list[tuple[str, StackBoardMaterialState]] = []
    for player_id, state in context.players:
        ordinary = state.to_stack_state()
        if ordinary is None:
            return None
        resolved.append((player_id, ordinary))
    return tuple(resolved)
