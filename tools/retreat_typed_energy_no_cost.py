"""Exact-print Energy-type-gated no-Retreat-Cost Abilities.

The source registry is complete for the 27 self/aura English Expanded-labeled
Ability prints whose no-Retreat-Cost condition names a specific Energy type.
The provider predicate supports typed physical unit snapshots and a deliberately
small, exact-print set of Special Energy providers requiring context.
Unknown Special Energy behavior is outside this semantic island.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from board_object_kernel import BoardPokemon, BoardState, EnergyAttachment
from retreat_cost_semantics import RetreatCostModifier
from retreat_dynamic_energy_units import (
    COUNTER_ENERGY_PRINT_IDS,
    REVERSAL_ENERGY_PRINT_IDS,
    RetreatEnergyProviderContext,
    holder_has_rule_box,
    holder_is_evolution,
    holder_is_pokemon_ex,
    holder_is_pokemon_gx,
)

Scope = Literal["self", "team"]


@dataclass(frozen=True)
class TypedNoCostSource:
    print_id: str
    card_name: str
    ability_name: str
    energy_type: str
    scope: Scope


SOURCES = (
    TypedNoCostSource("bw11-RC3", "Serperior", "Royal Garden", "G", "self"),
    TypedNoCostSource("sm11-148", "Dratini", "Aqua Lift", "W", "self"),
    TypedNoCostSource("sm5-97", "Gible", "Rock Hiding", "F", "self"),
    TypedNoCostSource("sm6-21", "Froakie", "Frubbles", "W", "self"),
    TypedNoCostSource("sm7-37", "Lombre", "Aqua Lift", "W", "self"),
    TypedNoCostSource("sma-SV11", "Froakie", "Frubbles", "W", "self"),
    TypedNoCostSource("sv3pt5-144", "Articuno", "Ice Float", "W", "self"),
    TypedNoCostSource("sv3pt5-145", "Zapdos ex", "Voltaic Float", "L", "self"),
    TypedNoCostSource("sv3pt5-146", "Moltres", "Flare Float", "R", "self"),
    TypedNoCostSource("sv3pt5-192", "Zapdos ex", "Voltaic Float", "L", "self"),
    TypedNoCostSource("sv3pt5-202", "Zapdos ex", "Voltaic Float", "L", "self"),
    TypedNoCostSource("svp-49", "Zapdos ex", "Voltaic Float", "L", "self"),
    TypedNoCostSource("svp-139", "Latias", "Mist Float", "P", "self"),
    TypedNoCostSource("swsh12pt5-21", "Entei", "Explosive Heat Dash", "R", "self"),
    TypedNoCostSource("bw11-88", "Darkrai-EX", "Dark Cloak", "D", "team"),
    TypedNoCostSource("bw5-63", "Darkrai-EX", "Dark Cloak", "D", "team"),
    TypedNoCostSource("bw5-107", "Darkrai-EX", "Dark Cloak", "D", "team"),
    TypedNoCostSource("bwp-BW46", "Darkrai-EX", "Dark Cloak", "D", "team"),
    TypedNoCostSource("sm8-86", "Zeraora-GX", "Thunderclap Zone", "L", "team"),
    TypedNoCostSource("sm8-201", "Zeraora-GX", "Thunderclap Zone", "L", "team"),
    TypedNoCostSource("sm8-221", "Zeraora-GX", "Thunderclap Zone", "L", "team"),
    TypedNoCostSource("sv3-82", "Clefable ex", "Lunar Zone", "P", "team"),
    TypedNoCostSource("sv7-107", "Archaludon", "Metal Bridge", "M", "team"),
    TypedNoCostSource("sv7-155", "Archaludon", "Metal Bridge", "M", "team"),
    TypedNoCostSource("sv8pt5-70", "Archaludon", "Metal Bridge", "M", "team"),
    TypedNoCostSource("xy9-32", "Manaphy-EX", "Aqua Tube", "W", "team"),
    TypedNoCostSource("xy9-116", "Manaphy-EX", "Aqua Tube", "W", "team"),
)

_BY_PRINT = {source.print_id: source for source in SOURCES}
_RAINBOW_ENERGY = frozenset({
    "sm1-137", "sm7-151", "sm7-183", "xy1-131", "xy8-152",
})
_PRISM_ENERGY = frozenset({"bw4-93", "me2pt5-216", "zsv10pt5-86"})
_ALL_TYPES = frozenset({
    ("swsh1-186", "Aurora Energy"),
    ("sv6-167", "Legacy Energy"),
})
_UNIT_ENERGY = {
    "sm5-137": frozenset({"G", "R", "W"}),
    "sm5-170": frozenset({"G", "R", "W"}),
    "sm5-138": frozenset({"L", "P", "M"}),
    "sm5-171": frozenset({"L", "P", "M"}),
    "sm6-118": frozenset({"F", "D", "Y"}),
    "sm6-146": frozenset({"F", "D", "Y"}),
}
_BASIC_TAGS = frozenset({"Basic", "Basic Pokémon", "Basic Pokemon"})


def provides_required_energy_type(
    attachment: EnergyAttachment,
    active: BoardPokemon,
    required_symbol: str,
    *,
    context: RetreatEnergyProviderContext | None = None,
) -> bool:
    """Return proved positive Energy-type supply for this physical attachment.

    Use exact printed Special Energy effects when normalization deliberately
    projects provider symbols to generic Colorless for Retreat quantity math.
    """
    if context is None:
        context = RetreatEnergyProviderContext()
    card = (attachment.print_id, attachment.card_name)

    if card in _ALL_TYPES:
        return True
    if attachment.card_name == "Rainbow Energy" and attachment.print_id in _RAINBOW_ENERGY:
        return True
    if attachment.card_name == "Prism Energy" and attachment.print_id in _PRISM_ENERGY:
        return bool(active.tags & _BASIC_TAGS)
    if attachment.card_name == "Double Dragon Energy" and attachment.print_id == "xy6-97":
        return "Dragon" in active.tags
    if attachment.card_name == "Fusion Strike Energy" and attachment.print_id == "swsh8-244":
        return "Fusion Strike" in active.tags
    if attachment.card_name == "Counter Energy" and attachment.print_id in COUNTER_ENERGY_PRINT_IDS:
        return (
            context.behind_on_prizes is True
            and not holder_is_pokemon_gx(active.tags)
            and not holder_is_pokemon_ex(active.tags)
        )
    if attachment.card_name == "Reversal Energy" and attachment.print_id in REVERSAL_ENERGY_PRINT_IDS:
        return (
            context.behind_on_prizes is True
            and holder_is_evolution(active.tags)
            and not holder_has_rule_box(active.tags)
        )
    if attachment.card_name == "Luminous Energy" and attachment.print_id in {
        "sv2-191", "sv6-226",
    }:
        return len(active.energy) == 1
    unit_energy_types = _UNIT_ENERGY.get(attachment.print_id)
    if unit_energy_types is not None and attachment.card_name.startswith("Unit Energy"):
        return required_symbol in unit_energy_types

    # Explicitly resolved Basic and single-type Special Energy snapshots.
    return required_symbol in attachment.units


def derive_typed_energy_no_retreat_cost(
    board: BoardState,
    *,
    context: RetreatEnergyProviderContext | None = None,
) -> tuple[RetreatCostModifier, ...]:
    """Resolve self and live in-play friendly team Abilities for own Active."""
    active = board.get(board.active_id)
    modifiers: list[RetreatCostModifier] = []
    for source in board.objects:
        entry = _BY_PRINT.get(source.print_id)
        if (
            entry is None
            or source.card_name != entry.card_name
            or not source.abilities_enabled
        ):
            continue
        if entry.scope == "self" and source.object_id != active.object_id:
            continue
        if any(
            provides_required_energy_type(e, active, entry.energy_type, context=context)
            for e in active.energy
        ):
            modifiers.append(RetreatCostModifier(
                effect_id=f"{source.object_id}:{entry.ability_name}",
                no_retreat_cost=True,
            ))
    return tuple(modifiers)
