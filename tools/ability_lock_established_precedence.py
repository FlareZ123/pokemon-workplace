"""Verified causal precedence for an established continuous Ability lock.

A Japanese Pokemon Card Q&A rules that an already-working Garbotoxin continues
to suppress Ting-Lu ex's Cursed Land when damage counters are later placed on
the Tool-attached Garbodor. The new damage condition would create a reciprocal
suppression cycle in a history-free snapshot, so the previous resolved state is
mechanically relevant.

This module intentionally supports only the verified Garbotoxin -> Cursed Land
transition. Other newly cyclic states remain unresolved.
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


VERIFIED_ESTABLISHED_PRECEDENCE = frozenset({("Garbotoxin", "Cursed Land")})


def _source_profile_name(
    source: AbilityLockSourceRef,
    player_board: BoardState,
    opponent_board: BoardState,
) -> str | None:
    board = player_board if source.owner == "player" else opponent_board
    profile = profile_for_source(board.get(source.object_id))
    return None if profile is None else profile.name


def resolve_verified_established_precedence(
    previous: AbilityLockResolution,
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_name: str | None = None,
) -> AbilityLockResolution:
    """Preserve a verified established suppressor through a newly reciprocal edge."""

    current = resolve_ability_lock_dependencies(
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    if current.resolved:
        return current

    if (
        not previous.resolved
        or previous.active_sources is None
        or len(previous.active_sources) != 1
        or len(current.potential_sources) != 2
        or len(current.unresolved_cycles) != 1
        or len(current.unresolved_cycles[0]) != 2
    ):
        return current

    winner = previous.active_sources[0]
    cycle = current.unresolved_cycles[0]
    if winner not in cycle:
        return current
    loser = cycle[0] if cycle[1] == winner else cycle[1]

    if (winner, loser) not in previous.suppression_edges:
        return current
    if (loser, winner) in previous.suppression_edges:
        return current

    if set(current.suppression_edges) != {(winner, loser), (loser, winner)}:
        return current

    winner_name = _source_profile_name(winner, player_board, opponent_board)
    loser_name = _source_profile_name(loser, player_board, opponent_board)
    if (winner_name, loser_name) not in VERIFIED_ESTABLISHED_PRECEDENCE:
        return current

    player_ids, opponent_ids = targets_for_source(
        winner,
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    return AbilityLockResolution(
        potential_sources=current.potential_sources,
        suppression_edges=current.suppression_edges,
        unresolved_cycles=(),
        active_sources=(winner,),
        player_suppressed_object_ids=player_ids,
        opponent_suppressed_object_ids=opponent_ids,
    )
