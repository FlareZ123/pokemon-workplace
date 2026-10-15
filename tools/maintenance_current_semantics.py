from __future__ import annotations

from typing import Any

# Official Pokemon Black & White introduction defines Item as the modern name
# for pre-Black & White plain Trainer cards, such as Poké Ball and PlusPower:
# https://www.pokemon.com/uk/pokemon-tcg/black-white
# This normalization is intentionally restricted to two printed Maintenance
# texts whose conditional two-card shuffle matches the modern version.
LEGACY_IDS = frozenset({"base1-83", "base4-112"})
LEGACY_RULE = (
    "Shuffle 2 of the other cards from your hand into your deck "
    "in order to draw a card."
)
CURRENT_RULE = (
    "Shuffle 2 cards from your hand into your deck. "
    "(If you can't shuffle 2 cards into your deck, you can't play this card.) "
    "Then, draw a card."
)


def normalize_historical_maintenance(card: dict[str, Any]) -> dict[str, Any]:
    """Apply audited current-effect semantics to two former plain Trainers."""
    if card.get("id") not in LEGACY_IDS:
        return card
    if (
        card.get("name") != "Maintenance"
        or card.get("supertype") != "Trainer"
        or (card.get("subtypes") or []) not in ([], ["Item"])
    ):
        raise ValueError(f"Audited Maintenance identity changed: {card['id']}")

    rules = card.get("rules") or []
    if rules not in ([LEGACY_RULE], [CURRENT_RULE]):
        raise ValueError(f"Audited Maintenance effect changed: {card['id']}")

    if card.get("subtypes") == ["Item"] and rules == [CURRENT_RULE]:
        return card
    return {**card, "subtypes": ["Item"], "rules": [CURRENT_RULE]}
