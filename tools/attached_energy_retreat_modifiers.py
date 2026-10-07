"""Derive Retreat Cost modifiers from exact attached Special Energy."""

from __future__ import annotations

from dataclasses import dataclass

from board_object_kernel import BoardPokemon
from retreat_cost_semantics import RetreatCostModifier, no_retreat_cost


@dataclass(frozen=True, order=True)
class AttachedEnergyRetreatRule:
    print_id: str
    card_name: str
    holder_tag: str
    delta: int = 0
    makes_no_retreat_cost: bool = False


ATTACHED_ENERGY_RETREAT_RULES = (
    AttachedEnergyRetreatRule(
        "me4-85",
        "Magnetic Metal Energy",
        "Metal",
        makes_no_retreat_cost=True,
    ),
    AttachedEnergyRetreatRule(
        "swsh3-175",
        "Hiding Darkness Energy",
        "Darkness",
        makes_no_retreat_cost=True,
    ),
    AttachedEnergyRetreatRule(
        "xy4-112",
        "Mystery Energy",
        "Psychic",
        delta=-2,
    ),
)
_RULE_BY_PRINT = {
    rule.print_id: rule
    for rule in ATTACHED_ENERGY_RETREAT_RULES
}


def attached_energy_retreat_modifiers(
    pokemon: BoardPokemon,
) -> tuple[RetreatCostModifier, ...]:
    """Return exact attached-Energy Retreat modifiers active on this holder."""

    modifiers = []
    for energy in pokemon.energy:
        if energy.print_id is None:
            continue
        rule = _RULE_BY_PRINT.get(energy.print_id)
        if (
            rule is None
            or energy.card_name != rule.card_name
            or rule.holder_tag not in pokemon.tags
        ):
            continue

        effect_id = f"{energy.instance_id}:{rule.card_name}"
        if rule.makes_no_retreat_cost:
            modifiers.append(no_retreat_cost(effect_id))
        else:
            modifiers.append(
                RetreatCostModifier(effect_id, delta=rule.delta)
            )

    return tuple(modifiers)
