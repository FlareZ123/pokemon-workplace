"""Bound Stadium activation chains by fixed-board Basic target capacity.

Source availability and effect-use identity are delegated to the existing
physical Stadium model. This model contributes one additional binding
constraint: every resident Gothitelle source and every reserved non-target
Pokémon occupies one of the six ordinary in-play Pokémon positions. With
no board release or replacement, each successful Grand Tree activation
consumes one *distinct* eligible Basic target from the remaining slots.

The same-copy effect-use policy remains unresolved by official evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from stadium_reentry_usage_bounds import (
    StadiumReentryState,
    UsagePolicy,
    activate,
    ordinary_play_successors,
    teleport_successors,
)


@dataclass(frozen=True)
class CapacityFrontierState:
    stadium: StadiumReentryState
    ready: frozenset[str]
    evolved: frozenset[str] = frozenset()
    reserved_non_targets: int = 0

    def __post_init__(self) -> None:
        if self.reserved_non_targets < 0:
            raise ValueError("Negative reserved Pokémon count")
        if self.ready & self.evolved:
            raise ValueError("One physical Basic cannot be ready and evolved")
        if (
            len(self.stadium.entry.teleport_room_sources)
            + self.reserved_non_targets
            + len(self.ready)
            + len(self.evolved)
            > 6
        ):
            raise ValueError("The abstract board exceeds Active + 5 Bench")


def maximize_target_evolutions(
    initial: CapacityFrontierState,
    policy: UsagePolicy,
    *,
    include_normal_play: bool = True,
) -> tuple[int, tuple[str, ...]]:
    """Search all source orders and distinct eligible-Basic effect resolutions."""
    agenda = [(initial, ())]
    seen = {initial}
    best = (len(initial.evolved), ())
    while agenda:
        state, trace = agenda.pop()
        if len(state.evolved) > best[0]:
            best = (len(state.evolved), trace)

        if state.ready:
            after_use = activate(state.stadium, policy)
            if after_use is not None:
                for target in sorted(state.ready):
                    evolved = replace(
                        state,
                        stadium=after_use,
                        ready=state.ready - {target},
                        evolved=state.evolved | {target},
                    )
                    if evolved not in seen:
                        seen.add(evolved)
                        agenda.append((evolved, trace + ("evolve:" + target,)))

        if include_normal_play:
            for stadium in ordinary_play_successors(state.stadium):
                successor = replace(state, stadium=stadium)
                if successor not in seen:
                    seen.add(successor)
                    agenda.append((successor, trace + ("ordinary-play",)))

        for source in sorted(
            state.stadium.entry.teleport_room_sources
            - state.stadium.entry.teleport_room_used
        ):
            for stadium in teleport_successors(state.stadium, source):
                successor = replace(state, stadium=stadium)
                if successor not in seen:
                    seen.add(successor)
                    agenda.append((successor, trace + ("teleport:" + source,)))
    return best
