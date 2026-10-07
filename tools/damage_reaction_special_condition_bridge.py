"""Compose post-damage reaction timing with typed Special Condition state."""

from __future__ import annotations

from dataclasses import dataclass

from damage_calculation_kernel import DamageResult
from special_condition_state import (
    ConditionKind,
    SpecialConditionState,
    apply_condition,
    regular_condition,
)


@dataclass(frozen=True)
class DamageTriggeredConditionResult:
    state: SpecialConditionState
    triggered: bool


def apply_damage_triggered_condition(
    state: SpecialConditionState,
    damage_result: DamageResult,
    condition: ConditionKind,
    *,
    source_label: str | None = None,
) -> DamageTriggeredConditionResult:
    """Apply a regular condition only when the attack dealt positive damage."""

    if damage_result.final_damage <= 0:
        return DamageTriggeredConditionResult(state, False)

    next_state = apply_condition(
        state,
        regular_condition(condition, source_label=source_label),
    )
    return DamageTriggeredConditionResult(next_state, True)
