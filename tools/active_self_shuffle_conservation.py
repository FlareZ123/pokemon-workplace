"""Physically conserve a self-shuffling Active Pokemon and every attached card.

For attacks such as Beheeyem's Mysterious Noise, the evolved Pokemon's full
stack and all attachments return to their owner's deck. Unlike a Knock Out,
this transition does not put cards into the discard pile or award Prizes.
Attack effects, turn scheduling, deck shuffling, and win/loss resolution remain
the responsibility of their existing owners.
"""

from __future__ import annotations

from dataclasses import replace

from board_position_state import validate_state
from identity_materialization import (
    assert_conserved,
    dematerialize,
    detach_instance,
    move_instance,
)
from stack_knockout_conservation import StackBoardMaterialState


def shuffle_active_and_attached_into_deck(
    state: StackBoardMaterialState,
    *,
    promote_id: str | None = None,
) -> StackBoardMaterialState | None:
    """Return a legal board/ledger transition or None for an invalid promotion.

    If the Active was the only Pokemon in play, the resulting board is None.
    No Prize is taken and attached Energy/Tools go to the deck with the stack.
    """
    board = state.board
    if board is None:
        return None

    active = board.get(board.active_id)
    if board.bench_ids:
        if promote_id not in board.bench_ids:
            return None
        remaining = tuple(
            pokemon for pokemon in board.pokemon
            if pokemon.pokemon_id != active.pokemon_id
        )
        after_board = replace(board, pokemon=remaining, active_id=promote_id)
        validate_state(after_board)
    else:
        if promote_id is not None:
            return None
        after_board = None

    ledger = state.ledger
    for card in active.stack:
        ledger = move_instance(ledger, card.card_id, "deck")
        ledger = dematerialize(ledger, card.card_id)
    for attachment in active.attachments:
        ledger = detach_instance(ledger, attachment.card_id, "deck")
        ledger = dematerialize(ledger, attachment.card_id)

    after = StackBoardMaterialState(ledger=ledger, board=after_board)
    assert_conserved(state.ledger, after.ledger)
    return after
