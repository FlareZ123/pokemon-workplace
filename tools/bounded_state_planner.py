"""Small breadth-first planner over validated immutable state transitions.

This module knows nothing about Pokémon card text. Callers supply named action
generators that already enforce game semantics. The planner only composes those
transitions up to a finite action depth and returns the first shortest goal
witness.

Keeping the planner generic lets exact kernels for Trainer play, Energy,
Bench geometry, locks, or turn boundaries remain the source of mechanical
truth.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Hashable, Iterable, Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar


StateT = TypeVar("StateT", bound=Hashable)

ActionGenerator = Callable[
    [StateT],
    Iterable[tuple[str, StateT]],
]
GoalPredicate = Callable[[StateT], bool]


@dataclass(frozen=True)
class PlanStep(Generic[StateT]):
    label: str
    state: StateT


@dataclass(frozen=True)
class PlanWitness(Generic[StateT]):
    steps: tuple[PlanStep[StateT], ...]
    final_state: StateT

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(step.label for step in self.steps)

    @property
    def depth(self) -> int:
        return len(self.steps)


def shortest_bounded_plan(
    initial_state: StateT,
    actions: Sequence[ActionGenerator[StateT]],
    goal: GoalPredicate[StateT],
    *,
    max_depth: int,
) -> PlanWitness[StateT] | None:
    """Return one shortest plan reaching goal within max_depth actions."""

    if max_depth < 0:
        raise ValueError("max_depth must be non-negative")

    action_generators = tuple(actions)
    if goal(initial_state):
        return PlanWitness((), initial_state)

    queue = deque([(initial_state, ())])
    best_depth = {initial_state: 0}

    while queue:
        state, steps = queue.popleft()
        depth = len(steps)
        if depth >= max_depth:
            continue

        for action in action_generators:
            for label, next_state in action(state):
                if not label:
                    raise ValueError("action labels must be non-empty")
                next_depth = depth + 1
                prior_depth = best_depth.get(next_state)
                if prior_depth is not None and prior_depth <= next_depth:
                    continue

                next_steps = steps + (PlanStep(label, next_state),)
                if goal(next_state):
                    return PlanWitness(next_steps, next_state)

                best_depth[next_state] = next_depth
                queue.append((next_state, next_steps))

    return None
