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
from profile_damage_context import resolve_printed_type_stages
from simple_attack_board_semantics import (
    CompiledAttackBoardSemantics,
    materialize_opponent_board_program,
)


def current_profile(
    pokemon_id: str,
    profiles: Mapping[str, PokemonCardProfile],
    current_print_id_by_pokemon_id: Mapping[str, str],
) -> PokemonCardProfile:
    """Resolve a board object through an explicit current-print binding.

    The stack's PokemonCard.card_id is a physical instance ID, not a database
    print ID. Keeping the binding separate preserves those two identities.
    """

    try:
        print_id = current_print_id_by_pokemon_id[pokemon_id]
    except KeyError as exc:
        raise ValueError(
            f"no current print binding for Pokemon {pokemon_id!r}"
        ) from exc
    profile = profiles.get(print_id)
    if profile is None:
        raise ValueError(f"no legal Pokemon profile for {print_id!r}")
    return profile


def hp_by_stack_board(
    board: BoardState,
    profiles: Mapping[str, PokemonCardProfile],
    current_print_id_by_pokemon_id: Mapping[str, str],
) -> dict[str, int]:
    if set(current_print_id_by_pokemon_id) != {
        pokemon.pokemon_id for pokemon in board.pokemon
    }:
        raise ValueError("current print bindings must match the board exactly")
    return {
        pokemon.pokemon_id: current_profile(
            pokemon.pokemon_id,
            profiles,
            current_print_id_by_pokemon_id,
        ).hp
        for pokemon in board.pokemon
    }


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

    ignore_wr = (
        semantics.ignore_weakness_resistance
        if ignore_weakness_resistance is None
        else ignore_weakness_resistance
    )
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
            weakness_enabled=weakness_enabled,
            resistance_enabled=resistance_enabled,
        )
        context = DamageContext(
            attack=AttackDamage(semantics.fixed_damage or 0),
            weakness_multiplier=stages.weakness_multiplier,
            weakness_addition=stages.weakness_addition,
            resistance_reduction=stages.resistance_reduction,
            ignore_defender_effects=ignore_effects,
        )

    return replace(base, damage_context=context)
