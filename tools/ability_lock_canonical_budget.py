"""Feed effective Ability-lock state into the canonical turn-budget owner."""

from __future__ import annotations

from ability_lock_causal_state import AbilityLockCausalState
from board_action_quota_derivation import refresh_canonical_action_quotas
from canonical_turn_budget_owner import CanonicalCompositeTurnState


def refresh_canonical_budget_from_lock_state(
    state: CanonicalCompositeTurnState,
    lock_state: AbilityLockCausalState,
    *,
    board_owner: str = "player",
) -> CanonicalCompositeTurnState | None:
    """Refresh quota grants from one resolved causal suppression overlay."""

    if board_owner not in {"player", "opponent"}:
        raise ValueError("board_owner must be 'player' or 'opponent'")
    if not lock_state.resolved:
        return None

    resolution = lock_state.resolution
    suppressed = (
        resolution.player_suppressed_object_ids
        if board_owner == "player"
        else resolution.opponent_suppressed_object_ids
    )
    if suppressed is None:
        return None

    return refresh_canonical_action_quotas(
        state,
        suppressed_ability_object_ids=suppressed,
    )
