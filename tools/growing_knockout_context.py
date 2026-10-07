"""Grow cross-player pending Knock Out membership before disposal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from cross_player_knockout_resolution import CrossPlayerKnockOutContext
from simultaneous_knockout_conservation import prepare_knock_out_batch
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class GrowingKnockOutContext:
    players: tuple[tuple[str, StackBoardMaterialState], ...]
    pending: tuple[tuple[str, tuple[str, ...]], ...]
    next_player_id: str

    def __post_init__(self) -> None:
        if len(self.players) != 2:
            raise ValueError("Pokemon TCG context requires exactly two players")
        player_ids = tuple(player_id for player_id, _state in self.players)
        if len(set(player_ids)) != 2:
            raise ValueError("player IDs must be unique")
        if self.next_player_id not in player_ids:
            raise ValueError("next_player_id must identify one player")

        pending_ids = tuple(player_id for player_id, _ids in self.pending)
        if set(pending_ids) != set(player_ids) or len(pending_ids) != 2:
            raise ValueError("pending membership must cover both players once")

        for player_id, ids in self.pending:
            if len(ids) != len(set(ids)):
                raise ValueError("pending Pokemon IDs must be unique")
            state = self.state_for(player_id)
            if state.board is None:
                if ids:
                    raise ValueError("terminal boards cannot have pending Pokemon")
                continue
            board_ids = {pokemon.pokemon_id for pokemon in state.board.pokemon}
            if not set(ids) <= board_ids:
                raise ValueError("pending membership contains unknown Pokemon")

    def state_for(self, player_id: str) -> StackBoardMaterialState:
        for current_id, state in self.players:
            if current_id == player_id:
                return state
        raise KeyError(player_id)

    def pending_for(self, player_id: str) -> tuple[str, ...]:
        for current_id, ids in self.pending:
            if current_id == player_id:
                return ids
        raise KeyError(player_id)


def begin_growing_knock_out_context(
    players: Mapping[str, StackBoardMaterialState],
    *,
    next_player_id: str,
    initial_knockouts: Mapping[str, Iterable[str]] | None = None,
) -> GrowingKnockOutContext | None:
    if len(players) != 2:
        return None

    initial = initial_knockouts or {}
    unknown_players = set(initial) - set(players)
    if unknown_players:
        return None

    pending = tuple(
        (player_id, tuple(initial.get(player_id, ())))
        for player_id in players
    )
    try:
        return GrowingKnockOutContext(
            tuple(players.items()),
            pending,
            next_player_id,
        )
    except ValueError:
        return None


def mark_additional_knock_out(
    context: GrowingKnockOutContext,
    *,
    player_id: str,
    pokemon_id: str,
) -> GrowingKnockOutContext | None:
    try:
        current = context.pending_for(player_id)
        state = context.state_for(player_id)
    except KeyError:
        return None

    if state.board is None:
        return None
    board_ids = {pokemon.pokemon_id for pokemon in state.board.pokemon}
    if pokemon_id not in board_ids:
        return None
    if pokemon_id in current:
        return context

    pending = tuple(
        (
            current_id,
            ids + (pokemon_id,) if current_id == player_id else ids,
        )
        for current_id, ids in context.pending
    )
    return GrowingKnockOutContext(
        context.players,
        pending,
        context.next_player_id,
    )


def to_cross_player_context(
    context: GrowingKnockOutContext,
) -> CrossPlayerKnockOutContext | None:
    prepared = []
    for player_id, state in context.players:
        ids = context.pending_for(player_id)
        if not ids:
            return None
        batch = prepare_knock_out_batch(state, ids)
        if batch is None:
            return None
        prepared.append((player_id, batch))

    return CrossPlayerKnockOutContext(
        tuple(prepared),
        next_player_id=context.next_player_id,
    )
