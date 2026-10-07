"""Bridge ordered attack damage into board-object HP and KO candidates.

Damage and effect-placed damage counters remain distinct transitions until the
attack's Knock Out check. This matters for Weakness/Resistance, prevention, and
effect immunity.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping

from board_object_kernel import BoardPokemon, BoardState
from damage_calculation_kernel import DamageContext, DamageResult, calculate_damage


@dataclass(frozen=True)
class EffectCounterPlacement:
    target_id: str
    count: int
    prevent_effects_of_attacks: bool = False

    def __post_init__(self) -> None:
        if not self.target_id:
            raise ValueError("target_id must be non-empty")
        if self.count < 0:
            raise ValueError("damage-counter count must be non-negative")


@dataclass(frozen=True)
class CounterPlacementOutcome:
    target_id: str
    requested: int
    placed: int


@dataclass(frozen=True)
class AttackDamagePhaseResult:
    board: BoardState
    damage_result: DamageResult
    counter_outcomes: tuple[CounterPlacementOutcome, ...]
    knocked_out_ids: tuple[str, ...]


def _replace_object(board: BoardState, pokemon: BoardPokemon) -> BoardState:
    next_board = replace(
        board,
        objects=tuple(
            pokemon if row.object_id == pokemon.object_id else row
            for row in board.objects
        ),
    )
    next_board.validate()
    return next_board


def _add_damage_counters(
    board: BoardState,
    target_id: str,
    count: int,
) -> BoardState:
    target = board.get(target_id)
    return _replace_object(
        board,
        replace(target, damage_counters=target.damage_counters + count),
    )


def apply_attack_damage(
    board: BoardState,
    target_id: str,
    context: DamageContext,
) -> tuple[BoardState, DamageResult]:
    """Calculate damage and place equivalent 10-damage counters on the target."""

    board.get(target_id)
    result = calculate_damage(context)
    if result.final_damage % 10 != 0:
        raise ValueError("board damage must be representable in 10-damage counters")
    if result.final_damage == 0:
        return board, result
    return (
        _add_damage_counters(board, target_id, result.final_damage // 10),
        result,
    )


def apply_effect_counter_placement(
    board: BoardState,
    placement: EffectCounterPlacement,
) -> tuple[BoardState, CounterPlacementOutcome]:
    """Apply attack-effect damage counters without damage arithmetic.

    A target immune to effects of attacks may still be selected, but zero
    counters are placed.
    """

    board.get(placement.target_id)
    placed = 0 if placement.prevent_effects_of_attacks else placement.count
    next_board = (
        board
        if placed == 0
        else _add_damage_counters(board, placement.target_id, placed)
    )
    return (
        next_board,
        CounterPlacementOutcome(placement.target_id, placement.count, placed),
    )


def knocked_out_ids(
    board: BoardState,
    hp_by_object_id: Mapping[str, int],
) -> tuple[str, ...]:
    """Return in-play objects whose damage counters meet or exceed HP."""

    result: list[str] = []
    for pokemon in board.objects:
        if pokemon.object_id not in hp_by_object_id:
            raise ValueError(f"missing HP for {pokemon.object_id!r}")
        hp = hp_by_object_id[pokemon.object_id]
        if hp <= 0 or hp % 10 != 0:
            raise ValueError("Pokemon HP must be a positive multiple of 10")
        if pokemon.damage_counters * 10 >= hp:
            result.append(pokemon.object_id)
    return tuple(result)


def resolve_attack_damage_phase(
    board: BoardState,
    *,
    damage_target_id: str,
    damage_context: DamageContext,
    counter_placements: tuple[EffectCounterPlacement, ...] = (),
    hp_by_object_id: Mapping[str, int],
) -> AttackDamagePhaseResult:
    """Resolve damage, effect counters, then perform the shared KO check.

    This intentionally delays KO detection until after all modeled attack
    effects, matching attack-resolution step 7.
    """

    current, damage_result = apply_attack_damage(
        board, damage_target_id, damage_context
    )
    outcomes: list[CounterPlacementOutcome] = []
    for placement in counter_placements:
        current, outcome = apply_effect_counter_placement(current, placement)
        outcomes.append(outcome)

    return AttackDamagePhaseResult(
        board=current,
        damage_result=damage_result,
        counter_outcomes=tuple(outcomes),
        knocked_out_ids=knocked_out_ids(current, hp_by_object_id),
    )
