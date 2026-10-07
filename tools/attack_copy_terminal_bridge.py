"""Gate copied-attack turn scheduling behind post-Knock-Out game resolution.

A pending turn-boundary consequence from a copied body is only actionable after
the Knock Out, Prize-window, terminal, and replacement-Active phases have
finished. This adapter consumes the existing post-Prize-window context rather
than duplicating those rules.
"""

from __future__ import annotations

from dataclasses import dataclass

from attack_copy_kernel import Resolution as CopyResolution
from attack_copy_turn_boundary_bridge import close_declared_attack
from canonical_turn_sequence_owner import TurnScheduleState
from post_knockout_game_resolution import Resolution as GameResolution
from post_prize_window_game_resolution import PrizeWindowResolution
from promotion_pending_conservation import finalize_promotions
from stack_knockout_conservation import StackBoardMaterialState
from unified_state_kernel import UnifiedState


@dataclass(frozen=True)
class CopyAttackMatchBoundary:
    """Result of attempting to leave the copied attack's KO/game phases."""

    game_resolution: GameResolution
    boards: tuple[tuple[str, StackBoardMaterialState], ...] | None
    turn_closure: tuple[TurnScheduleState, UnifiedState] | None

    @property
    def terminal(self) -> bool:
        return self.game_resolution.terminal


def close_copy_attack_after_game_resolution(
    *,
    schedule: TurnScheduleState,
    current_state: UnifiedState,
    copy_resolution: CopyResolution,
    prize_window_resolution: PrizeWindowResolution,
) -> CopyAttackMatchBoundary | None:
    """Close a copied attack only after terminal resolution and promotion.

    Terminal games never reach the turn scheduler. Continuing games remain
    blocked until every required replacement Active has been chosen and the
    promotion-pending context can be converted back into ordinary stack boards.
    """

    game_resolution = prize_window_resolution.resolution
    if game_resolution.terminal:
        return CopyAttackMatchBoundary(
            game_resolution=game_resolution,
            boards=None,
            turn_closure=None,
        )

    boards = finalize_promotions(prize_window_resolution.context)
    if boards is None:
        return None

    closed = close_declared_attack(
        schedule,
        current_state,
        copy_resolution,
    )
    if closed is None:
        return None

    return CopyAttackMatchBoundary(
        game_resolution=game_resolution,
        boards=boards,
        turn_closure=closed,
    )
