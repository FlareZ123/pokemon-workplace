from __future__ import annotations

from copy import deepcopy
from typing import Any

# Source: the 2026-10-10 bundled card snapshot in resources/cards/en/me5.json.
# Every correction is guarded by the stored print identity and raw fields.
KNOWN_STAGE_REPAIRS = {
    "me5-42": ("Mankey", (), ("Basic",)),
    "me5-115": ("Mega Chandelure ex", ("MEGA", "ex"), ("Stage 2", "MEGA", "ex")),
}
CHAND_RULE = (
    "Mega Evolution ex Rule: When your Mega Evolution Pokémon ex is Knocked Out, "
    "your opponent takes 3 Prize cards."
)


def normalize_verified_stage_metadata(card: dict[str, Any]) -> dict[str, Any]:
    """Patch only two independently verified missing stage fields.

    This is an opt-in layer for research tooling, intentionally not yet
    included in the central fingerprint/legality pipeline.
    """
    normalized = deepcopy(card)
    card_id = str(card.get("id", ""))
    if card_id not in KNOWN_STAGE_REPAIRS:
        return normalized

    name, expected, correct = KNOWN_STAGE_REPAIRS[card_id]
    if normalized.get("name") != name or normalized.get("supertype") != "Pokémon":
        raise ValueError(f"Stage repair identity changed: {card_id}")
    actual = tuple(normalized.get("subtypes") or ())
    if actual == correct:
        return normalized
    if actual != expected:
        raise ValueError(f"Audited stage fields changed: {card_id}: {actual}")

    if card_id == "me5-42":
        if normalized.get("hp") != "50" or normalized.get("evolvesFrom") is not None:
            raise ValueError("Mankey print's basic identity fields changed")
    else:
        if normalized.get("hp") != "350" or normalized.get("evolvesFrom") != "Lampent":
            raise ValueError("Mega Chandelure print's identity fields changed")
        if normalized.get("rules"):
            raise ValueError("Unexpected special-rule text in defective Chandelure record")
        normalized["rules"] = [CHAND_RULE]

    normalized["subtypes"] = list(correct)
    return normalized
