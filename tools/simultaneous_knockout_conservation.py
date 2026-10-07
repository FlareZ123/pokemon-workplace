"""Two-phase conservation model for simultaneous Knock Outs."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from board_position_state import BoardState, validate_state
from identity_materialization import (
    assert_conserved,
    dematerialize,
    detach_instance,
    move_instance,
)
from stack_knockout_conservation import StackBoardMaterialState

DISCARD = "discard"


@dataclass(frozen=True)
class PendingKnockOutBatch:
    """A pre-discard Knock Out batch whose cards remain in play for triggers."""

    state: StackBoardMaterialState
    knocked_out_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.state.board is None:
            raise ValueError("cannot prepare Knock Outs on a terminal board")
        if not self.knocked_out_ids:
            raise ValueError("Knock Out batch must be non-empty")
        if len(self.knocked_out_ids) != len(set(self.knocked_out_ids)):
            raise ValueError("Knock Out IDs must be unique")
        board_ids = {pokemon.pokemon_id for pokemon in self.state.board.pokemon}
        if not set(self.knocked_out_ids) <= board_ids:
            raise ValueError("Knock Out batch contains an unknown Pokemon")


def prepare_knock_out_batch(
    state: StackBoardMaterialState,
    pokemon_ids: Iterable[str],
) -> PendingKnockOutBatch | None:
    """Freeze a pre-discard batch without mutating board or identity state."""

    ids = tuple(pokemon_ids)
    try:
        return PendingKnockOutBatch(state, ids)
    except ValueError:
        return None


def discard_pending_knock_out_batch(
    pending: PendingKnockOutBatch,
    *,
    promote_id: str | None = None,
) -> StackBoardMaterialState | None:
    """Discard all members of one already-prepared Knock Out batch together.

    The caller should resolve any Knock Out-triggered effects before this
    transition. Promotion is selected only from Pokemon that survive the whole
    batch.
    """

    board = pending.state.board
    assert board is not None

    knocked_out = set(pending.knocked_out_ids)
    removed = tuple(
        pokemon
        for pokemon in board.pokemon
        if pokemon.pokemon_id in knocked_out
    )
    survivors = tuple(
        pokemon
        for pokemon in board.pokemon
        if pokemon.pokemon_id not in knocked_out
    )
    active_knocked_out = board.active_id in knocked_out

    if active_knocked_out:
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
            ledger = move_instance(ledger, card.card_id, DISCARD)
            ledger = dematerialize(ledger, card.card_id)
        for attachment in pokemon.attachments:
            ledger = detach_instance(ledger, attachment.card_id, DISCARD)
            ledger = dematerialize(ledger, attachment.card_id)

    next_state = StackBoardMaterialState(ledger, next_board)
    assert_conserved(pending.state.ledger, next_state.ledger)
    return next_state
