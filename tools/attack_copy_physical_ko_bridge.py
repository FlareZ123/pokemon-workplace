"""Replay copied-attack board effects on the stack-bearing physical board.

This bridge keeps the identity ledger and board topology synchronized while
damage changes. It stops at Knock Out candidates; callers can then enter the
existing simultaneous Knock Out batch layer after all step-6 reactions have
been resolved.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from attack_copy_kernel import Resolution
from board_position_state import replace_pokemon
from damage_board_bridge import CounterPlacementOutcome, EffectCounterPlacement
from damage_calculation_kernel import DamageContext, DamageResult, calculate_damage
from simultaneous_knockout_conservation import (
    PendingKnockOutBatch,
    prepare_knock_out_batch,
)
from stack_knockout_conservation import StackBoardMaterialState


@dataclass(frozen=True)
class PhysicalBoardEventProgram:
    damage_target_id: str
    damage_context: DamageContext
    counter_placements: tuple[EffectCounterPlacement, ...] = ()
    additional_damage: tuple[tuple[str, DamageContext], ...] = ()


@dataclass(frozen=True)
class PhysicalDamageRecord:
    event: str
    target_index: int
    target_id: str
    result: DamageResult


@dataclass(frozen=True)
class PhysicalBoardEventTrace:
    event: str
    damage_counters: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class AttackCopyPhysicalBoardResolution:
    resolution: Resolution
    state: StackBoardMaterialState
    damage_results: tuple[tuple[str, DamageResult], ...]
    counter_outcomes: tuple[tuple[str, CounterPlacementOutcome], ...]
    event_trace: tuple[PhysicalBoardEventTrace, ...]
    knocked_out_ids: tuple[str, ...]
    damage_targets: tuple[tuple[str, str], ...] = ()
    damage_records: tuple[PhysicalDamageRecord, ...] = ()


def _add_counters(
    state: StackBoardMaterialState,
    target_id: str,
    count: int,
) -> StackBoardMaterialState:
    board = state.board
    if board is None:
        raise ValueError("cannot damage a terminal board")
    target = board.get(target_id)
    next_board = replace_pokemon(
        board,
        replace(target, damage_counters=target.damage_counters + count),
    )
    return StackBoardMaterialState(state.ledger, next_board)


def _apply_damage(
    state: StackBoardMaterialState,
    target_id: str,
    context: DamageContext,
) -> tuple[StackBoardMaterialState, DamageResult]:
    result = calculate_damage(context)
    if result.final_damage % 10 != 0:
        raise ValueError("board damage must be representable in 10-damage counters")
    if result.final_damage == 0:
        return state, result
    return _add_counters(state, target_id, result.final_damage // 10), result


def _apply_effect_counters(
    state: StackBoardMaterialState,
    placement: EffectCounterPlacement,
) -> tuple[StackBoardMaterialState, CounterPlacementOutcome]:
    board = state.board
    if board is None:
        raise ValueError("cannot place counters on a terminal board")
    board.get(placement.target_id)
    placed = 0 if placement.prevent_effects_of_attacks else placement.count
    next_state = (
        state
        if placed == 0
        else _add_counters(state, placement.target_id, placed)
    )
    return (
        next_state,
        CounterPlacementOutcome(
            placement.target_id,
            placement.count,
            placed,
        ),
    )


def _knocked_out_ids(
    state: StackBoardMaterialState,
    hp_by_pokemon_id: Mapping[str, int],
) -> tuple[str, ...]:
    board = state.board
    if board is None:
        return ()

    result: list[str] = []
    for pokemon in board.pokemon:
        hp = hp_by_pokemon_id[pokemon.pokemon_id]
        if hp <= 0 or hp % 10 != 0:
            raise ValueError("Pokemon HP must be a positive multiple of 10")
        if pokemon.damage_counters * 10 >= hp:
            result.append(pokemon.pokemon_id)
    return tuple(result)


def replay_copy_attack_physical_board(
    resolution: Resolution,
    state: StackBoardMaterialState,
    *,
    event_programs: Mapping[str, PhysicalBoardEventProgram],
    hp_by_pokemon_id: Mapping[str, int],
) -> AttackCopyPhysicalBoardResolution:
    """Replay copy events while preserving the physical-card ledger."""

    current = state
    damage_results: list[tuple[str, DamageResult]] = []
    damage_targets: list[tuple[str, str]] = []
    damage_records: list[PhysicalDamageRecord] = []
    counter_outcomes: list[tuple[str, CounterPlacementOutcome]] = []
    trace: list[PhysicalBoardEventTrace] = []

    for event in resolution.state.events:
        program = event_programs.get(event)
        if program is not None:
            damage_actions = (
                (program.damage_target_id, program.damage_context),
            ) + program.additional_damage
            for index, (target_id, context) in enumerate(damage_actions):
                current, damage_result = _apply_damage(
                    current, target_id, context,
                )
                damage_results.append((event, damage_result))
                damage_targets.append((event, target_id))
                damage_records.append(
                    PhysicalDamageRecord(event, index, target_id, damage_result)
                )
            for placement in program.counter_placements:
                current, outcome = _apply_effect_counters(current, placement)
                counter_outcomes.append((event, outcome))

        board = current.board
        assert board is not None
        trace.append(
            PhysicalBoardEventTrace(
                event,
                tuple(
                    (pokemon.pokemon_id, pokemon.damage_counters)
                    for pokemon in board.pokemon
                ),
            )
        )

    return AttackCopyPhysicalBoardResolution(
        resolution=resolution,
        state=current,
        damage_results=tuple(damage_results),
        counter_outcomes=tuple(counter_outcomes),
        event_trace=tuple(trace),
        knocked_out_ids=_knocked_out_ids(current, hp_by_pokemon_id),
        damage_targets=tuple(damage_targets),
        damage_records=tuple(damage_records),
    )


def prepare_physical_knockouts(
    board_resolution: AttackCopyPhysicalBoardResolution,
) -> PendingKnockOutBatch | None:
    """Enter the existing physical KO phase from the completed board state.

    Call this after any applicable damaged-by-attack reactions have been applied.
    The function performs no disposal and preserves the trigger window.
    """

    if not board_resolution.knocked_out_ids:
        return None
    return prepare_knock_out_batch(
        board_resolution.state,
        board_resolution.knocked_out_ids,
    )
