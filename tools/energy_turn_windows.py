"""Turn-aware setup search for represented Energy attack lines.

The opponent's intervening turns are assumed inert. Physical zones, attached
Energy, and live Stadium effects persist while ordinary quotas refresh.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from heapq import heappop, heappush
from itertools import count
from typing import Callable, Sequence

from turn_action_budget import TurnAction, TurnActionBudget, budget_from_flags
from typed_energy_access import (
    Action,
    EnergyAccessState,
    attach_basic_energy_to_bagon,
    attach_dce_to_iron_thorns,
    crispin_for_bagon,
    dragon_claw_ready,
    guzma_hala_search,
    play_thunder_mountain,
    tag_call_for_guzma_hala,
    volt_cyclone_ready,
)


@dataclass(frozen=True)
class TimedEnergyState:
    """One player-turn position backed by canonical ordinary quotas."""

    access: EnergyAccessState
    budget: TurnActionBudget
    own_turn: int
    went_first: bool
    first_turn_attack_exception: bool = False
    first_turn_supporter_exception: bool = False

    def __post_init__(self) -> None:
        if self.own_turn < 1:
            raise ValueError("own_turn must be positive")
        if self.budget.turn_ended:
            raise ValueError("a closed turn must be advanced before planning")
        # Legacy card-specific actions expose one-use booleans, so reject
        # exceptional multi-play budgets until those actions are upgraded.
        if (
            self.budget.supporter_play_limit != 1
            or self.budget.stadium_play_limit != 1
            or self.budget.manual_energy_attachment_limit != 1
        ):
            raise ValueError("legacy Energy transitions require ordinary action quotas")
        if (
            self.access.supporter_used != self.budget.supporter_used
            or self.access.stadium_used != self.budget.stadium_play_used
            or (
                self.access.manual_attachment_used
                != self.budget.manual_energy_attachment_used
            )
        ):
            raise ValueError("Energy flags and canonical budget disagree")


def initial_timed_state(
    access: EnergyAccessState,
    *,
    went_first: bool,
    own_turn: int = 1,
    first_turn_attack_exception: bool = False,
    first_turn_supporter_exception: bool = False,
) -> TimedEnergyState:
    """Promote existing one-use flags to one authoritative action budget."""
    return TimedEnergyState(
        access=access,
        budget=budget_from_flags(
            supporter_used=access.supporter_used,
            stadium_play_used=access.stadium_used,
            manual_energy_attachment_used=access.manual_attachment_used,
        ),
        own_turn=own_turn,
        went_first=went_first,
        first_turn_attack_exception=first_turn_attack_exception,
        first_turn_supporter_exception=first_turn_supporter_exception,
    )


def _opening_supporter_blocked(state: TimedEnergyState) -> bool:
    return (
        state.went_first and state.own_turn == 1
        and not state.first_turn_supporter_exception
    )


def _opening_attack_blocked(state: TimedEnergyState) -> bool:
    return (
        state.went_first and state.own_turn == 1
        and not state.first_turn_attack_exception
    )


def _sync(access: EnergyAccessState, budget: TurnActionBudget) -> EnergyAccessState:
    return replace(
        access,
        supporter_used=budget.supporter_used,
        stadium_used=budget.stadium_play_used,
        manual_attachment_used=budget.manual_energy_attachment_used,
    )


def advance_own_turn(state: TimedEnergyState) -> TimedEnergyState:
    """Refresh action quota with no modeled opponent board mutations."""
    budget = state.budget.next_turn()
    return replace(
        state,
        own_turn=state.own_turn + 1,
        budget=budget,
        access=_sync(state.access, budget),
    )


TimedAction = tuple[Action, TurnAction | None]
IRON_THORNS_TIMED_ACTIONS: tuple[TimedAction, ...] = (
    (tag_call_for_guzma_hala, None),
    (guzma_hala_search, TurnAction.SUPPORTER),
    (play_thunder_mountain, TurnAction.STADIUM_PLAY),
    (attach_dce_to_iron_thorns, TurnAction.MANUAL_ENERGY_ATTACHMENT),
)
CRISPIN_BAGON_TIMED_ACTIONS: tuple[TimedAction, ...] = (
    (crispin_for_bagon, TurnAction.SUPPORTER),
    (attach_basic_energy_to_bagon, TurnAction.MANUAL_ENERGY_ATTACHMENT),
)


def execute_timed_action(
    state: TimedEnergyState, action: Action, quota: TurnAction | None
) -> list[tuple[str, TimedEnergyState]]:
    """Execute a typed physical transition under its canonical action window."""
    if quota is TurnAction.SUPPORTER and _opening_supporter_blocked(state):
        return []
    if quota is not None and not state.budget.can(quota):
        return []
    budget = state.budget if quota is None else state.budget.consume(quota)
    assert budget is not None
    return [
        (label, replace(state, access=_sync(updated, budget), budget=budget))
        for label, updated in action(state.access)
    ]


def attack_ready(
    state: TimedEnergyState, goal: Callable[[EnergyAccessState], bool]
) -> bool:
    return (
        not _opening_attack_blocked(state)
        and state.budget.can(TurnAction.ATTACK)
        and goal(state.access)
    )


@dataclass(frozen=True)
class TimedSetupResult:
    actions: tuple[str, ...]
    final_state: TimedEnergyState

    @property
    def earliest_own_turn(self) -> int:
        return self.final_state.own_turn


def earliest_setup(
    initial: TimedEnergyState,
    *,
    actions: Sequence[TimedAction],
    physical_goal: Callable[[EnergyAccessState], bool],
    max_own_turns: int = 3,
    max_actions: int = 16,
) -> TimedSetupResult | None:
    """Minimize own-turn deadline before action count, not vice versa."""
    if max_own_turns < initial.own_turn or max_actions < 0:
        return None
    serial = count()
    queue: list[tuple[int, int, int, TimedEnergyState, tuple[str, ...]]] = []
    heappush(queue, (initial.own_turn, 0, next(serial), initial, ()))
    best = {initial: (initial.own_turn, 0)}
    while queue:
        turn, distance, _, state, line = heappop(queue)
        if best[state] != (turn, distance):
            continue
        if attack_ready(state, physical_goal):
            return TimedSetupResult(actions=line, final_state=state)
        if distance >= max_actions:
            continue
        successors = [
            transition
            for action, quota in actions
            for transition in execute_timed_action(state, action, quota)
        ]
        if state.own_turn < max_own_turns:
            successors.append(
                ("End own turn; opponent turn assumed inert", advance_own_turn(state))
            )
        for label, updated in successors:
            candidate = (updated.own_turn, distance + 1)
            if candidate >= best.get(updated, (max_own_turns + 1, max_actions + 1)):
                continue
            best[updated] = candidate
            heappush(
                queue,
                (candidate[0], candidate[1], next(serial), updated, line + (label,)),
            )
    return None


def earliest_volt_cyclone_setup(
    initial: TimedEnergyState, **kwargs: int
) -> TimedSetupResult | None:
    return earliest_setup(
        initial, actions=IRON_THORNS_TIMED_ACTIONS,
        physical_goal=volt_cyclone_ready, **kwargs
    )


def earliest_dragon_claw_setup(
    initial: TimedEnergyState, **kwargs: int
) -> TimedSetupResult | None:
    return earliest_setup(
        initial, actions=CRISPIN_BAGON_TIMED_ACTIONS,
        physical_goal=dragon_claw_ready, **kwargs
    )
