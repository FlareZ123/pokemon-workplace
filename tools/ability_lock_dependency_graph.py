"""Dependency analysis for multiple continuous Ability-lock sources.

The single-source profile layer defines who each source would suppress if that
source were functioning. This module composes those predicates when the source
dependency graph is acyclic. Cycles are reported explicitly instead of assigning
an unsupported fixed point.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from board_object_kernel import BoardState
from single_source_ability_lock_geometry import (
    profile_for_source,
    single_source_suppressed_object_ids,
    source_profile_active,
)


@dataclass(frozen=True, order=True)
class AbilityLockSourceRef:
    owner: str
    object_id: str

    def __post_init__(self) -> None:
        if self.owner not in {"player", "opponent"}:
            raise ValueError("owner must be 'player' or 'opponent'")


@dataclass(frozen=True)
class AbilityLockResolution:
    potential_sources: tuple[AbilityLockSourceRef, ...]
    suppression_edges: tuple[
        tuple[AbilityLockSourceRef, AbilityLockSourceRef], ...
    ]
    unresolved_cycles: tuple[tuple[AbilityLockSourceRef, ...], ...]
    active_sources: tuple[AbilityLockSourceRef, ...] | None
    player_suppressed_object_ids: frozenset[str] | None
    opponent_suppressed_object_ids: frozenset[str] | None

    @property
    def resolved(self) -> bool:
        return self.active_sources is not None


def _board_for(
    ref: AbilityLockSourceRef,
    player_board: BoardState,
    opponent_board: BoardState,
) -> BoardState:
    return player_board if ref.owner == "player" else opponent_board


def potential_sources(
    player_board: BoardState,
    opponent_board: BoardState,
) -> tuple[AbilityLockSourceRef, ...]:
    """Return sources whose non-suppression activation conditions are met."""

    rows: list[AbilityLockSourceRef] = []
    for owner, board in (
        ("player", player_board),
        ("opponent", opponent_board),
    ):
        for pokemon in board.objects:
            profile = profile_for_source(pokemon)
            if profile is None:
                continue
            if source_profile_active(profile, pokemon, board):
                rows.append(AbilityLockSourceRef(owner, pokemon.object_id))
    return tuple(sorted(rows))


def targets_for_source(
    source: AbilityLockSourceRef,
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_name: str | None,
) -> tuple[frozenset[str], frozenset[str]]:
    """Return player/opponent object IDs this one source would suppress."""

    if source.owner == "player":
        player_ids = single_source_suppressed_object_ids(
            player_board,
            opponent_board,
            source_owner="player",
            source_object_id=source.object_id,
            stadium_name=stadium_name,
        )
        opponent_ids = single_source_suppressed_object_ids(
            opponent_board,
            player_board,
            source_owner="opponent",
            source_object_id=source.object_id,
            stadium_name=stadium_name,
        )
    else:
        player_ids = single_source_suppressed_object_ids(
            player_board,
            opponent_board,
            source_owner="opponent",
            source_object_id=source.object_id,
            stadium_name=stadium_name,
        )
        opponent_ids = single_source_suppressed_object_ids(
            opponent_board,
            player_board,
            source_owner="player",
            source_object_id=source.object_id,
            stadium_name=stadium_name,
        )
    return player_ids, opponent_ids


def suppression_edges(
    player_board: BoardState,
    opponent_board: BoardState,
    sources: Iterable[AbilityLockSourceRef],
    *,
    stadium_name: str | None = None,
) -> tuple[tuple[AbilityLockSourceRef, AbilityLockSourceRef], ...]:
    """Return potential source -> source suppression dependencies."""

    source_tuple = tuple(sources)
    source_set = set(source_tuple)
    edges: set[tuple[AbilityLockSourceRef, AbilityLockSourceRef]] = set()

    for source in source_tuple:
        player_ids, opponent_ids = targets_for_source(
            source,
            player_board,
            opponent_board,
            stadium_name=stadium_name,
        )
        for target in source_set:
            if target == source:
                continue
            target_ids = (
                player_ids if target.owner == "player" else opponent_ids
            )
            if target.object_id in target_ids:
                edges.add((source, target))
    return tuple(sorted(edges))


def _strongly_connected_cycles(
    sources: tuple[AbilityLockSourceRef, ...],
    edges: tuple[tuple[AbilityLockSourceRef, AbilityLockSourceRef], ...],
) -> tuple[tuple[AbilityLockSourceRef, ...], ...]:
    """Return SCCs that contain a directed cycle."""

    adjacency = {source: [] for source in sources}
    for left, right in edges:
        adjacency[left].append(right)

    index = 0
    stack: list[AbilityLockSourceRef] = []
    on_stack: set[AbilityLockSourceRef] = set()
    indices: dict[AbilityLockSourceRef, int] = {}
    lowlink: dict[AbilityLockSourceRef, int] = {}
    components: list[tuple[AbilityLockSourceRef, ...]] = []

    def visit(node: AbilityLockSourceRef) -> None:
        nonlocal index
        indices[node] = index
        lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for nxt in adjacency[node]:
            if nxt not in indices:
                visit(nxt)
                lowlink[node] = min(lowlink[node], lowlink[nxt])
            elif nxt in on_stack:
                lowlink[node] = min(lowlink[node], indices[nxt])

        if lowlink[node] != indices[node]:
            return
        component: list[AbilityLockSourceRef] = []
        while True:
            row = stack.pop()
            on_stack.remove(row)
            component.append(row)
            if row == node:
                break
        component_tuple = tuple(sorted(component))
        if len(component_tuple) > 1:
            components.append(component_tuple)

    for source in sources:
        if source not in indices:
            visit(source)

    return tuple(sorted(components))


def resolve_ability_lock_dependencies(
    player_board: BoardState,
    opponent_board: BoardState,
    *,
    stadium_name: str | None = None,
) -> AbilityLockResolution:
    """Resolve an acyclic source graph or report circular dependencies."""

    sources = potential_sources(player_board, opponent_board)
    edges = suppression_edges(
        player_board,
        opponent_board,
        sources,
        stadium_name=stadium_name,
    )
    cycles = _strongly_connected_cycles(sources, edges)
    if cycles:
        return AbilityLockResolution(
            potential_sources=sources,
            suppression_edges=edges,
            unresolved_cycles=cycles,
            active_sources=None,
            player_suppressed_object_ids=None,
            opponent_suppressed_object_ids=None,
        )

    predecessors = {source: [] for source in sources}
    successors = {source: [] for source in sources}
    for left, right in edges:
        predecessors[right].append(left)
        successors[left].append(right)

    indegree = {source: len(predecessors[source]) for source in sources}
    ready = sorted(source for source in sources if indegree[source] == 0)
    order: list[AbilityLockSourceRef] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for nxt in successors[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
                ready.sort()

    if len(order) != len(sources):
        raise AssertionError("cycle detection and topological ordering disagree")

    active: dict[AbilityLockSourceRef, bool] = {}
    for source in order:
        active[source] = not any(
            active[pred] for pred in predecessors[source]
        )

    active_sources = tuple(
        source for source in sources if active[source]
    )
    player_suppressed: set[str] = set()
    opponent_suppressed: set[str] = set()
    for source in active_sources:
        player_ids, opponent_ids = targets_for_source(
            source,
            player_board,
            opponent_board,
            stadium_name=stadium_name,
        )
        player_suppressed.update(player_ids)
        opponent_suppressed.update(opponent_ids)

    return AbilityLockResolution(
        potential_sources=sources,
        suppression_edges=edges,
        unresolved_cycles=(),
        active_sources=active_sources,
        player_suppressed_object_ids=frozenset(player_suppressed),
        opponent_suppressed_object_ids=frozenset(opponent_suppressed),
    )
