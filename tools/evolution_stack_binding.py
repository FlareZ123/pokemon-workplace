"""Bind physical evolution stacks to board objects and the identity ledger."""

from __future__ import annotations

from dataclasses import dataclass, replace

from board_object_kernel import evolve as board_evolve, next_turn as board_next_turn
from evolution_stack_state import EvolutionState, StackCard, replace_stack
from identity_materialization import (
    IdentityLedger, assert_conserved, move_instance, put_in_play_instance,
    validate_board_attachment_bindings,
)


@dataclass(frozen=True)
class EvolutionTransition:
    state: EvolutionState
    ledger: IdentityLedger
    removed_instance_id: str | None = None
    knockout_required: bool = False


def validate_ledger_binding(state: EvolutionState, ledger: IdentityLedger) -> None:
    state.validate()
    validate_board_attachment_bindings(ledger, state.board)
    for stack in state.stacks:
        for card in stack.cards:
            row = ledger.instance(card.instance_id)
            if (
                row.card_name != card.card_name
                or row.zone != "in_play"
                or row.board_object_id != stack.object_id
                or row.attached_to is not None
            ):
                raise ValueError(f"Pokemon stack binding mismatch for {card.instance_id}")


def ordinary_evolve(
    state: EvolutionState, ledger: IdentityLedger, object_id: str, card: StackCard,
) -> EvolutionTransition | None:
    if not state.evolution_allowed:
        return None
    stack = state.stack(object_id)
    if not stack.evolution_eligible:
        return None
    if card.stage_rank != stack.top.stage_rank + 1 or card.evolves_from != stack.top.card_name:
        return None
    try:
        row = ledger.instance(card.instance_id)
    except KeyError:
        return None
    if (
        row.zone != "hand"
        or row.card_name != card.card_name
        or row.attached_to is not None
        or row.board_object_id is not None
    ):
        return None

    board = board_evolve(
        state.board, object_id, new_card_name=card.card_name,
        new_print_id=card.print_id, new_tags=card.tags,
    )
    if board is None:
        return None
    next_ledger = put_in_play_instance(ledger, card.instance_id, object_id)
    assert_conserved(ledger, next_ledger)
    next_state = replace(state, board=board)
    next_state = replace_stack(next_state, replace(
        stack, cards=stack.cards + (card,), evolution_eligible=False,
    ))
    validate_ledger_binding(next_state, next_ledger)
    return EvolutionTransition(next_state, next_ledger)


def devolve_top(
    state: EvolutionState, ledger: IdentityLedger, object_id: str, *, destination_zone: str,
) -> EvolutionTransition | None:
    if destination_zone in {"attached", "in_play"}:
        raise ValueError("devolved Pokemon card must leave the board relation")
    stack = state.stack(object_id)
    if len(stack.cards) < 2:
        return None

    removed = stack.top
    exposed = stack.cards[-2]
    board = board_evolve(
        state.board, object_id, new_card_name=exposed.card_name,
        new_print_id=exposed.print_id, new_tags=exposed.tags,
    )
    if board is None:
        return None
    next_ledger = move_instance(ledger, removed.instance_id, destination_zone)
    assert_conserved(ledger, next_ledger)
    next_state = replace(state, board=board)
    next_state = replace_stack(next_state, replace(
        stack, cards=stack.cards[:-1], evolution_eligible=False,
    ))
    validate_ledger_binding(next_state, next_ledger)
    knockout_required = board.get(object_id).damage_counters * 10 >= exposed.hp
    return EvolutionTransition(
        next_state, next_ledger, removed.instance_id, knockout_required,
    )


def begin_next_turn(state: EvolutionState) -> EvolutionState:
    next_state = replace(
        state, board=board_next_turn(state.board),
        stacks=tuple(replace(row, evolution_eligible=True) for row in state.stacks),
        evolution_allowed=True,
    )
    next_state.validate()
    return next_state
