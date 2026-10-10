"""Conditional Grand Tree construction of additional Gothitelle Ability sources."""

from __future__ import annotations
from dataclasses import dataclass, replace
from stadium_reentry_usage_bounds import (
    StadiumReentryState, UsagePolicy, activate, ordinary_play_successors,
    teleport_successors,
)


@dataclass(frozen=True)
class BootstrapState:
    stadium: StadiumReentryState
    ready: int
    made: int = 0
    other: int = 0

    def __post_init__(self) -> None:
        if min(self.ready, self.made, self.other) < 0:
            raise ValueError("Negative board population")
        if len(self.stadium.entry.teleport_room_sources) + self.ready + self.other > 6:
            raise ValueError("Ordinary board capacity exceeded")


def build_gothitelle(state: BootstrapState, policy: UsagePolicy) -> BootstrapState | None:
    """One eligible Gothita evolves into a new source, consuming one ready Basic."""
    if not state.ready:
        return None
    used = activate(state.stadium, policy)
    if used is None:
        return None
    source = "built-" + str(state.made + 1)
    if source in used.entry.teleport_room_sources:
        raise ValueError("Duplicate source identity")
    entry = replace(
        used.entry, teleport_room_sources=used.entry.teleport_room_sources | {source}
    )
    return replace(
        state, stadium=replace(used, entry=entry),
        ready=state.ready - 1, made=state.made + 1,
    )


def maximize_built(
    start: BootstrapState, policy: UsagePolicy, *,
    allow_play: bool = True,
) -> tuple[int, tuple[str, ...]]:
    """Exhaustive turn search, symmetry-reducing equivalent ready Gothita."""
    stack = [(start, ())]
    seen = {start}
    best = (start.made, ())
    while stack:
        state, path = stack.pop()
        if state.made > best[0]:
            best = (state.made, path)
        evolved = build_gothitelle(state, policy)
        if evolved is not None and evolved not in seen:
            seen.add(evolved)
            stack.append((evolved, path + ("evolve",)))
        if allow_play:
            for result in ordinary_play_successors(state.stadium):
                successor = replace(state, stadium=result)
                if successor not in seen:
                    seen.add(successor)
                    stack.append((successor, path + ("play",)))
        remaining = state.stadium.entry.teleport_room_sources - state.stadium.entry.teleport_room_used
        for source in sorted(remaining):
            for result in teleport_successors(state.stadium, source):
                successor = replace(state, stadium=result)
                if successor not in seen:
                    seen.add(successor)
                    stack.append((successor, path + ("teleport:" + source,)))
    return best
