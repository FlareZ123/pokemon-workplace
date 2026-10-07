"""Turn-aged Special Condition state and deterministic Checkup resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from special_condition_state import (
    ConditionInstance,
    ConditionKind,
    ConditionModifier,
    ROTATION_CONDITIONS,
    SpecialConditionState,
    effective_damage_counters,
)


@dataclass(frozen=True)
class TimedCondition:
    condition: ConditionInstance
    applied_turn_serial: int

    def __post_init__(self) -> None:
        if self.applied_turn_serial < 0:
            raise ValueError("applied_turn_serial must be non-negative")


@dataclass(frozen=True)
class TimedConditionState:
    owner: str
    conditions: tuple[TimedCondition, ...] = ()

    def __post_init__(self) -> None:
        if not self.owner:
            raise ValueError("owner must be non-empty")
        typed = SpecialConditionState(
            tuple(row.condition for row in self.conditions)
        )
        if len(typed.conditions) != len(self.conditions):
            raise ValueError("timed condition state is inconsistent")

    def get(self, kind: ConditionKind) -> TimedCondition | None:
        for row in self.conditions:
            if row.condition.kind == kind:
                return row
        return None

    def untimed(self) -> SpecialConditionState:
        return SpecialConditionState(
            tuple(row.condition for row in self.conditions)
        )


@dataclass(frozen=True)
class BasicCheckupOutcome:
    next_state: TimedConditionState
    damage_counter_events: tuple[tuple[ConditionKind, int], ...]

    @property
    def total_damage_counters(self) -> int:
        return sum(amount for _, amount in self.damage_counter_events)


def apply_timed_condition(
    state: TimedConditionState,
    condition: ConditionInstance,
    *,
    applied_turn_serial: int,
) -> TimedConditionState:
    kept = tuple(
        row
        for row in state.conditions
        if row.condition.kind != condition.kind
        and not (
            condition.kind in ROTATION_CONDITIONS
            and row.condition.kind in ROTATION_CONDITIONS
        )
    )
    rows = kept + (TimedCondition(condition, applied_turn_serial),)
    rows = tuple(sorted(rows, key=lambda row: row.condition.kind.value))
    return TimedConditionState(state.owner, rows)


def _remove_kind(
    state: TimedConditionState,
    kind: ConditionKind,
) -> TimedConditionState:
    return TimedConditionState(
        state.owner,
        tuple(
            row for row in state.conditions
            if row.condition.kind != kind
        ),
    )


def resolve_basic_checkup(
    state: TimedConditionState,
    *,
    completed_turn_player: str,
    completed_turn_serial: int,
    burn_coin_heads: bool | None = None,
    asleep_coin_heads: bool | None = None,
    modifiers: Iterable[ConditionModifier] = (),
) -> BasicCheckupOutcome:
    """Resolve base Special Condition work for one Pokémon.

    Coin results are explicit inputs so randomness and coin-modifying cards stay
    outside this deterministic kernel. Paralysis recovery uses turn age: the
    owner must have completed a turn with serial greater than the turn in which
    the current Paralyzed instance was applied.
    """

    if not completed_turn_player:
        raise ValueError("completed_turn_player must be non-empty")
    if completed_turn_serial < 0:
        raise ValueError("completed_turn_serial must be non-negative")

    untimed = state.untimed()
    events: list[tuple[ConditionKind, int]] = []
    next_state = state

    poison = state.get(ConditionKind.POISONED)
    if poison is not None:
        amount = effective_damage_counters(
            untimed,
            ConditionKind.POISONED,
            modifiers,
        )
        assert amount is not None
        events.append((ConditionKind.POISONED, amount))

    burned = state.get(ConditionKind.BURNED)
    if burned is not None:
        amount = effective_damage_counters(
            untimed,
            ConditionKind.BURNED,
            modifiers,
        )
        assert amount is not None
        events.append((ConditionKind.BURNED, amount))
        if burn_coin_heads is None:
            raise ValueError(
                "burn_coin_heads is required for a Burned Pokémon"
            )
        if burn_coin_heads:
            next_state = _remove_kind(
                next_state,
                ConditionKind.BURNED,
            )

    asleep = state.get(ConditionKind.ASLEEP)
    if asleep is not None:
        if asleep_coin_heads is None:
            raise ValueError(
                "asleep_coin_heads is required for an Asleep Pokémon"
            )
        if asleep_coin_heads:
            next_state = _remove_kind(
                next_state,
                ConditionKind.ASLEEP,
            )

    paralyzed = state.get(ConditionKind.PARALYZED)
    if (
        paralyzed is not None
        and completed_turn_player == state.owner
        and completed_turn_serial > paralyzed.applied_turn_serial
    ):
        next_state = _remove_kind(
            next_state,
            ConditionKind.PARALYZED,
        )

    return BasicCheckupOutcome(next_state, tuple(events))
