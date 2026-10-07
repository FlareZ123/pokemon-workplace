"""Evaluate typed card actions from canonical board and temporal lock state."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from ability_lock_causal_state import AbilityLockCausalState
from attack_restriction_turn_windows import AttackRestrictionWindow
from board_derived_continuous_restrictions import active_restrictions_from_boards
from board_object_kernel import BoardState
from source_scoped_action_restrictions import (
    CardActionAttempt,
    SourceScopedActionRestriction,
    restriction_blocks_attempt,
)
from source_scoped_channel_projection import (
    SourceScopedPermissionProjection,
    action_allowed,
    project_source_scoped_permissions,
)
from source_scoped_restriction_activation import RestrictionActivationProfile


@dataclass(frozen=True)
class BoardDerivedActionPermission:
    attempt: CardActionAttempt
    active_restrictions: tuple[SourceScopedActionRestriction, ...]
    projection: SourceScopedPermissionProjection
    blocking_restrictions: tuple[SourceScopedActionRestriction, ...]
    allowed: bool


def evaluate_board_derived_action_permission(
    attempt: CardActionAttempt,
    *,
    player: str,
    player_board: BoardState,
    opponent_board: BoardState,
    profiles: Sequence[RestrictionActivationProfile],
    lock_state: AbilityLockCausalState,
    stadium_name: str | None = None,
    player_id: str = "player",
    opponent_id: str = "opponent",
    attack_windows: Sequence[AttackRestrictionWindow] = (),
) -> BoardDerivedActionPermission:
    """Evaluate one typed action against every currently active restriction."""

    restrictions = active_restrictions_from_boards(
        player,
        player_board,
        opponent_board,
        profiles=profiles,
        lock_state=lock_state,
        stadium_name=stadium_name,
        player_id=player_id,
        opponent_id=opponent_id,
        attack_windows=attack_windows,
    )
    projection = project_source_scoped_permissions(restrictions)
    blockers = tuple(
        restriction
        for restriction in restrictions
        if restriction_blocks_attempt(restriction, attempt)
    )
    allowed = action_allowed(projection, attempt)
    if allowed != (not blockers):
        raise AssertionError(
            "typed predicate and channel/residual projection disagree"
        )
    return BoardDerivedActionPermission(
        attempt=attempt,
        active_restrictions=restrictions,
        projection=projection,
        blocking_restrictions=blockers,
        allowed=allowed,
    )
