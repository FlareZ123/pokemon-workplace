"""Conserve materialized board attachments across Tool play, evolution, and Knock Out."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from board_object_kernel import BoardState, ToolAttachment, evolve, knock_out
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    attach_instance,
    dematerialize,
    detach_instance,
    materialize,
    validate_board_attachment_bindings,
)

HAND = "hand"
DISCARD = "discard"


@dataclass(frozen=True)
class BoardMaterialState:
    ledger: IdentityLedger
    board: BoardState | None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.board is None:
            attached = tuple(
                row.instance_id
                for row in self.ledger.instances
                if row.zone == "attached"
            )
            if attached:
                raise ValueError(
                    "terminal board cannot retain attached materialized cards: "
                    f"{attached!r}"
                )
            return
        self.board.validate()
        validate_board_attachment_bindings(self.ledger, self.board)


def _replace_tool(
    board: BoardState,
    object_id: str,
    tool: ToolAttachment | None,
) -> BoardState:
    pokemon = board.get(object_id)
    next_pokemon = replace(
        pokemon,
        tool=tool,
        pokemon_state=replace(
            pokemon.pokemon_state,
            tool_attached=tool is not None,
        ),
    )
    next_board = replace(
        board,
        objects=tuple(
            next_pokemon if row.object_id == object_id else row
            for row in board.objects
        ),
    )
    next_board.validate()
    return next_board


def attach_tool_from_hand(
    state: BoardMaterialState,
    *,
    object_id: str,
    card_class: str,
    instance_id: str,
    card_name: str,
    print_id: str | None = None,
) -> BoardMaterialState | None:
    if state.board is None:
        return None
    if state.ledger.exchangeable.count(card_class, HAND) <= 0:
        return None
    try:
        state.ledger.instance(instance_id)
    except KeyError:
        pass
    else:
        return None
    try:
        pokemon = state.board.get(object_id)
    except KeyError:
        return None
    if pokemon.tool is not None:
        return None

    ledger = materialize(
        state.ledger,
        card_class=card_class,
        card_name=card_name,
        source_zone=HAND,
        instance_id=instance_id,
    )
    ledger = attach_instance(ledger, instance_id, object_id)
    board = _replace_tool(
        state.board,
        object_id,
        ToolAttachment(instance_id, card_name, print_id=print_id),
    )
    next_state = BoardMaterialState(ledger, board)
    assert_conserved(state.ledger, next_state.ledger)
    return next_state


def evolve_with_conservation(
    state: BoardMaterialState,
    object_id: str,
    *,
    new_card_name: str,
    new_tags: Iterable[str] | None = None,
) -> BoardMaterialState | None:
    if state.board is None:
        return None
    board = evolve(
        state.board,
        object_id,
        new_card_name=new_card_name,
        new_tags=new_tags,
    )
    if board is None:
        return None
    next_state = BoardMaterialState(state.ledger, board)
    assert_conserved(state.ledger, next_state.ledger)
    return next_state


def knock_out_with_conservation(
    state: BoardMaterialState,
    object_id: str,
    *,
    promote_object_id: str | None = None,
) -> BoardMaterialState | None:
    """Remove the board object and dematerialize all discarded attachments."""

    if state.board is None:
        return None
    result = knock_out(
        state.board,
        object_id,
        promote_object_id=promote_object_id,
    )
    if result is None:
        return None

    board, removed = result
    ledger = state.ledger
    attached_ids = [energy.instance_id for energy in removed.energy]
    if removed.tool is not None:
        attached_ids.append(removed.tool.instance_id)

    for instance_id in attached_ids:
        ledger = detach_instance(ledger, instance_id, DISCARD)
        ledger = dematerialize(ledger, instance_id)

    next_state = BoardMaterialState(ledger, board)
    assert_conserved(state.ledger, next_state.ledger)
    return next_state
