"""Conserve full Pokemon stacks and attachments through Knock Out."""

from __future__ import annotations

from dataclasses import dataclass, replace

from board_position_state import (
    Attachment,
    AttachmentKind,
    BoardPokemon,
    BoardState,
    replace_pokemon,
    validate_state,
)
from identity_materialization import (
    IdentityLedger,
    assert_conserved,
    attach_instance,
    dematerialize,
    detach_instance,
    materialize,
    move_instance,
    validate_board_position_stack_bindings,
)

HAND = "hand"
DISCARD = "discard"


@dataclass(frozen=True)
class StackBoardMaterialState:
    """One authority for exchangeable counts, physical cards, and stack topology."""

    ledger: IdentityLedger
    board: BoardState | None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if self.board is None:
            bound = tuple(
                row.instance_id
                for row in self.ledger.instances
                if row.zone in {"in_play", "attached"}
            )
            if bound:
                raise ValueError(
                    "terminal board cannot retain board-bound instances: "
                    f"{bound!r}"
                )
            return

        validate_state(self.board)
        validate_board_position_stack_bindings(self.ledger, self.board)
        _validate_attachment_bindings(self.ledger, self.board)


def _validate_attachment_bindings(
    ledger: IdentityLedger,
    board: BoardState,
) -> None:
    expected: dict[str, tuple[str, str]] = {}
    for pokemon in board.pokemon:
        for attachment in pokemon.attachments:
            if attachment.card_id in expected:
                raise ValueError(
                    f"duplicate board attachment ID: {attachment.card_id}"
                )
            expected[attachment.card_id] = (
                pokemon.pokemon_id,
                attachment.name,
            )

    actual = {
        row.instance_id: (row.attached_to, row.card_name)
        for row in ledger.instances
        if row.zone == "attached"
    }
    if actual != expected:
        raise ValueError(
            "attachment bindings differ between identity ledger and stack board: "
            f"ledger={actual!r}, board={expected!r}"
        )


def _find_pokemon(
    board: BoardState,
    pokemon_id: str,
) -> BoardPokemon | None:
    for pokemon in board.pokemon:
        if pokemon.pokemon_id == pokemon_id:
            return pokemon
    return None


def attach_from_hand(
    state: StackBoardMaterialState,
    *,
    pokemon_id: str,
    card_class: str,
    instance_id: str,
    card_name: str,
    kind: AttachmentKind,
    retreat_units: int = 0,
) -> StackBoardMaterialState | None:
    """Materialize one Energy/Tool/other attachment from hand onto a Pokemon."""

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

    pokemon = _find_pokemon(state.board, pokemon_id)
    if pokemon is None:
        return None
    if kind == AttachmentKind.TOOL and any(
        card.kind == AttachmentKind.TOOL
        for card in pokemon.attachments
    ):
        return None

    ledger = materialize(
        state.ledger,
        card_class=card_class,
        card_name=card_name,
        source_zone=HAND,
        instance_id=instance_id,
    )
    ledger = attach_instance(ledger, instance_id, pokemon_id)

    attachment = Attachment(
        instance_id,
        card_name,
        kind,
        retreat_units=retreat_units,
    )
    next_pokemon = replace(
        pokemon,
        attachments=pokemon.attachments + (attachment,),
        combat=replace(
            pokemon.combat,
            tool_attached=(
                pokemon.combat.tool_attached
                or kind == AttachmentKind.TOOL
            ),
        ),
    )
    board = replace_pokemon(state.board, next_pokemon)
    next_state = StackBoardMaterialState(ledger, board)
    assert_conserved(state.ledger, next_state.ledger)
    return next_state


def knock_out_with_conservation(
    state: StackBoardMaterialState,
    pokemon_id: str,
    *,
    promote_id: str | None = None,
) -> StackBoardMaterialState | None:
    """Discard one complete Pokemon stack and all attached physical cards."""

    if state.board is None:
        return None
    pokemon = _find_pokemon(state.board, pokemon_id)
    if pokemon is None:
        return None

    remaining = tuple(
        row for row in state.board.pokemon
        if row.pokemon_id != pokemon_id
    )

    if pokemon_id == state.board.active_id:
        if not remaining:
            if promote_id is not None:
                return None
            board = None
        else:
            if promote_id not in state.board.bench_ids:
                return None
            board = replace(
                state.board,
                pokemon=remaining,
                active_id=promote_id,
            )
            validate_state(board)
    else:
        if promote_id is not None:
            return None
        board = replace(state.board, pokemon=remaining)
        validate_state(board)

    ledger = state.ledger
    for card in pokemon.stack:
        ledger = move_instance(ledger, card.card_id, DISCARD)
        ledger = dematerialize(ledger, card.card_id)

    for attachment in pokemon.attachments:
        ledger = detach_instance(ledger, attachment.card_id, DISCARD)
        ledger = dematerialize(ledger, attachment.card_id)

    next_state = StackBoardMaterialState(ledger, board)
    assert_conserved(state.ledger, next_state.ledger)
    return next_state
