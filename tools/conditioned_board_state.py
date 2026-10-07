"""Lossless Special Condition adapter for the existing board-object kernel.

The board-object kernel keeps a legacy set of Special Condition names because
older movement logic only needs membership and clearing. This adapter stores the
richer typed payload separately and validates that both representations stay in
sync.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable, Mapping

from board_object_kernel import (
    BoardState,
    EnergyAttachment,
    evolve as board_evolve,
    retreat as board_retreat,
    switch_active as board_switch_active,
)
from special_condition_state import (
    ConditionInstance,
    ConditionKind,
    SpecialConditionState,
    apply_condition,
    clear_conditions,
    legacy_name_projection,
    regular_condition,
)


@dataclass(frozen=True)
class ConditionedBoardState:
    board: BoardState
    condition_states: tuple[tuple[str, SpecialConditionState], ...]

    def get_conditions(self, object_id: str) -> SpecialConditionState:
        for key, state in self.condition_states:
            if key == object_id:
                return state
        raise KeyError(object_id)

    def validate(self) -> None:
        board_ids = {pokemon.object_id for pokemon in self.board.objects}
        condition_ids = [key for key, _ in self.condition_states]
        if set(condition_ids) != board_ids or len(condition_ids) != len(set(condition_ids)):
            raise ValueError("condition states must match board objects exactly")

        for pokemon in self.board.objects:
            typed = self.get_conditions(pokemon.object_id)
            if pokemon.special_conditions != legacy_name_projection(typed):
                raise ValueError(
                    f"legacy and typed Special Conditions disagree for {pokemon.object_id!r}"
                )


def _sorted_states(
    states: Mapping[str, SpecialConditionState] | Iterable[tuple[str, SpecialConditionState]],
) -> tuple[tuple[str, SpecialConditionState], ...]:
    items = states.items() if isinstance(states, Mapping) else states
    return tuple(sorted(items, key=lambda row: row[0]))


def make_conditioned_board(
    board: BoardState,
    condition_states: Mapping[str, SpecialConditionState],
) -> ConditionedBoardState:
    state = ConditionedBoardState(board, _sorted_states(condition_states))
    state.validate()
    return state


def lift_legacy_board_as_regular(board: BoardState) -> ConditionedBoardState:
    """Lossily lift legacy name-only state by assuming ordinary conditions.

    This cannot reconstruct an irregular payload such as Severe Poison from the
    old {"Poisoned"} representation. Callers that know richer provenance should
    use make_conditioned_board() instead.
    """

    states: dict[str, SpecialConditionState] = {}
    for pokemon in board.objects:
        typed = SpecialConditionState()
        for name in sorted(pokemon.special_conditions):
            typed = apply_condition(typed, regular_condition(ConditionKind(name)))
        states[pokemon.object_id] = typed
    return make_conditioned_board(board, states)


def _replace_condition_state(
    state: ConditionedBoardState,
    object_id: str,
    typed: SpecialConditionState,
    *,
    board: BoardState | None = None,
) -> ConditionedBoardState:
    next_board = state.board if board is None else board
    objects = tuple(
        replace(pokemon, special_conditions=legacy_name_projection(typed))
        if pokemon.object_id == object_id
        else pokemon
        for pokemon in next_board.objects
    )
    next_board = replace(next_board, objects=objects)
    next_board.validate()

    condition_states = tuple(
        (key, typed if key == object_id else current)
        for key, current in state.condition_states
    )
    result = ConditionedBoardState(next_board, condition_states)
    result.validate()
    return result


def apply_board_condition(
    state: ConditionedBoardState,
    object_id: str,
    condition: ConditionInstance,
) -> ConditionedBoardState:
    typed = apply_condition(state.get_conditions(object_id), condition)
    return _replace_condition_state(state, object_id, typed)


def clear_board_conditions(
    state: ConditionedBoardState,
    object_id: str,
) -> ConditionedBoardState:
    return _replace_condition_state(
        state,
        object_id,
        clear_conditions(state.get_conditions(object_id)),
    )


def switch_active(
    state: ConditionedBoardState,
    bench_object_id: str,
) -> ConditionedBoardState | None:
    outgoing_id = state.board.active_id
    board = board_switch_active(state.board, bench_object_id)
    if board is None:
        return None

    condition_states = tuple(
        (key, clear_conditions(typed) if key == outgoing_id else typed)
        for key, typed in state.condition_states
    )
    result = ConditionedBoardState(board, condition_states)
    result.validate()
    return result


def retreat(
    state: ConditionedBoardState,
    bench_object_id: str,
    *,
    retreat_cost: int,
    discard_energy_ids: Iterable[str],
) -> tuple[ConditionedBoardState, tuple[EnergyAttachment, ...]] | None:
    outgoing_id = state.board.active_id
    resolved = board_retreat(
        state.board,
        bench_object_id,
        retreat_cost=retreat_cost,
        discard_energy_ids=discard_energy_ids,
    )
    if resolved is None:
        return None

    board, discarded = resolved
    condition_states = tuple(
        (key, clear_conditions(typed) if key == outgoing_id else typed)
        for key, typed in state.condition_states
    )
    result = ConditionedBoardState(board, condition_states)
    result.validate()
    return result, discarded


def evolve(
    state: ConditionedBoardState,
    object_id: str,
    *,
    new_card_name: str,
    new_tags: Iterable[str] | None = None,
) -> ConditionedBoardState | None:
    board = board_evolve(
        state.board,
        object_id,
        new_card_name=new_card_name,
        new_tags=new_tags,
    )
    if board is None:
        return None

    condition_states = tuple(
        (key, clear_conditions(typed) if key == object_id else typed)
        for key, typed in state.condition_states
    )
    result = ConditionedBoardState(board, condition_states)
    result.validate()
    return result
