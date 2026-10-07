"""Typed Special Condition payload and Pokemon Checkup ordering helpers.

This module is intentionally conservative. It models rulebook-backed distinctions
that a simulator must preserve without attempting to implement every basic-rule
coin flip or recovery rule for Special Conditions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import permutations
from math import factorial
from typing import Iterable


class ConditionKind(str, Enum):
    POISONED = "Poisoned"
    BURNED = "Burned"
    ASLEEP = "Asleep"
    PARALYZED = "Paralyzed"
    CONFUSED = "Confused"


CHECKUP_ORDER = (
    ConditionKind.POISONED,
    ConditionKind.BURNED,
    ConditionKind.ASLEEP,
    ConditionKind.PARALYZED,
)
CHECKUP_CONDITION_BLOCK = "__special_condition_block__"

DEFAULT_DAMAGE_COUNTERS = {
    ConditionKind.POISONED: 1,
    ConditionKind.BURNED: 2,
    ConditionKind.CONFUSED: 3,
}


class ModifierMode(str, Enum):
    REPLACE_BASE = "replace_base"
    ADD = "add"


@dataclass(frozen=True)
class ConditionInstance:
    kind: ConditionKind
    base_damage_counters: int | None = None
    source_label: str | None = None

    def __post_init__(self) -> None:
        if self.base_damage_counters is not None and self.base_damage_counters < 0:
            raise ValueError("base_damage_counters must be non-negative")
        if self.kind not in DEFAULT_DAMAGE_COUNTERS and self.base_damage_counters is not None:
            raise ValueError(
                f"{self.kind.value} has no modeled damage-counter payload"
            )


@dataclass(frozen=True)
class SpecialConditionState:
    conditions: tuple[ConditionInstance, ...] = ()

    def __post_init__(self) -> None:
        kinds = [condition.kind for condition in self.conditions]
        if len(kinds) != len(set(kinds)):
            raise ValueError("each Special Condition kind may appear at most once")

    def get(self, kind: ConditionKind) -> ConditionInstance | None:
        for condition in self.conditions:
            if condition.kind == kind:
                return condition
        return None


@dataclass(frozen=True)
class ConditionModifier:
    kind: ConditionKind
    amount: int
    mode: ModifierMode
    source_label: str | None = None

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("modifier amount must be non-negative")
        if self.kind not in DEFAULT_DAMAGE_COUNTERS:
            raise ValueError(
                f"{self.kind.value} has no modeled damage-counter amount"
            )


def regular_condition(kind: ConditionKind, *, source_label: str | None = None) -> ConditionInstance:
    """Construct the ordinary version of one condition.

    The advanced manual exposes ordinary counter bases through its `instead of`
    examples: Poisoned 1, Burned 2, and Confused 3. Non-damaging conditions
    carry no numeric payload in this kernel.
    """

    return ConditionInstance(
        kind=kind,
        base_damage_counters=DEFAULT_DAMAGE_COUNTERS.get(kind),
        source_label=source_label,
    )


def apply_condition(
    state: SpecialConditionState,
    condition: ConditionInstance,
) -> SpecialConditionState:
    """Apply a condition, replacing an older instance of the same kind.

    This captures the manual's explicit rule that a newer regular/irregular
    version of a Special Condition replaces the previous version of that same
    condition. Cross-kind exclusivity belongs to the basic-rules layer and is
    deliberately outside this evidence-bounded helper.
    """

    kept = tuple(row for row in state.conditions if row.kind != condition.kind)
    ordered = tuple(sorted(kept + (condition,), key=lambda row: row.kind.value))
    return SpecialConditionState(ordered)


def clear_conditions(state: SpecialConditionState) -> SpecialConditionState:
    return SpecialConditionState()


def legacy_name_projection(state: SpecialConditionState) -> frozenset[str]:
    """Project to the old board kernel's lossy set-of-names representation."""

    return frozenset(condition.kind.value for condition in state.conditions)


def effective_damage_counters(
    state: SpecialConditionState,
    kind: ConditionKind,
    modifiers: Iterable[ConditionModifier] = (),
) -> int | None:
    """Return the counter amount for one currently present damaging condition.

    Base-replacement effects use the highest active replacement exactly once;
    additive effects then sum on top. A condition-local irregular payload is
    itself a base candidate, so a stronger active replacement can supersede it.
    """

    condition = state.get(kind)
    if condition is None or kind not in DEFAULT_DAMAGE_COUNTERS:
        return None

    assert condition.base_damage_counters is not None
    replacements = [condition.base_damage_counters]
    additions = 0

    for modifier in modifiers:
        if modifier.kind != kind:
            continue
        if modifier.mode == ModifierMode.REPLACE_BASE:
            replacements.append(modifier.amount)
        elif modifier.mode == ModifierMode.ADD:
            additions += modifier.amount
        else:
            raise ValueError(f"unsupported modifier mode: {modifier.mode!r}")

    return max(replacements) + additions


def checkup_conditions(state: SpecialConditionState) -> tuple[ConditionKind, ...]:
    """Return present Special Conditions in the manual's Checkup order."""

    present = {condition.kind for condition in state.conditions}
    return tuple(kind for kind in CHECKUP_ORDER if kind in present)


def enumerate_checkup_schedules(effect_ids: Iterable[str]) -> tuple[tuple[str, ...], ...]:
    """Enumerate rulebook-permitted placements of Checkup effects.

    The whole Special Condition sequence is treated as one atomic block relative
    to Trainer/Ability effects. For n distinct effects this produces (n+1)!
    abstract schedules before semantic pruning.
    """

    effects = tuple(effect_ids)
    if any(not effect_id for effect_id in effects):
        raise ValueError("effect IDs must be non-empty")
    if len(effects) != len(set(effects)):
        raise ValueError("effect IDs must be unique")

    schedules: list[tuple[str, ...]] = []
    for ordered_effects in permutations(effects):
        for block_index in range(len(effects) + 1):
            schedule = (
                ordered_effects[:block_index]
                + (CHECKUP_CONDITION_BLOCK,)
                + ordered_effects[block_index:]
            )
            schedules.append(schedule)
    return tuple(schedules)


def expected_schedule_count(effect_count: int) -> int:
    if effect_count < 0:
        raise ValueError("effect_count must be non-negative")
    return factorial(effect_count + 1)


def expand_checkup_schedule(
    schedule: tuple[str, ...],
    state: SpecialConditionState,
) -> tuple[str, ...]:
    """Expand the atomic condition block into its fixed internal order."""

    if schedule.count(CHECKUP_CONDITION_BLOCK) != 1:
        raise ValueError("schedule must contain exactly one condition block")

    expanded: list[str] = []
    for token in schedule:
        if token != CHECKUP_CONDITION_BLOCK:
            expanded.append(token)
            continue
        expanded.extend(f"condition:{kind.value}" for kind in checkup_conditions(state))
    return tuple(expanded)
