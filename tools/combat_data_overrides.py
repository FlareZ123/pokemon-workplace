"""Audited combat-field overrides applied above the bundled card database."""

from __future__ import annotations

from copy import deepcopy


COMBAT_DATA_OVERRIDES = {
    "me55-93": {
        "resistances": [{"type": "Fighting", "value": "-30"}],
        "reason": "bundled resistance value conflicts with independent current card listings",
        "sources": (
            "https://www.serebii.net/card/30thcelebration/093.shtml",
            "https://newrealmgames.com/products/murkrow-093-128-common-holofoil",
            "https://outof.games/realms/pokemon-tcg/cards/30th-celebration/murkrow-100019027/",
            "https://collectorsedge.co.uk/products/pokemon-30th-celebration-murkrow-093-128-holofoil",
        ),
    }
}


def apply_combat_data_overrides(card: dict) -> dict:
    """Return an isolated card mapping with audited combat corrections applied."""

    corrected = deepcopy(card)
    override = COMBAT_DATA_OVERRIDES.get(card.get("id"))
    if override is None:
        return corrected

    for field in ("weaknesses", "resistances"):
        if field in override:
            corrected[field] = deepcopy(override[field])
    return corrected
