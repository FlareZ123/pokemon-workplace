"""Translate card-grounded literal spread targets into physical copy-body damage.

This is a conservative single-reaction-site-per-target bridge. It passes
multiple independently typed damage actions to the physical replay without
choosing targets, modifying boards, or resolving subsequent reactions.
"""
from __future__ import annotations

from typing import Mapping

from attack_copy_physical_ko_bridge import PhysicalBoardEventProgram
from attack_damage_target_geometry import LiteralDamageTargetPlan
from board_position_state import BoardState
from damage_calculation_kernel import AttackDamage, DamageContext
from pokemon_card_profile import PokemonCardProfile
from profile_damage_context import resolve_printed_type_stages
from stack_board_profile_binding import current_profile


def materialize_profiled_literal_damage_program(
    plan: LiteralDamageTargetPlan,
    board: BoardState,
    *,
    actor_profile: PokemonCardProfile,
    profiles: Mapping[str, PokemonCardProfile],
    current_print_id_by_pokemon_id: Mapping[str, str],
    attacker_types: tuple[str, ...] | None = None,
) -> PhysicalBoardEventProgram:
    """Construct one program with typed damage sites, preserving actor type.

    Multiple hits on the same target in one body event are not yet supported
    by target-specific reaction matching. That case fails explicitly.
    """
    if not plan.instructions:
        raise ValueError("no actual target damage to materialize")
    ids = tuple(instruction.target_id for instruction in plan.instructions)
    if len(set(ids)) != len(ids):
        raise ValueError("same copied body damages one target more than once")

    live_types = actor_profile.types if attacker_types is None else attacker_types
    if not live_types:
        raise ValueError("the executing attacker must have at least one type")

    typed: list[tuple[str, DamageContext]] = []
    for instruction in plan.instructions:
        board.get(instruction.target_id)
        target = current_profile(
            instruction.target_id,
            profiles,
            current_print_id_by_pokemon_id,
        )
        damage = AttackDamage(instruction.amount)
        if instruction.ignore_weakness_resistance:
            context = DamageContext(
                attack=damage,
                ignore_weakness_resistance=True,
            )
        else:
            stages = resolve_printed_type_stages(live_types, target)
            context = DamageContext(
                attack=damage,
                weakness_multiplier=stages.weakness_multiplier,
                weakness_addition=stages.weakness_addition,
                resistance_reduction=stages.resistance_reduction,
            )
        typed.append((instruction.target_id, context))

    first, *additional = typed
    return PhysicalBoardEventProgram(
        damage_target_id=first[0],
        damage_context=first[1],
        additional_damage=tuple(additional),
    )
