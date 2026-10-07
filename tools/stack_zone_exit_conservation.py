"""Conserve a complete Pokemon stack when its board object leaves play.

This transition family is for effects that put or shuffle a Pokemon in play into
an ordinary zone. Previous Evolution cards follow the Pokemon. Attached cards
leave their attachment relations and can use a different resolved destination,
which distinguishes Scoop Up Cyclone / Cassius style effects from AZ style
effects.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from board_position_state import BoardPokemon, BoardState, validate_state
from identity_materialization import (
    assert_conserved,
    dematerialize,
    detach_instance,
    move_instance,
)
from stack_knockout_conservation import StackBoardMaterialState


BOARD_RELATION_ZONES = frozenset({"in_play", "attached"})


@dataclass(frozen=True)
class ZoneExitTransition:
    state: StackBoardMaterialState
    pokemon_card_ids: tuple[str, ...]
    attachment_card_ids: tuple[str, ...]


def _validate_destination(zone: str) -> None:
    if not zone:
        raise ValueError("destination zone must be non-empty")
    if zone in BOARD_RELATION_ZONES:
        raise ValueError("zone-exit destination must be off the board")


def _remove_board_object(
    board: BoardState,
    pokemon_id: str,
    *,
    promote_id: str | None,
) -> tuple[BoardState | None, BoardPokemon] | None:
    try:
        pokemon = board.get(pokemon_id)
    except StopIteration:
        return None

    remaining = tuple(
        row for row in board.pokemon
        if row.pokemon_id != pokemon_id
    )

    if pokemon_id == board.active_id:
        if not remaining:
            if promote_id is not None:
                return None
            return None, pokemon

        if promote_id not in board.bench_ids:
            return None

        next_board = replace(
            board,
            pokemon=remaining,
            active_id=promote_id,
        )
        validate_state(next_board)
        return next_board, pokemon

    if promote_id is not None:
        return None

    next_board = replace(board, pokemon=remaining)
    validate_state(next_board)
    return next_board, pokemon


def leave_play_with_conservation(
    state: StackBoardMaterialState,
    pokemon_id: str,
    *,
    pokemon_destination: str,
    attachment_destination: str,
    promote_id: str | None = None,
    preserve_identity: bool = False,
) -> ZoneExitTransition | None:
    """Move one whole Pokemon object out of play while conserving every card.

    All physical Pokemon cards in the evolution stack use pokemon_destination.
    Every attached physical card uses attachment_destination. The caller
    supplies resolved card semantics, so the same mechanical transition can
    represent Scoop Up Cyclone, Cassius, and AZ.

    preserve_identity keeps off-board physical instances materialized. This is
    useful while an enclosing effect still refers to a specific moved card.
    When false, completed off-board copies rejoin their exchangeable zone
    counts.
    """

    _validate_destination(pokemon_destination)
    _validate_destination(attachment_destination)

    if state.board is None:
        return None

    removed = _remove_board_object(
        state.board,
        pokemon_id,
        promote_id=promote_id,
    )
    if removed is None:
        return None

    board, pokemon = removed
    pokemon_card_ids = tuple(card.card_id for card in pokemon.stack)
    attachment_card_ids = tuple(
        card.card_id for card in pokemon.attachments
    )

    ledger = state.ledger

    for instance_id in pokemon_card_ids:
        ledger = move_instance(
            ledger,
            instance_id,
            pokemon_destination,
        )
        if not preserve_identity:
            ledger = dematerialize(ledger, instance_id)

    for instance_id in attachment_card_ids:
        ledger = detach_instance(
            ledger,
            instance_id,
            attachment_destination,
        )
        if not preserve_identity:
            ledger = dematerialize(ledger, instance_id)

    next_state = StackBoardMaterialState(ledger, board)
    assert_conserved(state.ledger, next_state.ledger)

    return ZoneExitTransition(
        next_state,
        pokemon_card_ids,
        attachment_card_ids,
    )
