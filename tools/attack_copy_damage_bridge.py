"""Replay copied-attack board effects before the turn-boundary handoff.

The attack-copy kernel records leaf-body effects and outer continuations in one
ordered event stream. This adapter interprets selected body events against the
board damage kernel, then exposes Knock Out candidates only after the complete
declared-attack event stream has been replayed.

It intentionally does not dispose Knocked Out Pokemon. A non-empty Knock Out
set is a phase barrier: downstream Knock Out processing must finish before the
turn scheduler consumes a pending extra-turn or ordinary handoff directive.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from attack_copy_kernel import Resolution
from attack_copy_turn_boundary_bridge import close_declared_attack
from board_object_kernel import BoardState
from canonical_turn_sequence_owner import TurnScheduleState
from damage_board_bridge import (
    CounterPlacementOutcome,
    EffectCounterPlacement,
    apply_attack_damage,
    apply_effect_counter_placement,
    knocked_out_ids,
)
from damage_calculation_kernel import DamageContext, DamageResult
from unified_state_kernel import UnifiedState


@dataclass(frozen=True)
class BoardEventProgram:
    """Board effects attached to one ordered copy-resolution event."""

    damage_target_id: str
    damage_context: DamageContext
    counter_placements: tuple[EffectCounterPlacement, ...] = ()


@dataclass(frozen=True)
class BoardEventTrace:
    event: str
    damage_counters: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class AttackCopyBoardResolution:
    resolution: Resolution
    board: BoardState
    damage_results: tuple[tuple[str, DamageResult], ...]
    counter_outcomes: tuple[tuple[str, CounterPlacementOutcome], ...]
    event_trace: tuple[BoardEventTrace, ...]
    knocked_out_ids: tuple[str, ...]


def replay_copy_attack_board(
    resolution: Resolution,
    board: BoardState,
    *,
    event_programs: Mapping[str, BoardEventProgram],
    hp_by_object_id: Mapping[str, int],
) -> AttackCopyBoardResolution:
    """Replay board commands in the copy kernel's exact event order.

    Damage and effect-counter placement happen at the leaf-body event. Outer
    continuation events remain ordered after that body. The shared Knock Out
    threshold check runs once, after every event has been replayed.
    """

    current = board
    damage_results: list[tuple[str, DamageResult]] = []
    counter_outcomes: list[tuple[str, CounterPlacementOutcome]] = []
    trace: list[BoardEventTrace] = []

    for event in resolution.state.events:
        program = event_programs.get(event)
        if program is not None:
            current, damage_result = apply_attack_damage(
                current,
                program.damage_target_id,
                program.damage_context,
            )
            damage_results.append((event, damage_result))
            for placement in program.counter_placements:
                current, outcome = apply_effect_counter_placement(
                    current,
                    placement,
                )
                counter_outcomes.append((event, outcome))

        trace.append(
            BoardEventTrace(
                event,
                tuple(
                    (pokemon.object_id, pokemon.damage_counters)
                    for pokemon in current.objects
                ),
            )
        )

    return AttackCopyBoardResolution(
        resolution=resolution,
        board=current,
        damage_results=tuple(damage_results),
        counter_outcomes=tuple(counter_outcomes),
        event_trace=tuple(trace),
        knocked_out_ids=knocked_out_ids(current, hp_by_object_id),
    )


def close_copy_attack_if_no_knockouts(
    schedule: TurnScheduleState,
    current_state: UnifiedState,
    board_resolution: AttackCopyBoardResolution,
) -> tuple[TurnScheduleState, UnifiedState] | None:
    """Close the turn only when no end-of-attack Knock Out phase is pending.

    A non-empty Knock Out candidate set must be routed through the repository's
    Knock Out phase machinery first. Returning None makes it impossible for this
    adapter to start an extra turn while a zero-HP Active remains unresolved.
    """

    if board_resolution.knocked_out_ids:
        return None
    return close_declared_attack(
        schedule,
        current_state,
        board_resolution.resolution,
    )
