"""Atomic same-player batch conservation for non-Knock-Out Pokemon exits."""

from __future__ import annotations

from dataclasses import dataclass

from promotion_pending_conservation import PromotionPendingState
from stack_knockout_conservation import StackBoardMaterialState
from stack_zone_exit_conservation import (
    route_removed_pokemon_cards,
    validate_zone_exit_destination,
)


@dataclass(frozen=True)
class BatchZoneExitTransition:
    state: PromotionPendingState
    pokemon_ids: tuple[str, ...]
    pokemon_card_ids: tuple[str, ...]
    attachment_card_ids: tuple[str, ...]


def leave_play_batch_before_promotion(
    state: StackBoardMaterialState,
    pokemon_ids: tuple[str, ...],
    *,
    pokemon_destination: str,
    attachment_destination: str,
    preserve_identity: bool = False,
) -> BatchZoneExitTransition | None:
    """Remove a resolved set of board objects atomically before any promotion."""

    validate_zone_exit_destination(pokemon_destination)
    validate_zone_exit_destination(attachment_destination)

    if state.board is None:
        return None
    if len(pokemon_ids) != len(set(pokemon_ids)):
        return None

    board = state.board
    board_by_id = {
        pokemon.pokemon_id: pokemon
        for pokemon in board.pokemon
    }
    if not set(pokemon_ids) <= set(board_by_id):
        return None

    removed_ids = set(pokemon_ids)
    removed = tuple(
        pokemon
        for pokemon in board.pokemon
        if pokemon.pokemon_id in removed_ids
    )
    survivors = tuple(
        pokemon
        for pokemon in board.pokemon
        if pokemon.pokemon_id not in removed_ids
    )
    active_id = (
        None
        if board.active_id in removed_ids
        else board.active_id
    )

    ledger = state.ledger
    pokemon_card_ids: list[str] = []
    attachment_card_ids: list[str] = []

    for pokemon in removed:
        (
            ledger,
            moved_pokemon_cards,
            moved_attachments,
        ) = route_removed_pokemon_cards(
            ledger,
            pokemon,
            pokemon_destination=pokemon_destination,
            attachment_destination=attachment_destination,
            preserve_identity=preserve_identity,
        )
        pokemon_card_ids.extend(moved_pokemon_cards)
        attachment_card_ids.extend(moved_attachments)

    pending = PromotionPendingState(
        ledger,
        survivors,
        active_id,
        board.retreat_used,
        board.evolution_allowed,
        board.bench_capacity,
    )

    return BatchZoneExitTransition(
        pending,
        tuple(pokemon.pokemon_id for pokemon in removed),
        tuple(pokemon_card_ids),
        tuple(attachment_card_ids),
    )
