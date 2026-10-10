"""Exact-print no-Retreat-Cost Abilities gated by attached Energy amount.

Thresholds compare current provided Energy units, not Energy card count.
The caller is responsible for resolving conditional Energy before this pass.
"""
from __future__ import annotations

from dataclasses import dataclass

from board_object_kernel import BoardPokemon
from retreat_cost_semantics import RetreatCostModifier


@dataclass(frozen=True)
class LowEnergyNoRetreatCostSource:
    print_id: str
    card_name: str
    ability_name: str
    max_attached_units: int


LOW_ENERGY_NO_RETREAT_SOURCES = (
    LowEnergyNoRetreatCostSource("bw8-22", "Lampent", "Freefloating", 0),
    LowEnergyNoRetreatCostSource("bw8-53", "Zubat", "Free Flight", 0),
    LowEnergyNoRetreatCostSource("sm10-98", "Gligar", "Free Flight", 0),
    LowEnergyNoRetreatCostSource("me2-11", "Charmander", "Agile", 0),
    LowEnergyNoRetreatCostSource("sv10-36", "Ethan's Magcargo", "Melt Away", 0),
    LowEnergyNoRetreatCostSource("me2pt5-24", "Ethan's Magcargo", "Melt Away", 0),
    LowEnergyNoRetreatCostSource("me2pt5-222", "Ethan's Magcargo", "Melt Away", 0),
    LowEnergyNoRetreatCostSource("sv4-121", "Morpeko", "In a Hungry Hurry", 0),
    LowEnergyNoRetreatCostSource("sv4-206", "Morpeko", "In a Hungry Hurry", 0),
    LowEnergyNoRetreatCostSource("sm11-51", "Golisopod", "Emergency Exit", 2),
)
_SOURCES_BY_PRINT = {source.print_id: source for source in LOW_ENERGY_NO_RETREAT_SOURCES}


def derive_attached_energy_threshold_no_cost(
    active: BoardPokemon,
) -> RetreatCostModifier | None:
    """Return active source only when its printed and live conditions hold."""
    source = _SOURCES_BY_PRINT.get(active.print_id)
    if (
        source is None
        or source.card_name != active.card_name
        or not active.abilities_enabled
    ):
        return None
    provided = sum(len(energy.units) for energy in active.energy)
    if provided > source.max_attached_units:
        return None
    return RetreatCostModifier(
        effect_id=f"{active.object_id}:{source.ability_name}",
        no_retreat_cost=True,
    )
