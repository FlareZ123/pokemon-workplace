"""Cross-player promotion ordering after simultaneous Active Knock Outs."""

from __future__ import annotations

from dataclasses import dataclass

from simultaneous_knockout_conservation import (
    PendingKnockOutBatch,
    discard_pending_knock_out_batch,
)
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class CrossPlayerKnockOutContext:
    """Two pending KO batches plus sequential promotion decisions."""

    players: tuple[tuple[str, PendingKnockOutBatch], ...]
    next_player_id: str
    promotions: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if len(self.players) != 2:
            raise ValueError("Pokemon TCG context requires exactly two players")
        player_ids = tuple(player_id for player_id, _pending in self.players)
        if len(set(player_ids)) != 2:
            raise ValueError("player IDs must be unique")
        if self.next_player_id not in player_ids:
            raise ValueError("next_player_id must identify one player")
        promoted_players = tuple(player_id for player_id, _ in self.promotions)
        if len(promoted_players) != len(set(promoted_players)):
            raise ValueError("a player cannot choose promotion twice")
        if any(player_id not in player_ids for player_id in promoted_players):
            raise ValueError("promotion contains unknown player")

    def pending_for(self, player_id: str) -> PendingKnockOutBatch:
        for current_id, pending in self.players:
            if current_id == player_id:
                return pending
        raise KeyError(player_id)


@dataclass(frozen=True)
class CrossPlayerResolvedState:
    players: tuple[tuple[str, StackBoardMaterialState], ...]

    def state_for(self, player_id: str) -> StackBoardMaterialState:
        for current_id, state in self.players:
            if current_id == player_id:
                return state
        raise KeyError(player_id)


def _surviving_ids(pending: PendingKnockOutBatch) -> tuple[str, ...]:
    board = pending.state.board
    assert board is not None
    knocked_out = set(pending.knocked_out_ids)
    return tuple(
        pokemon.pokemon_id
        for pokemon in board.pokemon
        if pokemon.pokemon_id not in knocked_out
    )


def _requires_promotion(pending: PendingKnockOutBatch) -> bool:
    board = pending.state.board
    assert board is not None
    return (
        board.active_id in set(pending.knocked_out_ids)
        and bool(_surviving_ids(pending))
    )


def promotion_order(
    context: CrossPlayerKnockOutContext,
) -> tuple[str, ...]:
    """Return only players who need a promotion, in legal decision order."""

    requiring = tuple(
        player_id
        for player_id, pending in context.players
        if _requires_promotion(pending)
    )
    if len(requiring) <= 1:
        return requiring

    other = next(
        player_id
        for player_id in requiring
        if player_id != context.next_player_id
    )
    return (context.next_player_id, other)


def next_promotion_player(
    context: CrossPlayerKnockOutContext,
) -> str | None:
    decided = {player_id for player_id, _ in context.promotions}
    for player_id in promotion_order(context):
        if player_id not in decided:
            return player_id
    return None


def choose_promotion(
    context: CrossPlayerKnockOutContext,
    *,
    player_id: str,
    pokemon_id: str,
) -> CrossPlayerKnockOutContext | None:
    """Record exactly the next legal promotion decision."""

    if next_promotion_player(context) != player_id:
        return None

    pending = context.pending_for(player_id)
    if pokemon_id not in _surviving_ids(pending):
        return None

    return CrossPlayerKnockOutContext(
        context.players,
        context.next_player_id,
        context.promotions + ((player_id, pokemon_id),),
    )


def resolve_cross_player_knock_out(
    context: CrossPlayerKnockOutContext,
) -> CrossPlayerResolvedState | None:
    """Dispose both batches after every required promotion has been chosen."""

    if next_promotion_player(context) is not None:
        return None

    promotions = dict(context.promotions)
    resolved: list[tuple[str, StackBoardMaterialState]] = []
    for player_id, pending in context.players:
        state = discard_pending_knock_out_batch(
            pending,
            promote_id=promotions.get(player_id),
        )
        if state is None:
            return None
        resolved.append((player_id, state))

    return CrossPlayerResolvedState(tuple(resolved))
