"""Pokemon TCG helper for attack-phase attachment removal before KO preparation."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from board_position_state import AttachmentKind, replace_pokemon
from identity_materialization import assert_conserved, dematerialize, detach_instance
from stack_knockout_conservation import StackBoardMaterialState

DISCARD_ZONE = "discard"


def apply_attack_attachment_discard(
    state: StackBoardMaterialState,
    *,
    pokemon_id: str,
    card_ids: Iterable[str],
) -> StackBoardMaterialState | None:
    """Apply a card-game effect that discards selected attached cards."""

    if state.board is None:
        return None

    selected = tuple(card_ids)
    if not selected or len(selected) != len(set(selected)):
        return None

    try:
        pokemon = state.board.get(pokemon_id)
    except (KeyError, StopIteration):
        return None

    attached = {card.card_id for card in pokemon.attachments}
    if not set(selected) <= attached:
        return None

    selected_set = set(selected)
    remaining = tuple(
        card
        for card in pokemon.attachments
        if card.card_id not in selected_set
    )

    updated = replace(
        pokemon,
        attachments=remaining,
        combat=replace(
            pokemon.combat,
            tool_attached=any(
                card.kind == AttachmentKind.TOOL
                for card in remaining
            ),
        ),
    )
    board = replace_pokemon(state.board, updated)

    ledger = state.ledger
    for card_id in selected:
        ledger = detach_instance(ledger, card_id, DISCARD_ZONE)
        ledger = dematerialize(ledger, card_id)

    next_state = StackBoardMaterialState(ledger, board)
    assert_conserved(state.ledger, next_state.ledger)
    return next_state
