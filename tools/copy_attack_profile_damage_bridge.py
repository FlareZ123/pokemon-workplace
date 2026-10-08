"""Apply card-profile type stages to compiled copied-attack damage.

A copied attack supplies an attack body. The Pokemon using the declared attack
remains the attacking Pokemon, so Weakness and Resistance must use that
Pokemon's current type rather than the copied source card's printed type.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Mapping

from attack_copy_physical_ko_bridge import PhysicalBoardEventProgram
from board_position_state import BoardState
from damage_calculation_kernel import AttackDamage, DamageContext
from pokemon_card_profile import PokemonCardProfile
from stack_board_profile_binding import current_profile, hp_by_stack_board
from profile_damage_context import resolve_printed_type_stages
from simple_attack_board_semantics import (
    CompiledAttackBoardSemantics,
    materialize_opponent_board_program,
)


def materialize_profiled_copy_program(
    semantics: CompiledAttackBoardSemantics,
    board: BoardState,
    *,
    actor_profile: PokemonCardProfile,
    profiles: Mapping[str, PokemonCardProfile],
    current_print_id_by_pokemon_id: Mapping[str, str],
    counter_allocation: Iterable[tuple[str, int]] = (),
    attacker_types: tuple[str, ...] | None = None,
    weakness_enabled: bool = True,
    resistance_enabled: bool = True,
    ignore_weakness_resistance: bool | None = None,
    ignore_defender_effects: bool | None = None,
) -> PhysicalBoardEventProgram:
    """Compile opponent-facing board effects with printed type stages.

    actor_profile is the Pokemon actually using the copied attack.
    semantics may come from a different source Pokemon entirely.
    """

    base = materialize_opponent_board_program(
        semantics,
        board,
        counter_allocation=counter_allocation,
    )
    target = current_profile(
        board.active_id,
        profiles,
        current_print_id_by_pokemon_id,
    )

    live_attacker_types = (
        actor_profile.types
        if attacker_types is None
        else attacker_types
    )
    if not live_attacker_types:
        raise ValueError("attacking Pokemon must have at least one current type")

    ignore_weakness = (
        semantics.ignore_weakness
        if ignore_weakness_resistance is None
        else ignore_weakness_resistance
    )
    ignore_resistance = (
        semantics.ignore_resistance
        if ignore_weakness_resistance is None
        else ignore_weakness_resistance
    )
    ignore_wr = ignore_weakness and ignore_resistance
    ignore_effects = (
        semantics.ignore_defender_effects
        if ignore_defender_effects is None
        else ignore_defender_effects
    )

    if ignore_wr:
        context = DamageContext(
            attack=AttackDamage(semantics.fixed_damage or 0),
            ignore_weakness_resistance=True,
            ignore_defender_effects=ignore_effects,
        )
    else:
        stages = resolve_printed_type_stages(
            live_attacker_types,
            target,
            weakness_enabled=weakness_enabled and not ignore_weakness,
            resistance_enabled=resistance_enabled and not ignore_resistance,
        )
        context = DamageContext(
            attack=AttackDamage(semantics.fixed_damage or 0),
            weakness_multiplier=stages.weakness_multiplier,
            weakness_addition=stages.weakness_addition,
            resistance_reduction=stages.resistance_reduction,
            ignore_defender_effects=ignore_effects,
        )

    return replace(base, damage_context=context)
