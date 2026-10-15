from __future__ import annotations

from typing import Any

# 30th Celebration 96/128, official Pokémon card database:
# https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/30th/96
# The bundled me55 source omits the printed "Evolves From: Zorua".
CARD_ID = "me55-96"
PARENT = "Zorua"

# White Flare #50 and #131 source-text typo: "Antiuqe" versus official
# Antique Plume Fossil #79, whose printed text explicitly evolves into Archen.
# https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/rsv10pt5/79
ARCHEN_IDS = frozenset({"rsv10pt5-50", "rsv10pt5-131"})
ARCHEN_SOURCE_PARENT = "Antiuqe Plume Fossil"
ARCHEN_PARENT = "Antique Plume Fossil"
AUDITED_EVOLUTION_PARENT_PRINTS = frozenset({CARD_ID}) | ARCHEN_IDS


def normalize_verified_evolution_parent(card: dict[str, Any]) -> dict[str, Any]:
    """Restore a physically verified evolution parent for one exact print."""
    if card.get("id") not in AUDITED_EVOLUTION_PARENT_PRINTS:
        return card
    if card["id"] in ARCHEN_IDS:
        if (
            card.get("name") != "Archen"
            or card.get("supertype") != "Pokémon"
            or card.get("subtypes") != ["Stage 1"]
            or card.get("hp") != "80"
            or card.get("regulationMark") != "I"
            or not any(a.get("name") == "Acrobatics" for a in card.get("attacks", []))
        ):
            raise ValueError(f"Audited Archen print identity changed: {card['id']}")
        if card.get("evolvesFrom") not in (ARCHEN_SOURCE_PARENT, ARCHEN_PARENT):
            raise ValueError(f"Audited Archen source parent changed: {card['id']}")
        if card["evolvesFrom"] == ARCHEN_PARENT:
            return card
        return {**card, "evolvesFrom": ARCHEN_PARENT}
    if (
        card.get("name") != "Zoroark"
        or card.get("supertype") != "Pokémon"
        or card.get("subtypes") != ["Stage 1"]
        or card.get("hp") != "120"
        or card.get("regulationMark") != "J"
        or not any(a.get("name") == "Nighttime Byway" for a in card.get("abilities", []))
    ):
        raise ValueError("Audited Zoroark print identity changed: me55-96")
    if card.get("evolvesFrom") not in (None, PARENT):
        raise ValueError("Audited Zoroark evolution parent changed: me55-96")
    if card.get("evolvesFrom") == PARENT:
        return card
    return {**card, "evolvesFrom": PARENT}
