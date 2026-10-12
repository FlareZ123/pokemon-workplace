"""Exact-print conditional self-Ability sources of no Retreat Cost.

These five predicates use observable current state: physical attached Energy,
damage counters, an in-play Stadium, or opponent Pokemon rule-box families.
Printed sources requiring typed Energy or turn history are out of scope.
Stadium presence is independent of whether the Stadium's own effect is enabled.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from board_object_kernel import BoardPokemon, BoardState
from retreat_cost_semantics import RetreatCostModifier
from retreat_dynamic_energy_units import (
    holder_is_pokemon_ex,
    holder_is_pokemon_gx,
    holder_is_pokemon_v,
)

Trigger = Literal["any_energy", "damaged", "stadium", "opponent_v", "opponent_gx_ex"]


@dataclass(frozen=True)
class ConditionalSelfFreeCostSource:
    print_id: str
    card_name: str
    ability_name: str
    trigger: Trigger


SOURCES = (
    ConditionalSelfFreeCostSource("mcd22-10", "Tynamo", "Levitate", "any_energy"),
    ConditionalSelfFreeCostSource("sm7-47", "Voltorb", "Floating Electrons", "any_energy"),
    ConditionalSelfFreeCostSource("sm8-58", "Mantine", "Mantine Surf", "any_energy"),
    ConditionalSelfFreeCostSource("sma-SV13", "Voltorb", "Floating Electrons", "any_energy"),
    ConditionalSelfFreeCostSource("swsh11-52", "Pikachu", "Pika Dash", "any_energy"),
    ConditionalSelfFreeCostSource("swsh11tg-TG05", "Pikachu", "Pika Dash", "any_energy"),
    ConditionalSelfFreeCostSource("swsh12pt5gg-GG30", "Pikachu", "Pika Dash", "any_energy"),
    ConditionalSelfFreeCostSource("swsh4-57", "Tynamo", "Levitate", "any_energy"),
    ConditionalSelfFreeCostSource("xyp-XY163", "Weezing", "Levitate", "any_energy"),
    ConditionalSelfFreeCostSource("swsh10-74", "Sudowoodo", "Vamoose", "damaged"),
    ConditionalSelfFreeCostSource("sm4-31", "Alolan Raichu", "Surge Surfer", "stadium"),
    ConditionalSelfFreeCostSource("sm9-22", "Squirtle", "Floating Shell", "stadium"),
    ConditionalSelfFreeCostSource("smp-SM72", "Alolan Raichu", "Surge Surfer", "stadium"),
    ConditionalSelfFreeCostSource("swsh2-35", "Cinderace V", "Field Runner", "stadium"),
    ConditionalSelfFreeCostSource("swsh2-178", "Cinderace V", "Field Runner", "stadium"),
    ConditionalSelfFreeCostSource("swsh45-18", "Cinderace V", "Field Runner", "stadium"),
    ConditionalSelfFreeCostSource("swshp-SWSH015", "Cinderace V", "Field Runner", "stadium"),
    ConditionalSelfFreeCostSource("xy8-70", "Cresselia", "My Way", "stadium"),
    ConditionalSelfFreeCostSource("pgo-25", "Wimpod", "Punk Out", "opponent_v"),
    ConditionalSelfFreeCostSource("sm10-127", "Genesect", "Fast-Flight Configuration", "opponent_gx_ex"),
    ConditionalSelfFreeCostSource("sm8-50", "Litleo", "Wild Dash", "opponent_gx_ex"),
)
_BY_PRINT = {source.print_id: source for source in SOURCES}


def derive_conditional_self_free_cost(
    active: BoardPokemon,
    opponent: BoardState,
    *,
    stadium_print_id: str | None = None,
) -> RetreatCostModifier | None:
    """Resolve only verified printed Abilities with satisfied live predicates."""
    source = _BY_PRINT.get(active.print_id)
    if (
        source is None
        or active.card_name != source.card_name
        or not active.abilities_enabled
    ):
        return None

    trigger = source.trigger
    enabled = (
        bool(active.energy) if trigger == "any_energy" else
        active.damage_counters > 0 if trigger == "damaged" else
        stadium_print_id is not None if trigger == "stadium" else
        any(holder_is_pokemon_v(p.tags) for p in opponent.objects)
            if trigger == "opponent_v" else
        any(
            holder_is_pokemon_gx(p.tags) or holder_is_pokemon_ex(p.tags)
            for p in opponent.objects
        )
    )
    if not enabled:
        return None
    return RetreatCostModifier(
        effect_id=f"{active.object_id}:{source.ability_name}",
        no_retreat_cost=True,
    )
