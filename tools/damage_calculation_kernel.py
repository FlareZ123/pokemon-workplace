"""Exact damage-calculation order for a conservative Pokemon TCG subset.

This module models the six damage-calculation steps from the Advanced Player's
Rulebook. Attack-resolution effects outside damage remain upstream/downstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class AttackDamageMode(str, Enum):
    FIXED = "fixed"
    PLUS = "plus"
    MINUS = "minus"
    TIMES = "times"


@dataclass(frozen=True)
class AttackDamage:
    """Printed attack damage plus the step-1 attack-text adjustment.

    `base` is the number printed next to the attack. For PLUS and MINUS,
    `modifier` is the amount added/subtracted by attack text. For TIMES,
    `modifier` is the counted multiplier. FIXED ignores `modifier`.
    """

    base: int
    mode: AttackDamageMode = AttackDamageMode.FIXED
    modifier: int = 0

    def __post_init__(self) -> None:
        if self.base < 0:
            raise ValueError("printed attack damage must be non-negative")
        if self.mode is AttackDamageMode.TIMES and self.modifier < 0:
            raise ValueError("damage multiplier count must be non-negative")

    def resolve(self) -> int:
        if self.mode is AttackDamageMode.FIXED:
            return self.base
        if self.mode is AttackDamageMode.PLUS:
            return self.base + self.modifier
        if self.mode is AttackDamageMode.MINUS:
            return self.base - self.modifier
        if self.mode is AttackDamageMode.TIMES:
            return self.base * self.modifier
        raise AssertionError(f"unhandled damage mode: {self.mode}")


@dataclass(frozen=True)
class DamageContext:
    attack: AttackDamage
    attacker_effect_modifiers: tuple[int, ...] = ()
    weakness_multiplier: int | None = None
    resistance_reduction: int = 0
    defender_effect_modifiers: tuple[int, ...] = ()
    prevent_all_damage: bool = False
    ignore_weakness_resistance: bool = False
    ignore_defender_effects: bool = False

    def __post_init__(self) -> None:
        if self.weakness_multiplier is not None and self.weakness_multiplier < 1:
            raise ValueError("Weakness multiplier must be at least 1")
        if self.resistance_reduction < 0:
            raise ValueError("Resistance reduction must be non-negative")


@dataclass(frozen=True)
class DamageResult:
    step1_attack_damage: int
    step2_attacker_effects: int | None
    step3_weakness: int | None
    step4_resistance: int | None
    step5_defender_effects: int | None
    final_damage: int
    stopped_after_step: int | None = None
    prevention_applied: bool = False


def _sum_modifiers(value: int, modifiers: Iterable[int]) -> int:
    return value + sum(modifiers)


def calculate_damage(context: DamageContext) -> DamageResult:
    """Resolve attack damage in rulebook order.

    Non-positive results at the rulebook stop points become zero final damage.
    `ignore_defender_effects` skips step 5 and final damage prevention, matching
    B-07. Weakness/Resistance existence is supplied as current state and is not
    reconstructed when defender effects are ignored.
    """

    step1 = context.attack.resolve()
    if (
        context.attack.mode in {AttackDamageMode.MINUS, AttackDamageMode.TIMES}
        and step1 <= 0
    ):
        return DamageResult(step1, None, None, None, None, 0, stopped_after_step=1)

    step2 = _sum_modifiers(step1, context.attacker_effect_modifiers)
    if step2 <= 0:
        return DamageResult(step1, step2, None, None, None, 0, stopped_after_step=2)

    if context.ignore_weakness_resistance:
        step3 = step2
        step4 = step2
    else:
        step3 = (
            step2 * context.weakness_multiplier
            if context.weakness_multiplier is not None
            else step2
        )
        step4 = step3 - context.resistance_reduction
        if step4 <= 0:
            return DamageResult(
                step1,
                step2,
                step3,
                step4,
                None,
                0,
                stopped_after_step=4,
            )

    if context.ignore_defender_effects:
        step5 = step4
    else:
        step5 = _sum_modifiers(step4, context.defender_effect_modifiers)
        if step5 <= 0:
            return DamageResult(
                step1,
                step2,
                step3,
                step4,
                step5,
                0,
                stopped_after_step=5,
            )

    prevention_applied = (
        context.prevent_all_damage and not context.ignore_defender_effects
    )
    final = 0 if prevention_applied else step5
    return DamageResult(
        step1,
        step2,
        step3,
        step4,
        step5,
        final,
        stopped_after_step=6 if prevention_applied else None,
        prevention_applied=prevention_applied,
    )
