from __future__ import annotations

from typing import Any

# 30th Celebration 96/128, official Pokémon card database:
# https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/30th/96
# The bundled me55 source omits the printed "Evolves From: Zorua".
CARD_ID = "me55-96"
PARENT = "Zorua"


def normalize_verified_evolution_parent(card: dict[str, Any]) -> dict[str, Any]:
    """Restore a physically verified evolution parent for one exact print."""
    if card.get("id") != CARD_ID:
        return card
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
