"""Keep identity-ledger bindings synchronized when Energy moves on board."""

from __future__ import annotations

from board_attachment_conservation import BoardMaterialState
from board_object_kernel import move_energy_between_pokemon
from identity_materialization import assert_conserved, attach_instance


def move_energy_with_conservation(
    state: BoardMaterialState,
    instance_id: str,
    *,
    source_object_id: str,
    target_object_id: str,
) -> BoardMaterialState | None:
    if state.board is None:
        return None

    try:
        instance = state.ledger.instance(instance_id)
    except KeyError:
        return None
    if instance.zone != "attached" or instance.attached_to != source_object_id:
        return None

    board = move_energy_between_pokemon(
        state.board,
        instance_id,
        source_object_id=source_object_id,
        target_object_id=target_object_id,
    )
    if board is None:
        return None

    ledger = attach_instance(
        state.ledger,
        instance_id,
        target_object_id,
    )
    next_state = BoardMaterialState(ledger, board)
    assert_conserved(state.ledger, next_state.ledger)
    return next_state
