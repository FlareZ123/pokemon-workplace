"""Turn scheduling whose action budgets live only in UnifiedState.

The older TurnSequenceState keeps its own current/other budgets. This adapter
separates schedule metadata from budget ownership so a composed planner can use
UnifiedState.turn_budget as the single authoritative per-player action history.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from legacy_turn_budget_bridge import apply_budget_to_unified
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import UnifiedState, consume_turn_action


@dataclass(frozen=True)
class TurnScheduleState:
    current_player: str
    other_player: str
    extra_turn_queued: bool = False
    skip_checkup_before_next_turn: bool = False

    def __post_init__(self) -> None:
        if not self.current_player or not self.other_player:
            raise ValueError("player identifiers must be non-empty")
        if self.current_player == self.other_player:
            raise ValueError("players must be distinct")
        if self.skip_checkup_before_next_turn and not self.extra_turn_queued:
            raise ValueError("checkup skip requires a queued extra turn")


@dataclass(frozen=True)
class CanonicalTurnAdvance:
    schedule: TurnScheduleState
    current_state: UnifiedState
    other_state: UnifiedState
    pokemon_checkup_occurs: bool
    same_player_continues: bool


def _budget(state: UnifiedState) -> TurnActionBudget:
    if state.turn_budget is None:
        raise ValueError("turn-sequence ownership requires canonical turn budgets")
    return state.turn_budget


def close_turn_with_attack(
    schedule: TurnScheduleState,
    current_state: UnifiedState,
    *,
    take_another_turn: bool = False,
    skip_pokemon_checkup: bool = False,
) -> tuple[TurnScheduleState, UnifiedState] | None:
    """Close the current canonical budget and optionally queue an extra turn."""

    if skip_pokemon_checkup and not take_another_turn:
        raise ValueError("checkup skip requires an extra-turn effect")
    _budget(current_state)

    next_state = consume_turn_action(current_state, TurnAction.ATTACK)
    if next_state is None:
        return None
    next_schedule = replace(
        schedule,
        extra_turn_queued=take_another_turn,
        skip_checkup_before_next_turn=(
            take_another_turn and skip_pokemon_checkup
        ),
    )
    return next_schedule, next_state


def close_turn_voluntarily(
    schedule: TurnScheduleState,
    current_state: UnifiedState,
) -> tuple[TurnScheduleState, UnifiedState] | None:
    """End the current turn without attacking."""

    _budget(current_state)
    next_state = consume_turn_action(current_state, TurnAction.END_TURN)
    if next_state is None:
        return None
    return (
        replace(
            schedule,
            extra_turn_queued=False,
            skip_checkup_before_next_turn=False,
        ),
        next_state,
    )


def _reset_budget(state: UnifiedState) -> UnifiedState:
    budget = _budget(state).next_turn()
    return apply_budget_to_unified(state, budget)


def advance_turn(
    schedule: TurnScheduleState,
    current_state: UnifiedState,
    other_state: UnifiedState,
) -> CanonicalTurnAdvance | None:
    """Advance to the scheduled turn using only UnifiedState-owned budgets."""

    current_budget = _budget(current_state)
    _budget(other_state)
    if not current_budget.turn_ended:
        return None

    if schedule.extra_turn_queued:
        next_current = _reset_budget(current_state)
        return CanonicalTurnAdvance(
            schedule=TurnScheduleState(
                current_player=schedule.current_player,
                other_player=schedule.other_player,
            ),
            current_state=next_current,
            other_state=other_state,
            pokemon_checkup_occurs=(
                not schedule.skip_checkup_before_next_turn
            ),
            same_player_continues=True,
        )

    next_current = _reset_budget(other_state)
    return CanonicalTurnAdvance(
        schedule=TurnScheduleState(
            current_player=schedule.other_player,
            other_player=schedule.current_player,
        ),
        current_state=next_current,
        other_state=current_state,
        pokemon_checkup_occurs=True,
        same_player_continues=False,
    )
