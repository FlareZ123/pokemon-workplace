"""Step-6 reactions that trigger after a Pokemon is damaged by an attack."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from board_object_kernel import BoardState
from damage_board_bridge import (
    EffectCounterPlacement,
    apply_effect_counter_placement,
    knocked_out_ids,
)
from damage_calculation_kernel import DamageResult


class DamageReactionKind(str, Enum):
    FIXED_COUNTERS = "fixed_counters"
    MIRROR_FINAL_DAMAGE = "mirror_final_damage"


@dataclass(frozen=True)
class DamageReaction:
    kind: DamageReactionKind
    fixed_counters: int = 0

    def __post_init__(self) -> None:
        if self.fixed_counters < 0:
            raise ValueError("fixed_counters must be non-negative")


@dataclass(frozen=True)
class DamageReactionResult:
    attacker_board: BoardState
    defender_board: BoardState
    attacker_knocked_out_ids: tuple[str, ...]
    defender_knocked_out_ids: tuple[str, ...]
    counters_placed_on_attacker: int
    triggered: bool


def resolve_damage_reactions(
    attacker_board: BoardState,
    defender_board: BoardState,
    damage_result: DamageResult,
    *,
    reactions: tuple[DamageReaction, ...],
    attacker_hp_by_object_id: dict[str, int],
    defender_hp_by_object_id: dict[str, int],
) -> DamageReactionResult:
    """Apply ordered reactions, then expose both sides' KO candidates."""

    current_attacker = attacker_board
    placed = 0
    triggered = damage_result.final_damage > 0

    if triggered:
        for reaction in reactions:
            if reaction.kind is DamageReactionKind.FIXED_COUNTERS:
                count = reaction.fixed_counters
            elif reaction.kind is DamageReactionKind.MIRROR_FINAL_DAMAGE:
                if damage_result.final_damage % 10 != 0:
                    raise ValueError("mirrored damage must convert to damage counters")
                count = damage_result.final_damage // 10
            else:
                raise AssertionError(reaction.kind)

            current_attacker, outcome = apply_effect_counter_placement(
                current_attacker,
                EffectCounterPlacement(
                    current_attacker.active_id,
                    count,
                ),
            )
            placed += outcome.placed

    return DamageReactionResult(
        attacker_board=current_attacker,
        defender_board=defender_board,
        attacker_knocked_out_ids=knocked_out_ids(
            current_attacker,
            attacker_hp_by_object_id,
        ),
        defender_knocked_out_ids=knocked_out_ids(
            defender_board,
            defender_hp_by_object_id,
        ),
        counters_placed_on_attacker=placed,
        triggered=triggered,
    )
