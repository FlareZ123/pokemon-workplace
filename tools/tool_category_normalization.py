from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    load_json,
)

LEGACY_ITEM_RULES = frozenset(
    {
        "You may play as many Item cards as you like during your turn (before your attack).",
        "You may play any number of Item cards during your turn.",
    }
)


def is_pokemon_tool(card: dict[str, Any]) -> bool:
    return card.get("supertype") == "Trainer" and any(
        subtype.startswith("Pokémon Tool") for subtype in (card.get("subtypes") or [])
    )


def normalize_legacy_tool_category(card: dict[str, Any]) -> dict[str, Any]:
    """Apply the current rule that legacy Pokémon Tools are not Item cards."""

    normalized = deepcopy(card)
    if not is_pokemon_tool(normalized):
        return normalized

    subtypes = list(normalized.get("subtypes") or [])
    if "Item" in subtypes:
        subtypes = [subtype for subtype in subtypes if subtype != "Item"]
        normalized["subtypes"] = subtypes

    rules = list(normalized.get("rules") or [])
    filtered = [rule for rule in rules if rule not in LEGACY_ITEM_RULES]
    if filtered:
        normalized["rules"] = filtered
    elif "rules" in normalized:
        normalized.pop("rules")

    return normalized


def summarize_legacy_tool_normalization(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    set_by_id = {row["id"]: row for row in sets}
    expanded_sets = frozenset(
        row["id"] for row in sets if (row.get("legalities") or {}).get("expanded") == "Legal"
    )

    cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards.append(card)

    legal_expanded = [
        card
        for card in cards
        if card["_set_id"] in expanded_sets and classify_effective_legality(card)[0] == "Legal"
    ]

    changed = [
        card
        for card in legal_expanded
        if gameplay_fingerprint(card)
        != gameplay_fingerprint(normalize_legacy_tool_category(card))
    ]
    dual_item_tool = [
        card
        for card in changed
        if is_pokemon_tool(card) and "Item" in (card.get("subtypes") or [])
    ]
    obsolete_rule = [
        card
        for card in changed
        if any(rule in LEGACY_ITEM_RULES for rule in (card.get("rules") or []))
    ]

    raw_fingerprints = {gameplay_fingerprint(card) for card in legal_expanded}
    normalized_fingerprints = {
        gameplay_fingerprint(normalize_legacy_tool_category(card))
        for card in legal_expanded
    }

    series_counts = Counter(
        set_by_id[card["_set_id"]].get("series") for card in changed
    )
    phrase_counts = Counter(
        rule
        for card in obsolete_rule
        for rule in (card.get("rules") or [])
        if rule in LEGACY_ITEM_RULES
    )

    return {
        "counts": {
            "legal_expanded_prints": len(legal_expanded),
            "changed_tool_prints": len(changed),
            "changed_tool_names": len({card["name"] for card in changed}),
            "dual_item_tool_prints": len(dual_item_tool),
            "obsolete_item_rule_prints": len(obsolete_rule),
            "raw_legal_gameplay_fingerprints": len(raw_fingerprints),
            "normalized_legal_gameplay_fingerprints": len(normalized_fingerprints),
        },
        "changed_by_series": dict(sorted(series_counts.items())),
        "obsolete_item_rule_phrases": dict(sorted(phrase_counts.items())),
        "dual_item_tool_ids": sorted(card["id"] for card in dual_item_tool),
        "changed_tool_ids": sorted(card["id"] for card in changed),
    }
