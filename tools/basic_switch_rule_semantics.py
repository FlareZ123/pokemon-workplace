from __future__ import annotations

from typing import Any

SWITCH_CURRENT = "Switch your Active Pokémon with 1 of your Benched Pokémon."
SWITCH_OLD = "Switch 1 of your Active Pokémon with 1 of your Benched Pokémon."

ENERGY_SWITCH_CURRENT = "Move a basic Energy from 1 of your Pokémon to another of your Pokémon."
ENERGY_SWITCH_OLD = "Move a basic Energy card attached to 1 of your Pokémon to another of your Pokémon."
ENERGY_SWITCH_OLD_MISSING_TO = "Move a basic Energy card attached 1 of your Pokémon to another of your Pokémon."

SUPPORTED_RULES: dict[str, dict[str, str]] = {
    "Switch": {SWITCH_OLD: SWITCH_CURRENT},
    "Energy Switch": {
        ENERGY_SWITCH_OLD: ENERGY_SWITCH_CURRENT,
        ENERGY_SWITCH_OLD_MISSING_TO: ENERGY_SWITCH_CURRENT,
    },
}


def normalize_basic_switch_wording(card: dict[str, Any]) -> dict[str, Any]:
    """Normalize exact Item movement wordings with identical actions.

    Expanded has one Active Pokémon, and "a basic Energy card attached"
    and "a basic Energy from" both refer to one attached Basic Energy card.
    """
    if (
        card.get("supertype") != "Trainer"
        or "Item" not in (card.get("subtypes") or ())
        or card.get("name") not in SUPPORTED_RULES
    ):
        return card
    mappings = SUPPORTED_RULES[card["name"]]
    old_rules = card.get("rules") or ()
    new_rules = [mappings.get(rule, rule) for rule in old_rules]
    if new_rules == list(old_rules):
        return card
    normalized = dict(card)
    normalized["rules"] = new_rules
    return normalized
