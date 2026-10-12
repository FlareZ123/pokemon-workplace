from __future__ import annotations

from copy import deepcopy
from typing import Any

CARD_ID = "sv8pt5-92"
CARD_NAME = "Terapagos ex"
OLD_SUBTYPES = ("Basic", "ex")
NEW_SUBTYPES = ("Basic", "Tera", "ex")
TERA_RULE = (
    "As long as this Pokémon is on your Bench, prevent all damage done to this "
    "Pokémon by attacks (both yours and your opponent's)."
)
EX_RULE = (
    "Pokémon ex rule: When your Pokémon ex is Knocked Out, "
    "your opponent takes 2 Prize cards."
)


def normalize_verified_tera_metadata(card: dict[str, Any]) -> dict[str, Any]:
    """Repair the exact Prismatic Evolutions #92 missing Tera subtype and rule.

    Independent field guards permit idempotent partial upstream corrections.
    Other print IDs remain unchanged, including same-name other-attack cards.
    """
    normalized = deepcopy(card)
    if normalized.get("id") != CARD_ID:
        return normalized

    if (
        normalized.get("name") != CARD_NAME
        or normalized.get("supertype") != "Pokémon"
        or normalized.get("hp") != "230"
        or normalized.get("types") != ["Colorless"]
    ):
        raise ValueError("Audited Terapagos ex print identity changed")

    stages = tuple(normalized.get("subtypes") or ())
    if stages not in (OLD_SUBTYPES, NEW_SUBTYPES):
        raise ValueError(f"Unexpected Terapagos ex subtypes: {stages}")

    rules = normalized.get("rules") or []
    if rules not in ([EX_RULE], [TERA_RULE, EX_RULE]):
        raise ValueError("Unexpected Terapagos ex rule text")

    normalized["subtypes"] = list(NEW_SUBTYPES)
    normalized["rules"] = [TERA_RULE, EX_RULE]
    return normalized
