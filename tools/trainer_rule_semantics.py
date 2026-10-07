from __future__ import annotations

from copy import deepcopy
from typing import Any

FISHERMAN_CURRENT = "Put 4 basic Energy cards from your discard pile into your hand."
FISHERMAN_LEGACY = frozenset(
    {
        (
            "Choose 4 basic Energy cards from your discard pile (if there are fewer basic Energy "
            "cards than choose, take all of them), show them to your opponent, and put them into "
            "your hand."
        ),
        (
            "Search your discard pile for 4 basic Energy cards, show them to your opponent, and "
            "put them into your hand."
        ),
    }
)

LIFE_HERB_CURRENT = (
    "Flip a coin. If heads, heal 60 damage and remove all Special Conditions from 1 of your Pokémon."
)
LIFE_HERB_LEGACY_NO_EXCLUSION = (
    "Flip a coin. If heads, choose 1 of your Pokémon, and remove all Special Conditions and "
    "6 damage counters from that Pokémon (all if there are less than 6)."
)

RULE_EVIDENCE = {
    "fisherman_number_shortage": "resources/advanced-players-rulebook.md II-A",
    "fisherman_public_discard": "https://www.pokemon.com/us/play-pokemon/about/pokemon-tcg-glossary",
    "life_herb_heal": "resources/advanced-players-rulebook.md C-06",
    "life_herb_damage_counter": "resources/advanced-players-rulebook.md C-07",
}


def normalize_rule_grounded_trainer_semantics(card: dict[str, Any]) -> dict[str, Any]:
    """Normalize narrowly proven historical Trainer wordings to current semantics."""

    normalized = deepcopy(card)
    if normalized.get("supertype") != "Trainer":
        return normalized

    rules = list(normalized.get("rules") or ())
    if normalized.get("name") == "Fisherman":
        rules = [
            FISHERMAN_CURRENT if rule in FISHERMAN_LEGACY else rule
            for rule in rules
        ]
    elif normalized.get("name") == "Life Herb":
        rules = [
            LIFE_HERB_CURRENT if rule == LIFE_HERB_LEGACY_NO_EXCLUSION else rule
            for rule in rules
        ]

    if rules:
        normalized["rules"] = rules
    elif "rules" in normalized:
        normalized.pop("rules")
    return normalized
