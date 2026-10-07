"""Setup-time precedence for mutually suppressing continuous Abilities.

Official Japanese Pokemon Card Q&A gives the first player's Active Ability
priority when both Active Pokemon begin the game with mutually suppressing
continuous Abilities. This module applies that narrow precedence rule to a
two-source reciprocal Active-Ability cycle. Other cyclic dependency shapes stay
unresolved.
"""

from __future__ import annotations

from ability_lock_dependency_graph import (
    AbilityLockResolution,
    AbilityLockSourceRef,
    resolve_ability_lock_dependencies,
    targets_for_source,
)
from board_object_kernel import BoardState
from single_source_ability_lock_geometry import profile_for_source


def _source_profile(
    source: AbilityLockSourceRef,
    player_board: BoardState,
    opponent_board: BoardState,
):
    board = player_board if source.owner == "player" else opponent_board
    return profile_for_source(board.get(source.object_id))


def resolve_setup_ability_lock_precedence(
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    first_player_owner: str,
    stadium_name: str | None = None,
) -> AbilityLockResolution:
    """Resolve the official two-Active setup precedence case when applicable."""

    if first_player_owner not in {"player", "opponent"}:
        raise ValueError("first_player_owner must be 'player' or 'opponent'")

    base = resolve_ability_lock_dependencies(
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    if base.resolved:
        return base

    if (
        len(base.potential_sources) != 2
        or len(base.unresolved_cycles) != 1
        or len(base.unresolved_cycles[0]) != 2
    ):
        return base

    left, right = base.unresolved_cycles[0]
    if left.owner == right.owner:
        return base

    expected_edges = {(left, right), (right, left)}
    if set(base.suppression_edges) != expected_edges:
        return base

    left_profile = _source_profile(left, player_board, opponent_board)
    right_profile = _source_profile(right, player_board, opponent_board)
    if (
        left_profile is None
        or right_profile is None
        or left_profile.activation != "active"
        or right_profile.activation != "active"
    ):
        return base

    winner = left if left.owner == first_player_owner else right
    player_ids, opponent_ids = targets_for_source(
        winner,
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    return AbilityLockResolution(
        potential_sources=base.potential_sources,
        suppression_edges=base.suppression_edges,
        unresolved_cycles=(),
        active_sources=(winner,),
        player_suppressed_object_ids=player_ids,
        opponent_suppressed_object_ids=opponent_ids,
    )
