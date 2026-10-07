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
from target_bound_attack_restrictions import (
    TargetBoundAttackRestrictionWindow,
    target_bound_restriction_blocks_attempt,
)


@dataclass(frozen=True)
class BoardDerivedActionPermission:
    attempt: CardActionAttempt
    active_restrictions: tuple[SourceScopedActionRestriction, ...]
    target_bound_windows: tuple[TargetBoundAttackRestrictionWindow, ...]
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
    target_bound_attack_windows: Sequence[TargetBoundAttackRestrictionWindow] = (),
    target_object_id: str | None = None,
) -> BoardDerivedActionPermission:
    """Evaluate one typed action against every currently active restriction.

    Defending-Pokemon attack restrictions must be supplied as target-bound
    windows. Their target relation is derived from physical object identity.
    """

    if any(
        window.restriction.required_target_relation is not None
        for window in attack_windows
    ):
        raise ValueError(
            "target-scoped attack restrictions require physical target binding"
        )
    if target_bound_attack_windows and target_object_id is None:
        raise ValueError(
            "target_object_id is required with target-bound attack restrictions"
        )

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
    ordinary_blockers = tuple(
        restriction
        for restriction in restrictions
        if restriction_blocks_attempt(restriction, attempt)
    )
    ordinary_allowed = action_allowed(projection, attempt)
    if ordinary_allowed != (not ordinary_blockers):
        raise AssertionError(
            "typed predicate and channel/residual projection disagree"
        )

    bound_rows = tuple(target_bound_attack_windows)
    bound_blockers = tuple(
        bound.window.restriction
        for bound in bound_rows
        if target_bound_restriction_blocks_attempt(
            bound,
            player=player,
            attempt=attempt,
            target_object_id=target_object_id or "",
        )
    )
    blockers = ordinary_blockers + bound_blockers
    return BoardDerivedActionPermission(
        attempt=attempt,
        active_restrictions=restrictions,
        target_bound_windows=bound_rows,
        projection=projection,
        blocking_restrictions=blockers,
        allowed=ordinary_allowed and not bound_blockers,
    )
