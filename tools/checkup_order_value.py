"""Small deterministic evaluator for damage-counter ordering during Checkup."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from special_condition_state import CHECKUP_CONDITION_BLOCK


class CounterEffectKind(str, Enum):
    PUT = "put"
    HEAL = "heal"


@dataclass(frozen=True)
class CounterEffect:
    effect_id: str
    kind: CounterEffectKind
    amount: int

    def __post_init__(self) -> None:
        if not self.effect_id:
            raise ValueError("effect_id must be non-empty")
        if self.amount < 0:
            raise ValueError("amount must be non-negative")


def apply_counter_effect(damage_counters: int, effect: CounterEffect) -> int:
    if damage_counters < 0:
        raise ValueError("damage_counters must be non-negative")
    if effect.kind == CounterEffectKind.PUT:
        return damage_counters + effect.amount
    if effect.kind == CounterEffectKind.HEAL:
        return max(0, damage_counters - effect.amount)
    raise ValueError(f"unsupported counter effect: {effect.kind!r}")


def resolve_counter_schedule(
    schedule: tuple[str, ...],
    *,
    initial_damage_counters: int,
    condition_block_damage_counters: int,
    effects: Mapping[str, CounterEffect],
) -> int:
    """Resolve one already-legal Checkup schedule for a single target.

    The condition block is summarized as a fixed counter addition. This helper
    studies ordering algebra only; eligibility, condition recovery, trigger
    creation, and Knock Out resolution remain upstream/downstream.
    """

    if initial_damage_counters < 0 or condition_block_damage_counters < 0:
        raise ValueError("counter amounts must be non-negative")
    if schedule.count(CHECKUP_CONDITION_BLOCK) != 1:
        raise ValueError("schedule must contain exactly one condition block")

    effect_tokens = tuple(
        token for token in schedule if token != CHECKUP_CONDITION_BLOCK
    )
    if len(effect_tokens) != len(set(effect_tokens)):
        raise ValueError("effect IDs cannot repeat in a schedule")
    if set(effect_tokens) != set(effects):
        raise ValueError("schedule effect IDs must match the supplied effects")

    damage = initial_damage_counters
    for token in schedule:
        if token == CHECKUP_CONDITION_BLOCK:
            damage += condition_block_damage_counters
        else:
            damage = apply_counter_effect(damage, effects[token])
    return damage


def schedule_outcomes(
    schedules: tuple[tuple[str, ...], ...],
    *,
    initial_damage_counters: int,
    condition_block_damage_counters: int,
    effects: Mapping[str, CounterEffect],
) -> tuple[tuple[tuple[str, ...], int], ...]:
    return tuple(
        (
            schedule,
            resolve_counter_schedule(
                schedule,
                initial_damage_counters=initial_damage_counters,
                condition_block_damage_counters=condition_block_damage_counters,
                effects=effects,
            ),
        )
        for schedule in schedules
    )
