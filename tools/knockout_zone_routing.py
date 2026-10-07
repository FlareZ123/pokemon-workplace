"""Route cards leaving a pending Knock Out batch to resolved zones."""

from __future__ import annotations

from dataclasses import replace
from typing import Mapping

from board_position_state import BoardState, validate_state
from identity_materialization import (
    assert_conserved,
    dematerialize,
    detach_instance,
    move_instance,
)
from simultaneous_knockout_conservation import PendingKnockOutBatch
from stack_knockout_conservation import StackBoardMaterialState

DEFAULT_DESTINATION = "discard"
BOARD_BOUND_ZONES = frozenset({"attached", "in_play"})


def discard_pending_with_zone_routes(
    pending: PendingKnockOutBatch,
    *,
    promote_id: str | None = None,
    destinations: Mapping[str, str] | None = None,
) -> StackBoardMaterialState | None:
    """Dispose a KO batch after triggers resolve per-instance destinations."""

    board = pending.state.board
    assert board is not None

    routes = dict(destinations or {})
    if any(
        not zone or zone in BOARD_BOUND_ZONES
        for zone in routes.values()
    ):
        return None

    knocked_out = set(pending.knocked_out_ids)
    removed = tuple(
        pokemon
        for pokemon in board.pokemon
        if pokemon.pokemon_id in knocked_out
    )
    removed_instance_ids = {
        card.card_id
        for pokemon in removed
        for card in pokemon.stack
    }
    removed_instance_ids.update(
        attachment.card_id
        for pokemon in removed
        for attachment in pokemon.attachments
    )
    if not set(routes) <= removed_instance_ids:
        return None

    survivors = tuple(
        pokemon
        for pokemon in board.pokemon
        if pokemon.pokemon_id not in knocked_out
    )
    if board.active_id in knocked_out:
        if not survivors:
            if promote_id is not None:
                return None
            next_board: BoardState | None = None
        else:
            survivor_ids = {pokemon.pokemon_id for pokemon in survivors}
            if promote_id not in survivor_ids:
                return None
            next_board = replace(
                board,
                pokemon=survivors,
                active_id=promote_id,
            )
            validate_state(next_board)
    else:
        if promote_id is not None:
            return None
        next_board = replace(board, pokemon=survivors)
        validate_state(next_board)

    ledger = pending.state.ledger
    for pokemon in removed:
        for card in pokemon.stack:
            destination = routes.get(card.card_id, DEFAULT_DESTINATION)
            ledger = move_instance(ledger, card.card_id, destination)
            ledger = dematerialize(ledger, card.card_id)
        for attachment in pokemon.attachments:
            destination = routes.get(
                attachment.card_id,
                DEFAULT_DESTINATION,
            )
            ledger = detach_instance(
                ledger,
                attachment.card_id,
                destination,
            )
            ledger = dematerialize(ledger, attachment.card_id)

    next_state = StackBoardMaterialState(ledger, next_board)
    assert_conserved(pending.state.ledger, next_state.ledger)
    return next_state
