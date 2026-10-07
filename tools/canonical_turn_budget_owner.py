"""Canonical ownership adapter for per-turn action bandwidth.

UnifiedState can own the integer TurnActionBudget directly. This module joins
that owner to BoardState for physical Retreat execution while keeping the legacy
retreat_used boolean as a compatibility projection only.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from board_object_kernel import BoardState, EnergyAttachment, retreat
from legacy_turn_budget_bridge import project_composite_turn_budget
from turn_action_budget import TurnAction, TurnActionBudget
from unified_state_kernel import UnifiedState, consume_turn_action


@dataclass(frozen=True)
class CanonicalCompositeTurnState:
    unified: UnifiedState
    board: BoardState

    def __post_init__(self) -> None:
        if self.unified.turn_budget is None:
            raise ValueError("UnifiedState must own a canonical turn budget")
        if self.board.retreat_used != self.unified.turn_budget.retreat_used:
            raise ValueError(
                "legacy BoardState.retreat_used must mirror whether canonical "
                "Retreat usage is nonzero"
            )

    @property
    def budget(self) -> TurnActionBudget:
        budget = self.unified.turn_budget
        assert budget is not None
        return budget


def promote_composite_turn_budget(
    unified: UnifiedState,
    board: BoardState,
    *,
    supporter_play_limit: int = 1,
    stadium_play_limit: int = 1,
    manual_energy_attachment_limit: int = 1,
    retreat_limit: int = 1,
) -> CanonicalCompositeTurnState:
    """Materialize one authoritative budget from a legacy composite state."""

    if unified.turn_budget is None:
        budget = project_composite_turn_budget(
            unified,
            board,
            supporter_play_limit=supporter_play_limit,
            stadium_play_limit=stadium_play_limit,
            manual_energy_attachment_limit=manual_energy_attachment_limit,
            retreat_limit=retreat_limit,
        )
        unified = replace(unified, turn_budget=budget)
    return CanonicalCompositeTurnState(unified=unified, board=board)


def with_canonical_budget(
    state: CanonicalCompositeTurnState,
    budget: TurnActionBudget,
) -> CanonicalCompositeTurnState:
    """Replace the canonical budget and refresh the Retreat compatibility bit."""

    unified = replace(state.unified, turn_budget=budget)
    board = replace(state.board, retreat_used=budget.retreat_used)
    board.validate()
    return CanonicalCompositeTurnState(unified=unified, board=board)


def retreat_with_canonical_budget(
    state: CanonicalCompositeTurnState,
    bench_object_id: str,
    *,
    retreat_cost: int,
    discard_energy_ids: Iterable[str],
) -> tuple[CanonicalCompositeTurnState, tuple[EnergyAttachment, ...]] | None:
    """Execute physical Retreat while the canonical budget owns its quota.

    BoardState.retreat_used is cleared only in the temporary compatibility view
    passed to the legacy board transition. The canonical budget decides whether
    another Retreat is allowed, so integer quotas remain representable.
    """

    if not state.budget.can(TurnAction.RETREAT):
        return None

    legacy_board_view = replace(state.board, retreat_used=False)
    resolved = retreat(
        legacy_board_view,
        bench_object_id,
        retreat_cost=retreat_cost,
        discard_energy_ids=discard_energy_ids,
    )
    if resolved is None:
        return None
    board, discarded = resolved

    unified = consume_turn_action(state.unified, TurnAction.RETREAT)
    assert unified is not None
    budget = unified.turn_budget
    assert budget is not None
    board = replace(board, retreat_used=budget.retreat_used)
    board.validate()
    return CanonicalCompositeTurnState(unified=unified, board=board), discarded
