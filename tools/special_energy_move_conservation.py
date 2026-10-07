"""Resolve the conservation boundary for moved Special Energy cards."""

from __future__ import annotations

from dataclasses import replace

from board_attachment_conservation import BoardMaterialState
from energy_movement_conservation import move_energy_with_conservation
from identity_materialization import (
    assert_conserved,
    dematerialize,
    detach_instance,
)

DISCARD = "discard"


def move_special_energy_with_conservation(
    state: BoardMaterialState,
    instance_id: str,
    *,
    source_object_id: str,
    target_object_id: str,
    destination_accepts_card: bool,
) -> BoardMaterialState | None:
    """Move a known Special Energy after destination legality is resolved.

    A legal destination keeps the same materialized physical instance attached.
    If the chosen destination cannot legally have that Special Energy attached,
    the card is removed from the source and returned to the exchangeable
    discard-pile count instead.
    """

    if state.board is None or source_object_id == target_object_id:
        return None

    try:
        source = state.board.get(source_object_id)
        state.board.get(target_object_id)
        row = state.ledger.instance(instance_id)
    except KeyError:
        return None

    if row.zone != "attached" or row.attached_to != source_object_id:
        return None

    matches = tuple(
        energy
        for energy in source.energy
        if energy.instance_id == instance_id
    )
    if len(matches) != 1:
        return None

    if destination_accepts_card:
        return move_energy_with_conservation(
            state,
            instance_id,
            source_object_id=source_object_id,
            target_object_id=target_object_id,
        )

    next_source = replace(
        source,
        energy=tuple(
            energy
            for energy in source.energy
            if energy.instance_id != instance_id
        ),
    )
    board = replace(
        state.board,
        objects=tuple(
            next_source
            if pokemon.object_id == source_object_id
            else pokemon
            for pokemon in state.board.objects
        ),
    )
    board.validate()

    ledger = detach_instance(state.ledger, instance_id, DISCARD)
    ledger = dematerialize(ledger, instance_id)

    next_state = BoardMaterialState(ledger, board)
    assert_conserved(state.ledger, next_state.ledger)
    return next_state
