from __future__ import annotations

from typing import Any

# Four English Trainer Kit historical prints store the same text.
HISTORICAL_IDS = frozenset({"tk1a-9", "tk1b-9", "tk2a-8", "tk2b-9"})
HISTORICAL_RULE = (
    "Search your deck for a basic Energy card, show it to your opponent, "
    "and put it into your hand. Shuffle your deck afterward"
)
CURRENT_RULE = (
    "Search your deck for a basic Energy card, reveal it, and put it "
    "into your hand. Shuffle your deck afterward."
)


def normalize_historical_energy_search(card: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize only four exact public-reveal, restricted-search prints."""
    if card.get("id") not in HISTORICAL_IDS:
        return card
    if (
        card.get("name") != "Energy Search"
        or card.get("supertype") != "Trainer"
        or card.get("subtypes") != ["Item"]
        or card.get("rules") not in ([HISTORICAL_RULE], [CURRENT_RULE])
    ):
        raise ValueError(f"Audited Trainer Kit Energy Search changed: {card['id']}")
    if card["rules"] == [CURRENT_RULE]:
        return card
    return {**card, "rules": [CURRENT_RULE]}
