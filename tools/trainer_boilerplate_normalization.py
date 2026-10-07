from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    load_json,
)

ITEM_PLAY_RULES = frozenset(
    {
        "You may play as many Item cards as you like during your turn (before your attack).",
        "You may play any number of Item cards during your turn.",
    }
)

SUPPORTER_PLAY_RULES = frozenset(
    {
        "You may play only 1 Supporter card during your turn.",
        "You may play only 1 Supporter card during your turn (before your attack).",
        (
            "You can play only one Supporter card each turn. When you play this card, "
            "put it next to your Active Pokémon. When your turn ends, discard this card."
        ),
        (
            "You can play only 1 Supporter card each turn. When you play this card, "
            "put it next to your Active Pokémon. When your turn ends, discard this card."
        ),
    }
)


def normalize_trainer_boilerplate(card: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(card)
    if normalized.get("supertype") != "Trainer":
        return normalized

    subtypes = set(normalized.get("subtypes") or [])
    removable: set[str] = set()
    if "Item" in subtypes:
        removable.update(ITEM_PLAY_RULES)
    if "Supporter" in subtypes:
        removable.update(SUPPORTER_PLAY_RULES)
    if not removable:
        return normalized

    rules = list(normalized.get("rules") or [])
    filtered = [rule for rule in rules if rule not in removable]
    if filtered:
        normalized["rules"] = filtered
    elif "rules" in normalized:
        normalized.pop("rules")
    return normalized


def summarize_trainer_boilerplate(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = frozenset(
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    )

    cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards.append(card)

    changed_archive = [
        card
        for card in cards
        if gameplay_fingerprint(card)
        != gameplay_fingerprint(normalize_trainer_boilerplate(card))
    ]

    legal_expanded = [
        card
        for card in cards
        if card["_set_id"] in expanded_sets
        and classify_effective_legality(card)[0] == "Legal"
    ]
    changed_legal = [
        card
        for card in legal_expanded
        if gameplay_fingerprint(card)
        != gameplay_fingerprint(normalize_trainer_boilerplate(card))
    ]

    raw_fingerprints = {gameplay_fingerprint(card) for card in legal_expanded}
    normalized_fingerprints = {
        gameplay_fingerprint(normalize_trainer_boilerplate(card))
        for card in legal_expanded
    }

    normalized_groups: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for card in legal_expanded:
        raw = gameplay_fingerprint(card)
        normalized = gameplay_fingerprint(normalize_trainer_boilerplate(card))
        normalized_groups[normalized][raw].append(card["id"])

    merge_groups = {
        normalized: raw_groups
        for normalized, raw_groups in normalized_groups.items()
        if len(raw_groups) > 1
    }

    archive_rule_counts = Counter(
        rule
        for card in changed_archive
        for rule in (card.get("rules") or [])
        if rule in ITEM_PLAY_RULES or rule in SUPPORTER_PLAY_RULES
    )

    def subtype_count(rows: list[dict[str, Any]], subtype: str) -> int:
        return sum(subtype in (card.get("subtypes") or []) for card in rows)

    merge_names = []
    for raw_groups in merge_groups.values():
        ids = {card_id for group in raw_groups.values() for card_id in group}
        names = {card["name"] for card in legal_expanded if card["id"] in ids}
        if len(names) != 1:
            raise ValueError(f"Boilerplate normalization merged different names: {names}")
        merge_names.extend(names)

    return {
        "counts": {
            "archive_changed_prints": len(changed_archive),
            "archive_changed_names": len({card["name"] for card in changed_archive}),
            "archive_item_changed_prints": subtype_count(changed_archive, "Item"),
            "archive_supporter_changed_prints": subtype_count(changed_archive, "Supporter"),
            "legal_expanded_prints": len(legal_expanded),
            "legal_changed_prints": len(changed_legal),
            "legal_changed_names": len({card["name"] for card in changed_legal}),
            "legal_item_changed_prints": subtype_count(changed_legal, "Item"),
            "legal_supporter_changed_prints": subtype_count(changed_legal, "Supporter"),
            "raw_legal_gameplay_fingerprints": len(raw_fingerprints),
            "normalized_legal_gameplay_fingerprints": len(normalized_fingerprints),
            "legal_fingerprint_reduction": len(raw_fingerprints) - len(normalized_fingerprints),
            "legal_merge_groups": len(merge_groups),
        },
        "archive_rule_counts": dict(sorted(archive_rule_counts.items())),
        "legal_merge_names": sorted(merge_names),
    }
