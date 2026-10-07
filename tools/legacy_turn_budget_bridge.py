"""Compatibility bridge from legacy split turn flags to TurnActionBudget.

This module is transitional. It lets current kernels share one projected view of
ordinary per-turn action bandwidth without requiring an immediate breaking state
rewrite.
"""

from __future__ import annotations

from dataclasses import replace

from board_object_kernel import BoardState
from turn_action_budget import TurnActionBudget
from unified_state_kernel import UnifiedState


def project_unified_turn_budget(
    state: UnifiedState,
    *,
    retreat_used: bool = False,
) -> TurnActionBudget:
    """Project the turn flags currently spread across UnifiedState and BenchState."""

    return TurnActionBudget(
        supporter_used=state.bench.supporter_used,
        stadium_play_used=state.stadium_used,
        manual_energy_attachment_used=state.manual_attachment_used,
        retreat_used=retreat_used,
        turn_ended=state.bench.turn_ended,
    )


def project_composite_turn_budget(
    unified: UnifiedState,
    board: BoardState,
) -> TurnActionBudget:
    """Project one budget from the current unified and board-object kernels."""

    return project_unified_turn_budget(
        unified,
        retreat_used=board.retreat_used,
    )


def apply_budget_to_unified(
    state: UnifiedState,
    budget: TurnActionBudget,
) -> UnifiedState:
    """Synchronize legacy unified/Bench flags from one projected budget."""

    return replace(
        state,
        bench=replace(
            state.bench,
            supporter_used=budget.supporter_used,
            turn_ended=budget.turn_ended,
        ),
        stadium_used=budget.stadium_play_used,
        manual_attachment_used=budget.manual_energy_attachment_used,
    )


def apply_budget_to_board(
    state: BoardState,
    budget: TurnActionBudget,
) -> BoardState:
    """Synchronize the legacy board Retreat flag from one projected budget."""

    next_state = replace(state, retreat_used=budget.retreat_used)
    next_state.validate()
    return next_state
