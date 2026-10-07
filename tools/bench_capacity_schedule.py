from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class ReleaseBudget:
    item: int = 0
    ability: int = 0
    supporter: int = 0
    attack: int = 0

    def __post_init__(self) -> None:
        if min(self.item, self.ability, self.supporter, self.attack) < 0:
            raise ValueError("release budgets must be non-negative")


@dataclass(frozen=True)
class ScheduleResult:
    max_activations: int
    goal_reached: bool
    earliest_goal_turn: int | None
    explored_states: int


@dataclass(frozen=True)
class _State:
    turn: int
    activated: int
    resident: int
    item_left: int
    ability_left: int
    supporter_left: int
    attack_left: int
    supporter_used: bool


def evaluate_bench_schedule(
    *,
    support_activations: int,
    core_bench_slots: int,
    max_turns: int,
    release_budget: ReleaseBudget = ReleaseBudget(),
    bench_capacity: int = 5,
) -> ScheduleResult:
    """Exact BFS for transactional Bench support under typed release windows.

    Core Bench occupancy is persistent. Each support activation benches one new
    transactional support and leaves it resident until a release action removes
    one resident support. Item and Ability releases do not consume a per-turn
    window in this abstract kernel. At most one Supporter release may be used per
    turn. An attack release ends the current turn immediately.

    Release actions are generic resources whose card-specific targeting and
    accessibility must be established before supplying their budgets here.
    """

    if support_activations < 0:
        raise ValueError("support_activations must be non-negative")
    if not 0 <= core_bench_slots <= bench_capacity:
        raise ValueError("core_bench_slots must fit on the Bench")
    if max_turns <= 0:
        raise ValueError("max_turns must be positive")

    transactional_capacity = bench_capacity - core_bench_slots
    if support_activations == 0:
        return ScheduleResult(0, True, 1, 1)
    if transactional_capacity == 0:
        return ScheduleResult(0, False, None, 1)

    initial = _State(
        turn=1,
        activated=0,
        resident=0,
        item_left=release_budget.item,
        ability_left=release_budget.ability,
        supporter_left=release_budget.supporter,
        attack_left=release_budget.attack,
        supporter_used=False,
    )
    queue = deque([initial])
    seen = {initial}
    max_activated = 0
    earliest: int | None = None

    def push(state: _State) -> None:
        if state not in seen:
            seen.add(state)
            queue.append(state)

    while queue:
        state = queue.popleft()
        max_activated = max(max_activated, state.activated)
        if state.activated >= support_activations:
            earliest = state.turn if earliest is None else min(earliest, state.turn)
            continue

        if state.resident < transactional_capacity:
            push(
                _State(
                    turn=state.turn,
                    activated=state.activated + 1,
                    resident=state.resident + 1,
                    item_left=state.item_left,
                    ability_left=state.ability_left,
                    supporter_left=state.supporter_left,
                    attack_left=state.attack_left,
                    supporter_used=state.supporter_used,
                )
            )

        if state.resident > 0 and state.item_left > 0:
            push(
                _State(
                    turn=state.turn,
                    activated=state.activated,
                    resident=state.resident - 1,
                    item_left=state.item_left - 1,
                    ability_left=state.ability_left,
                    supporter_left=state.supporter_left,
                    attack_left=state.attack_left,
                    supporter_used=state.supporter_used,
                )
            )

        if state.resident > 0 and state.ability_left > 0:
            push(
                _State(
                    turn=state.turn,
                    activated=state.activated,
                    resident=state.resident - 1,
                    item_left=state.item_left,
                    ability_left=state.ability_left - 1,
                    supporter_left=state.supporter_left,
                    attack_left=state.attack_left,
                    supporter_used=state.supporter_used,
                )
            )

        if (
            state.resident > 0
            and state.supporter_left > 0
            and not state.supporter_used
        ):
            push(
                _State(
                    turn=state.turn,
                    activated=state.activated,
                    resident=state.resident - 1,
                    item_left=state.item_left,
                    ability_left=state.ability_left,
                    supporter_left=state.supporter_left - 1,
                    attack_left=state.attack_left,
                    supporter_used=True,
                )
            )

        if state.turn < max_turns:
            push(
                _State(
                    turn=state.turn + 1,
                    activated=state.activated,
                    resident=state.resident,
                    item_left=state.item_left,
                    ability_left=state.ability_left,
                    supporter_left=state.supporter_left,
                    attack_left=state.attack_left,
                    supporter_used=False,
                )
            )

            if state.resident > 0 and state.attack_left > 0:
                push(
                    _State(
                        turn=state.turn + 1,
                        activated=state.activated,
                        resident=state.resident - 1,
                        item_left=state.item_left,
                        ability_left=state.ability_left,
                        supporter_left=state.supporter_left,
                        attack_left=state.attack_left - 1,
                        supporter_used=False,
                    )
                )

    return ScheduleResult(
        max_activations=max_activated,
        goal_reached=earliest is not None,
        earliest_goal_turn=earliest,
        explored_states=len(seen),
    )
