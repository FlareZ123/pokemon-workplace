from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    load_json,
)


@dataclass(frozen=True)
class EmptyAttackFieldMatch:
    source_card_id: str
    name: str
    target_card_ids: tuple[str, ...]


def normalize_empty_attack_fields(card: dict[str, Any]) -> dict[str, Any]:
    """Canonicalize absent and empty optional attack text fields."""

    normalized = deepcopy(card)
    attacks = normalized.get("attacks")
    if not isinstance(attacks, list):
        return normalized

    for attack in attacks:
        if not isinstance(attack, dict):
            continue
        for key in ("damage", "text"):
            if attack.get(key) == "":
                attack.pop(key)
    return normalized


def audit_empty_attack_field_matches(
    resources_root: Path,
) -> tuple[EmptyAttackFieldMatch, ...]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    cards: list[dict[str, Any]] = []
    legal_by_name: dict[str, list[dict[str, Any]]] = {}
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards.append(card)
            if path.stem in expanded_sets and classify_effective_legality(card)[0] == "Legal":
                legal_by_name.setdefault(card["name"], []).append(card)

    rows: list[EmptyAttackFieldMatch] = []
    for source in cards:
        if source["_set_id"] in expanded_sets:
            continue
        targets = legal_by_name.get(source["name"], ())
        if not targets:
            continue

        raw_source = gameplay_fingerprint(source)
        normalized_source = gameplay_fingerprint(
            normalize_empty_attack_fields(source)
        )
        matching_targets = tuple(
            sorted(
                target["id"]
                for target in targets
                if gameplay_fingerprint(normalize_empty_attack_fields(target))
                == normalized_source
                and gameplay_fingerprint(target) != raw_source
            )
        )
        if matching_targets:
            rows.append(
                EmptyAttackFieldMatch(
                    source_card_id=source["id"],
                    name=source["name"],
                    target_card_ids=matching_targets,
                )
            )

    return tuple(rows)
