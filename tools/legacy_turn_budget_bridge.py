"""Compatibility bridge from legacy split turn flags to TurnActionBudget.

This module is transitional. It lets current kernels share one projected view of
ordinary per-turn action bandwidth without requiring an immediate breaking state
rewrite. Reverse synchronization is intentionally restricted to states the
legacy booleans can represent exactly.
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
    supporter_play_limit: int = 1,
    stadium_play_limit: int = 1,
    manual_energy_attachment_limit: int = 1,
    retreat_limit: int = 1,
) -> TurnActionBudget:
    """Project legacy flags plus currently derived action limits.

    Once UnifiedState owns an explicit budget, that value is authoritative and
    the legacy limit arguments are ignored.
    """

    if state.turn_budget is not None:
        return state.turn_budget

    return TurnActionBudget(
        supporter_used=state.bench.supporter_used,
        supporter_play_limit=supporter_play_limit,
        stadium_play_used=state.stadium_used,
        stadium_play_limit=stadium_play_limit,
        manual_energy_attachment_used=state.manual_attachment_used,
        manual_energy_attachment_limit=manual_energy_attachment_limit,
        retreat_used=retreat_used,
        retreat_limit=retreat_limit,
        turn_ended=state.bench.turn_ended,
    )


def project_composite_turn_budget(
    unified: UnifiedState,
    board: BoardState,
    *,
    supporter_play_limit: int = 1,
    stadium_play_limit: int = 1,
    manual_energy_attachment_limit: int = 1,
    retreat_limit: int = 1,
) -> TurnActionBudget:
    """Project one budget from the current unified and board-object kernels."""

    return project_unified_turn_budget(
        unified,
        retreat_used=board.retreat_used,
        supporter_play_limit=supporter_play_limit,
        stadium_play_limit=stadium_play_limit,
        manual_energy_attachment_limit=manual_energy_attachment_limit,
        retreat_limit=retreat_limit,
    )


def apply_budget_to_unified(
    state: UnifiedState,
    budget: TurnActionBudget,
) -> UnifiedState:
    """Synchronize a budget into UnifiedState.

    Canonical states retain the full integer quota and mirror only boolean
    compatibility fields. Legacy-only states still reject lossy quota shapes.
    """

    if state.turn_budget is not None:
        return replace(
            state,
            turn_budget=budget,
            bench=replace(
                state.bench,
                supporter_used=budget.supporter_used,
                turn_ended=budget.turn_ended,
            ),
            stadium_used=budget.stadium_play_used,
            manual_attachment_used=budget.manual_energy_attachment_used,
        )

    if (
        budget.supporter_play_limit != 1
        or budget.stadium_play_limit != 1
        or budget.manual_energy_attachment_limit != 1
        or budget.supporter_plays_used > 1
        or budget.stadium_plays_used > 1
        or budget.manual_energy_attachments_used > 1
    ):
        raise ValueError(
            "legacy UnifiedState/BenchState cannot exactly encode modified "
            "action quotas"
        )

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
    """Synchronize exactly representable Retreat state into BoardState."""

    if budget.retreat_limit != 1 or budget.retreats_used > 1:
        raise ValueError("legacy BoardState cannot exactly encode Retreat quotas")

    next_state = replace(state, retreat_used=budget.retreat_used)
    next_state.validate()
    return next_state
