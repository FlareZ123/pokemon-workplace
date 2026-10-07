from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    has_tournament_ban_rule,
    load_json,
)
from tools.current_card_semantics import (
    current_semantic_fingerprint,
    normalize_current_card_semantics,
)
from tools.reprint_negative_evidence import collect_known_non_equivalent_ids
from tools.trainer_boilerplate_normalization import normalize_trainer_boilerplate


def boilerplate_semantic_fingerprint(card: dict[str, Any]) -> str:
    normalized = normalize_current_card_semantics(card)
    normalized = normalize_trainer_boilerplate(normalized)
    return gameplay_fingerprint(normalized)


def audit_boilerplate_candidate_delta(resources_root: Path) -> dict[str, Any]:
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

    legal_by_current: dict[str, list[dict[str, Any]]] = defaultdict(list)
    legal_by_candidate: dict[str, list[dict[str, Any]]] = defaultdict(list)
    legal_names: set[str] = set()
    for card in cards:
        if card["_set_id"] not in expanded_sets:
            continue
        if classify_effective_legality(card)[0] != "Legal":
            continue
        legal_names.add(card["name"])
        legal_by_current[current_semantic_fingerprint(card)].append(card)
        legal_by_candidate[boilerplate_semantic_fingerprint(card)].append(card)

    newly_exact: list[dict[str, Any]] = []
    for card in cards:
        if card["_set_id"] in expanded_sets:
            continue
        if card["name"] not in legal_names:
            continue
        if has_tournament_ban_rule(card):
            continue
        if (card.get("legalities") or {}).get("unlimited") == "Banned":
            continue

        current_targets = legal_by_current.get(current_semantic_fingerprint(card), ())
        candidate_targets = legal_by_candidate.get(
            boilerplate_semantic_fingerprint(card), ()
        )
        if current_targets or not candidate_targets:
            continue

        newly_exact.append(
            {
                "id": card["id"],
                "name": card["name"],
                "set_id": card["_set_id"],
                "supertype": card.get("supertype"),
                "candidate_target_ids": sorted(
                    target["id"] for target in candidate_targets
                ),
            }
        )

    negative_ids = set(collect_known_non_equivalent_ids(resources_root))
    negative_collisions = sorted(
        row["id"] for row in newly_exact if row["id"] in negative_ids
    )

    by_name = Counter(row["name"] for row in newly_exact)
    by_supertype = Counter(row["supertype"] for row in newly_exact)
    return {
        "counts": {
            "new_exact_candidate_prints": len(newly_exact),
            "new_exact_candidate_names": len(by_name),
            "new_exact_candidate_supertypes": dict(sorted(by_supertype.items())),
            "known_negative_collisions": len(negative_collisions),
        },
        "new_exact_by_name": dict(sorted(by_name.items())),
        "known_negative_collision_ids": negative_collisions,
        "rows": sorted(newly_exact, key=lambda row: (row["name"], row["id"])),
    }
