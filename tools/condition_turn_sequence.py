"""Compose turn advancement with Special Condition Checkup resolution."""

from __future__ import annotations

from dataclasses import dataclass

from timed_special_conditions import (
    BasicCheckupOutcome,
    TimedConditionState,
    resolve_basic_checkup,
)
from turn_sequence_kernel import TurnAdvance, TurnSequenceState, advance_turn


@dataclass(frozen=True)
class ConditionBoundaryAdvance:
    turn_advance: TurnAdvance
    next_turn_serial: int
    conditions: TimedConditionState
    checkup_outcome: BasicCheckupOutcome | None


def advance_with_conditions(
    sequence: TurnSequenceState,
    conditions: TimedConditionState,
    *,
    current_turn_serial: int,
    burn_coin_heads: bool | None = None,
    asleep_coin_heads: bool | None = None,
) -> ConditionBoundaryAdvance | None:
    """Advance one ended turn and resolve base status work only if Checkup occurs."""

    if current_turn_serial < 0:
        raise ValueError("current_turn_serial must be non-negative")

    advanced = advance_turn(sequence)
    if advanced is None:
        return None

    outcome: BasicCheckupOutcome | None = None
    next_conditions = conditions
    if advanced.pokemon_checkup_occurs:
        outcome = resolve_basic_checkup(
            conditions,
            completed_turn_player=sequence.current_player,
            completed_turn_serial=current_turn_serial,
            burn_coin_heads=burn_coin_heads,
            asleep_coin_heads=asleep_coin_heads,
        )
        next_conditions = outcome.next_state

    return ConditionBoundaryAdvance(
        turn_advance=advanced,
        next_turn_serial=current_turn_serial + 1,
        conditions=next_conditions,
        checkup_outcome=outcome,
    )
