"""Pre-exit Ability visibility for simultaneous in-play departures.

Leave-play and Knock-Out trigger eligibility can depend on suppression that is
still active immediately before a simultaneous batch of Pokemon leaves play.
This module snapshots effective Ability availability from a resolved causal lock
state without mutating the physical boards.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ability_lock_causal_state import AbilityLockCausalState
from board_object_kernel import BoardState


@dataclass(frozen=True)
class PreExitAbilityVisibility:
    player_exiting_ids: frozenset[str]
    opponent_exiting_ids: frozenset[str]
    player_enabled_ability_ids: frozenset[str]
    opponent_enabled_ability_ids: frozenset[str]

    def ability_enabled(self, owner: str, object_id: str) -> bool:
        if owner == "player":
            return object_id in self.player_enabled_ability_ids
        if owner == "opponent":
            return object_id in self.opponent_enabled_ability_ids
        raise ValueError("owner must be 'player' or 'opponent'")


def _checked_ids(board: BoardState, object_ids: Iterable[str]) -> frozenset[str]:
    ids = frozenset(object_ids)
    for object_id in ids:
        board.get(object_id)
    return ids


def snapshot_pre_exit_ability_visibility(
    player_board: BoardState,
    opponent_board: BoardState,
    lock_state: AbilityLockCausalState,
    *,
    player_exiting_ids: Iterable[str] = (),
    opponent_exiting_ids: Iterable[str] = (),
) -> PreExitAbilityVisibility | None:
    """Return Ability availability immediately before one simultaneous exit."""

    if not lock_state.resolved:
        return None

    resolution = lock_state.resolution
    player_suppressed = resolution.player_suppressed_object_ids
    opponent_suppressed = resolution.opponent_suppressed_object_ids
    if player_suppressed is None or opponent_suppressed is None:
        return None

    player_ids = _checked_ids(player_board, player_exiting_ids)
    opponent_ids = _checked_ids(opponent_board, opponent_exiting_ids)

    player_enabled = frozenset(
        object_id
        for object_id in player_ids
        if player_board.get(object_id).abilities_enabled
        and object_id not in player_suppressed
    )
    opponent_enabled = frozenset(
        object_id
        for object_id in opponent_ids
        if opponent_board.get(object_id).abilities_enabled
        and object_id not in opponent_suppressed
    )

    return PreExitAbilityVisibility(
        player_exiting_ids=player_ids,
        opponent_exiting_ids=opponent_ids,
        player_enabled_ability_ids=player_enabled,
        opponent_enabled_ability_ids=opponent_enabled,
    )
