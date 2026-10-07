"""Translate printed Pokemon type modifiers into ordered damage inputs."""

from __future__ import annotations

from dataclasses import dataclass

from pokemon_card_profile import PokemonCardProfile, TypedModifier
from type_modifier_catalog import TypeModifierKind


@dataclass(frozen=True)
class ResolvedTypeStages:
    weakness_multiplier: int | None = None
    weakness_addition: int = 0
    resistance_reduction: int = 0
    matched_weakness: TypedModifier | None = None
    matched_resistance: TypedModifier | None = None


def _matching(rows, attacker_types: tuple[str, ...]):
    types = set(attacker_types)
    return tuple(row for row in rows if row.energy_type in types)


def resolve_printed_type_stages(
    attacker_types: tuple[str, ...],
    target: PokemonCardProfile,
    *,
    weakness_enabled: bool = True,
    resistance_enabled: bool = True,
) -> ResolvedTypeStages:
    weakness_matches = _matching(target.weaknesses, attacker_types) if weakness_enabled else ()
    resistance_matches = _matching(target.resistances, attacker_types) if resistance_enabled else ()
    if len(weakness_matches) > 1:
        raise ValueError("multiple matching Weakness modifiers are unsupported")
    if len(resistance_matches) > 1:
        raise ValueError("multiple matching Resistance modifiers are unsupported")

    weakness_multiplier = None
    weakness_addition = 0
    matched_weakness = weakness_matches[0] if weakness_matches else None
    if matched_weakness is not None:
        modifier = matched_weakness.modifier
        if modifier.kind is TypeModifierKind.MULTIPLY:
            weakness_multiplier = modifier.amount
        elif modifier.kind is TypeModifierKind.ADD:
            weakness_addition = modifier.amount
        else:
            raise ValueError("subtractive Weakness is unsupported")

    resistance_reduction = 0
    matched_resistance = resistance_matches[0] if resistance_matches else None
    if matched_resistance is not None:
        modifier = matched_resistance.modifier
        if modifier.kind is TypeModifierKind.SUBTRACT:
            resistance_reduction = modifier.amount
        else:
            raise ValueError("non-subtractive Resistance is unsupported")

    return ResolvedTypeStages(
        weakness_multiplier=weakness_multiplier,
        weakness_addition=weakness_addition,
        resistance_reduction=resistance_reduction,
        matched_weakness=matched_weakness,
        matched_resistance=matched_resistance,
    )
