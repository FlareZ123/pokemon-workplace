"""Supporter play-event provenance for Expanded simulations."""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from turn_action_budget import TurnAction, TurnActionBudget


class ExecutionClass(str, Enum):
    SUPPORTER_PLAY = "supporter_play"
    ATTACK_EFFECT = "attack_effect"


@dataclass(frozen=True)
class SupporterIdentity:
    copy_id: str
    name: str
    qualifiers: frozenset[str] = frozenset()


@dataclass(frozen=True)
class SupporterPlayEvent:
    copy_id: str
    name: str
    qualifiers: frozenset[str]


@dataclass(frozen=True)
class ExecutedSupporterBody:
    body_source_copy_id: str
    body_source_name: str
    execution_class: ExecutionClass
    outer_played_copy_id: str | None
    outer_played_name: str | None

    @property
    def triggers_supporter_from_hand_reactions(self) -> bool:
        return self.execution_class is ExecutionClass.SUPPORTER_PLAY


@dataclass(frozen=True)
class SupporterExecutionState:
    budget: TurnActionBudget = TurnActionBudget()
    play_events: tuple[SupporterPlayEvent, ...] = ()
    last_execution: ExecutedSupporterBody | None = None


def play_supporter_from_hand(
    state: SupporterExecutionState,
    played: SupporterIdentity,
    *,
    delegated_body_source: SupporterIdentity | None = None,
) -> SupporterExecutionState | None:
    budget = state.budget.consume(TurnAction.SUPPORTER)
    if budget is None:
        return None
    body = delegated_body_source or played
    event = SupporterPlayEvent(played.copy_id, played.name, played.qualifiers)
    execution = ExecutedSupporterBody(
        body.copy_id, body.name, ExecutionClass.SUPPORTER_PLAY, played.copy_id, played.name
    )
    return replace(
        state,
        budget=budget,
        play_events=state.play_events + (event,),
        last_execution=execution,
    )


def copy_supporter_effect_as_attack(
    state: SupporterExecutionState,
    body: SupporterIdentity,
) -> SupporterExecutionState | None:
    budget = state.budget.consume(TurnAction.ATTACK)
    if budget is None:
        return None
    execution = ExecutedSupporterBody(
        body.copy_id, body.name, ExecutionClass.ATTACK_EFFECT, None, None
    )
    return replace(state, budget=budget, last_execution=execution)


def played_supporter_from_hand(
    state: SupporterExecutionState,
    *,
    qualifier: str | None = None,
    name_contains: str | None = None,
) -> bool:
    for event in state.play_events:
        if qualifier is not None and qualifier not in event.qualifiers:
            continue
        if name_contains is not None and name_contains not in event.name:
            continue
        return True
    return False
