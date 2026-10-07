"""Translate Knock Out redirection signatures into per-instance zone routes."""

from __future__ import annotations

from typing import Iterable

from board_position_state import AttachmentKind
from knockout_redirection_taxonomy import (
    ALL_TO_LOST,
    ATTACHED_ENERGY_TO_HAND,
    POKEMON_TO_LOST,
    SELF_TO_HAND,
)
from simultaneous_knockout_conservation import PendingKnockOutBatch

DISCARD = "discard"
HAND = "hand"
LOST_ZONE = "lost_zone"

SUPPORTED_SIGNATURES = frozenset(
    {
        SELF_TO_HAND,
        ALL_TO_LOST,
        POKEMON_TO_LOST,
        ATTACHED_ENERGY_TO_HAND,
    }
)


def destinations_for_redirection(
    pending: PendingKnockOutBatch,
    *,
    pokemon_id: str,
    routing_signature: str,
    selected_energy_ids: Iterable[str] = (),
) -> dict[str, str] | None:
    """Resolve one classified KO redirection into explicit destinations.

    The returned mapping is consumed by
    knockout_zone_routing.discard_pending_with_zone_routes. It preserves
    destinations that card text states explicitly even when they equal the
    ordinary discard sink. Removed instances omitted from the mapping remain
    semantically untouched by this effect and follow normal KO disposal unless
    another effect redirects them.

    selected_energy_ids is intentionally semantic input from the caller.
    The signature layer can verify that selected instances are Energy attached
    to the Knocked Out Pokemon, but it does not infer predicates such as
    "Basic Water Energy" from card names or classes.
    """

    if routing_signature not in SUPPORTED_SIGNATURES:
        return None
    if pokemon_id not in pending.knocked_out_ids:
        return None

    board = pending.state.board
    assert board is not None

    try:
        pokemon = board.get(pokemon_id)
    except (KeyError, StopIteration):
        return None

    stack_ids = tuple(card.card_id for card in pokemon.stack)
    attachment_ids = tuple(card.card_id for card in pokemon.attachments)
    energy_ids = {
        card.card_id
        for card in pokemon.attachments
        if card.kind == AttachmentKind.ENERGY
    }

    selected = tuple(selected_energy_ids)
    if len(selected) != len(set(selected)):
        return None

    if routing_signature != ATTACHED_ENERGY_TO_HAND and selected:
        return None

    if routing_signature == SELF_TO_HAND:
        # Durable Blade-like text explicitly returns the Pokemon while
        # discarding attached cards.
        return {
            **{instance_id: HAND for instance_id in stack_ids},
            **{instance_id: DISCARD for instance_id in attachment_ids},
        }

    if routing_signature == ALL_TO_LOST:
        return {
            instance_id: LOST_ZONE
            for instance_id in stack_ids + attachment_ids
        }

    if routing_signature == POKEMON_TO_LOST:
        # Lost City-like text explicitly sends the Pokemon to the Lost Zone and
        # explicitly discards attached cards.
        return {
            **{instance_id: LOST_ZONE for instance_id in stack_ids},
            **{instance_id: DISCARD for instance_id in attachment_ids},
        }

    if not set(selected) <= energy_ids:
        return None
    return {instance_id: HAND for instance_id in selected}
