from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json
from tools.current_card_semantics import current_semantic_fingerprint

CURRENT_HANDBOOK_SOURCE = (
    "Play! Pokemon Tournament Handbook reprint example: Copycat"
)
EXPLICIT_POSITIVE_SOURCE_ID = "ex7-83"
EXPLICIT_POSITIVE_TARGET_ID = "sm7-127"


def collect_known_equivalent_ids(resources_root: Path) -> dict[str, str]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = frozenset(
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    )

    cards: list[dict[str, Any]] = []
    cards_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards.append(card)
            cards_by_id[card["id"]] = card

    source = cards_by_id[EXPLICIT_POSITIVE_SOURCE_ID]
    target = cards_by_id[EXPLICIT_POSITIVE_TARGET_ID]
    if source["name"] != target["name"] or source["name"] != "Copycat":
        raise ValueError("Current-handbook Copycat exemplar identity changed")
    if target["_set_id"] not in expanded_sets:
        raise ValueError("Current-handbook Copycat target is no longer in Expanded scope")
    if classify_effective_legality(target)[0] != "Legal":
        raise ValueError("Current-handbook Copycat target is not effectively legal")

    source_fingerprint = current_semantic_fingerprint(source)
    result: dict[str, str] = {}
    for card in cards:
        if card["_set_id"] in expanded_sets:
            continue
        if card.get("name") != source["name"]:
            continue
        if current_semantic_fingerprint(card) != source_fingerprint:
            continue
        result[card["id"]] = CURRENT_HANDBOOK_SOURCE

    if EXPLICIT_POSITIVE_SOURCE_ID not in result:
        raise ValueError("Explicit Copycat source was not recovered")
    return dict(sorted(result.items()))


def summarize_positive_reprint_evidence(resources_root: Path) -> dict[str, Any]:
    reasons = collect_known_equivalent_ids(resources_root)
    cards_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            cards_by_id[raw["id"]] = raw

    names = Counter(cards_by_id[card_id]["name"] for card_id in reasons)
    sources = Counter(reasons.values())
    return {
        "counts": {
            "official_semantic_candidate_prints": len(reasons),
            "names": len(names),
        },
        "prints_by_name": dict(sorted(names.items())),
        "reasons": dict(sorted(sources.items())),
        "card_ids": sorted(reasons),
        "explicit_target_id": EXPLICIT_POSITIVE_TARGET_ID,
    }
