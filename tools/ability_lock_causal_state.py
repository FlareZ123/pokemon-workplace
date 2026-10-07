"""Causal owner for effective continuous Ability-lock state.

The history-free dependency graph remains the source of current source geometry.
This layer owns the minimal verified precedence continuity needed when that graph
is cyclic:

- setup first-player precedence for the verified two-Active family;
- established Garbotoxin precedence when Cursed Land gains a reverse edge;
- persistence of an already verified cyclic winner while the source graph itself
  remains unchanged.

Unsupported cyclic transitions remain unresolved.
"""

from __future__ import annotations

from dataclasses import dataclass

from ability_lock_dependency_graph import (
    AbilityLockResolution,
    AbilityLockSourceRef,
    resolve_ability_lock_dependencies,
    targets_for_source,
)
from ability_lock_established_precedence import (
    resolve_verified_established_precedence,
)
from ability_lock_setup_precedence import resolve_setup_ability_lock_precedence
from board_object_kernel import BoardState


@dataclass(frozen=True)
class AbilityLockCausalState:
    resolution: AbilityLockResolution
    basis: str

    @property
    def resolved(self) -> bool:
        return self.resolution.resolved


def _materialize_sources(
    base: AbilityLockResolution,
    active_sources: tuple[AbilityLockSourceRef, ...],
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_name: str | None,
) -> AbilityLockResolution:
    player_ids: set[str] = set()
    opponent_ids: set[str] = set()
    for source in active_sources:
        source_player_ids, source_opponent_ids = targets_for_source(
            source,
            player_board,
            opponent_board,
            stadium_name=stadium_name,
        )
        player_ids.update(source_player_ids)
        opponent_ids.update(source_opponent_ids)

    return AbilityLockResolution(
        potential_sources=base.potential_sources,
        suppression_edges=base.suppression_edges,
        unresolved_cycles=(),
        active_sources=active_sources,
        player_suppressed_object_ids=frozenset(player_ids),
        opponent_suppressed_object_ids=frozenset(opponent_ids),
    )


def initialize_snapshot_lock_state(
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_name: str | None = None,
) -> AbilityLockCausalState:
    resolution = resolve_ability_lock_dependencies(
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    return AbilityLockCausalState(
        resolution=resolution,
        basis="snapshot" if resolution.resolved else "unresolved",
    )


def initialize_setup_lock_state(
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    first_player_owner: str,
    stadium_name: str | None = None,
) -> AbilityLockCausalState:
    snapshot = resolve_ability_lock_dependencies(
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    resolution = resolve_setup_ability_lock_precedence(
        player_board,
        opponent_board,
        first_player_owner=first_player_owner,
        stadium_name=stadium_name,
    )
    if snapshot.resolved:
        basis = "snapshot"
    elif resolution.resolved:
        basis = "setup_first_player"
    else:
        basis = "unresolved"
    return AbilityLockCausalState(resolution=resolution, basis=basis)


def advance_lock_state(
    previous: AbilityLockCausalState,
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_name: str | None = None,
) -> AbilityLockCausalState:
    """Advance effective lock state across one board/event boundary."""

    current = resolve_ability_lock_dependencies(
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    if current.resolved:
        return AbilityLockCausalState(current, "snapshot")

    previous_resolution = previous.resolution
    if not previous_resolution.resolved or previous_resolution.active_sources is None:
        return AbilityLockCausalState(current, "unresolved")

    same_source_graph = (
        current.potential_sources == previous_resolution.potential_sources
        and current.suppression_edges == previous_resolution.suppression_edges
    )
    if same_source_graph and all(
        source in current.potential_sources
        for source in previous_resolution.active_sources
    ):
        persisted = _materialize_sources(
            current,
            previous_resolution.active_sources,
            player_board,
            opponent_board,
            stadium_name=stadium_name,
        )
        return AbilityLockCausalState(persisted, previous.basis)

    established = resolve_verified_established_precedence(
        previous_resolution,
        player_board,
        opponent_board,
        stadium_name=stadium_name,
    )
    if established.resolved:
        return AbilityLockCausalState(established, "verified_established")

    return AbilityLockCausalState(current, "unresolved")
