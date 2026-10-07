from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json
from tools.current_card_semantics import current_semantic_fingerprint

TOURNAMENT_HANDBOOK_NEGATIVE_SOURCE = "Tournament Handbook reprint example: Rainbow Energy"
CONTEXTUAL_DIVERGENCE_SOURCE = (
    "Current Expanded target-scope divergence: Life Herb excludes Pokémon-ex"
)
EXPLICIT_NEGATIVE_EXEMPLAR_ID = "base5-17"
CONTEXTUAL_NON_EQUIVALENT_IDS = frozenset({"ex5-90", "ex6-93"})
STRUCTURAL_ENERGY_COLLISION_NAMES = frozenset({"Darkness Energy", "Metal Energy"})


def collect_known_non_equivalent_ids(resources_root: Path) -> dict[str, str]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = frozenset(
        row["id"] for row in sets if (row.get("legalities") or {}).get("expanded") == "Legal"
    )

    cards: list[dict[str, Any]] = []
    cards_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards.append(card)
            cards_by_id[card["id"]] = card

    legal_by_name: dict[str, list[dict[str, Any]]] = {}
    for card in cards:
        if card["_set_id"] not in expanded_sets:
            continue
        if classify_effective_legality(card)[0] != "Legal":
            continue
        legal_by_name.setdefault(card["name"], []).append(card)

    result: dict[str, str] = {}

    for name in STRUCTURAL_ENERGY_COLLISION_NAMES:
        targets = legal_by_name.get(name, [])
        if not targets or any("Basic" not in (target.get("subtypes") or []) for target in targets):
            raise ValueError(f"Expected all current {name} targets to be Basic Energy")
        for card in cards:
            if card["_set_id"] in expanded_sets or card.get("name") != name:
                continue
            if "Special" in (card.get("subtypes") or []):
                result[card["id"]] = "historical Special Energy versus current Basic Energy"

    exemplar = cards_by_id[EXPLICIT_NEGATIVE_EXEMPLAR_ID]
    exemplar_fingerprint = current_semantic_fingerprint(exemplar)
    for card in cards:
        if card["_set_id"] in expanded_sets:
            continue
        if card.get("name") != "Rainbow Energy":
            continue
        if current_semantic_fingerprint(card) == exemplar_fingerprint:
            result[card["id"]] = TOURNAMENT_HANDBOOK_NEGATIVE_SOURCE

    current_life_herb = legal_by_name.get("Life Herb", [])
    if not current_life_herb:
        raise ValueError("Expected a current legal Expanded Life Herb")
    if any(
        "excluding Pokémon-ex" in " ".join(target.get("rules") or ())
        for target in current_life_herb
    ):
        raise ValueError("Current legal Life Herb unexpectedly retains Pokémon-ex exclusion")

    pokemon_ex_witnesses = [
        card
        for card in cards
        if card["_set_id"] in expanded_sets
        and classify_effective_legality(card)[0] == "Legal"
        and any(
            "When Pokémon-ex has been Knocked Out" in rule
            for rule in (card.get("rules") or ())
        )
    ]
    if not pokemon_ex_witnesses:
        raise ValueError("No current legal Expanded Pokémon-ex witness found")

    for card_id in CONTEXTUAL_NON_EQUIVALENT_IDS:
        card = cards_by_id[card_id]
        if card["_set_id"] in expanded_sets or card.get("name") != "Life Herb":
            raise ValueError(f"Unexpected contextual divergence identity: {card_id}")
        if "excluding Pokémon-ex" not in " ".join(card.get("rules") or ()):
            raise ValueError(f"Life Herb exclusion missing from source text: {card_id}")
        result[card_id] = CONTEXTUAL_DIVERGENCE_SOURCE

    return dict(sorted(result.items()))


def summarize_negative_reprint_evidence(resources_root: Path) -> dict[str, Any]:
    reasons = collect_known_non_equivalent_ids(resources_root)
    cards_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            cards_by_id[raw["id"]] = raw

    names = Counter(cards_by_id[card_id]["name"] for card_id in reasons)
    sources = Counter(reasons.values())
    return {
        "counts": {
            "known_non_equivalent_prints": len(reasons),
            "names": len(names),
        },
        "prints_by_name": dict(sorted(names.items())),
        "reasons": dict(sorted(sources.items())),
        "card_ids": sorted(reasons),
    }
