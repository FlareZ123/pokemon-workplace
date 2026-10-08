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

MOOMOO_MILK_CURRENT = (
    "Choose 1 of your Pokémon, and then flip 2 coins. For each heads, heal 30 damage from that Pokémon."
)
MOOMOO_MILK_LEGACY = (
    "Choose 1 of your Pokémon. Flip 2 coins. For each heads, remove 3 damage counters from that Pokémon."
)

VS_SEEKER_CURRENT = "Put a Supporter card from your discard pile into your hand."
VS_SEEKER_LEGACY = (
    "Search your discard pile for a Supporter card, show it to your opponent, and put it into your hand."
)

BILLS_MAINTENANCE_CURRENT = "Shuffle a card from your hand into your deck. If you do, draw 3 cards."
BILLS_MAINTENANCE_LEGACY = (
    "If you have any cards in your hand, shuffle 1 of them into your deck, then draw 3 cards."
)

UNDERGROUND_EXPEDITION_CURRENT = (
    "Look at the bottom 4 cards of your deck and put 2 of them into your hand. "
    "Put the other cards back on the bottom of your deck in any order."
)
UNDERGROUND_EXPEDITION_LEGACY = frozenset(
    {
        (
            "Look at the bottom 4 cards of your deck. Put 2 of those cards into your hand, "
            "and then return the remaining cards to the bottom of your deck in any order."
        ),
        (
            "Look at the 4 cards from the bottom of your deck. Choose any 2 cards there and "
            "put them into your hand. Put the remaining cards back on the bottom of your deck in any order."
        ),
    }
)


RULE_EVIDENCE = {
    "fisherman_number_shortage": "resources/advanced-players-rulebook.md II-A",
    "fisherman_public_discard": "https://www.pokemon.com/us/play-pokemon/about/pokemon-tcg-glossary",
    "life_herb_heal": "resources/advanced-players-rulebook.md C-06",
    "life_herb_damage_counter": "resources/advanced-players-rulebook.md C-07",
    "moomoo_milk_heal": "resources/advanced-players-rulebook.md C-06",
    "moomoo_milk_damage_counter": "resources/advanced-players-rulebook.md C-07",
    "vs_seeker_public_discard": "https://www.pokemon.com/us/play-pokemon/about/pokemon-tcg-glossary",
    "vs_seeker_implied_choice": "resources/advanced-players-rulebook.md D-04",
    "bills_maintenance_supporter_playability": "resources/advanced-players-rulebook.md B-03",
    "bills_maintenance_dependency": "resources/advanced-players-rulebook.md E-20",
    "underground_expedition_number_shortage": "resources/advanced-players-rulebook.md II-A",
    "underground_expedition_choice": "resources/advanced-players-rulebook.md D-04",
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
    elif normalized.get("name") == "Moomoo Milk":
        rules = [
            MOOMOO_MILK_CURRENT if rule == MOOMOO_MILK_LEGACY else rule
            for rule in rules
        ]
    elif normalized.get("name") == "VS Seeker":
        rules = [
            VS_SEEKER_CURRENT if rule == VS_SEEKER_LEGACY else rule
            for rule in rules
        ]
    elif normalized.get("name") == "Bill's Maintenance":
        rules = [
            BILLS_MAINTENANCE_CURRENT if rule == BILLS_MAINTENANCE_LEGACY else rule
            for rule in rules
        ]
    elif normalized.get("name") == "Underground Expedition":
        rules = [
            UNDERGROUND_EXPEDITION_CURRENT if rule in UNDERGROUND_EXPEDITION_LEGACY else rule
            for rule in rules
        ]

    if rules:
        normalized["rules"] = rules
    elif "rules" in normalized:
        normalized.pop("rules")
    return normalized
