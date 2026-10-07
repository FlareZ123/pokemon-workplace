from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import (
    gameplay_fingerprint,
    has_tournament_ban_rule,
    load_json,
    classify_effective_legality,
)


def build_candidates(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    all_cards: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            row = dict(raw)
            row["_set_id"] = path.stem
            all_cards.append(row)

    legal_expanded_by_fingerprint: dict[str, list[dict[str, Any]]] = defaultdict(list)
    legal_expanded_names: set[str] = set()
    for card in all_cards:
        if card["_set_id"] not in expanded_sets:
            continue
        status, _source = classify_effective_legality(card)
        if status != "Legal":
            continue
        legal_expanded_by_fingerprint[gameplay_fingerprint(card)].append(card)
        legal_expanded_names.add(card["name"])

    exact_candidates: list[dict[str, Any]] = []
    same_name_review_pool: list[dict[str, Any]] = []
    for card in all_cards:
        if card["_set_id"] in expanded_sets:
            continue
        if has_tournament_ban_rule(card):
            continue
        if (card.get("legalities") or {}).get("unlimited") == "Banned":
            continue

        if card["name"] in legal_expanded_names:
            same_name_review_pool.append(
                {
                    "id": card["id"],
                    "name": card["name"],
                    "set_id": card["_set_id"],
                    "supertype": card.get("supertype"),
                }
            )

        fingerprint = gameplay_fingerprint(card)
        targets = legal_expanded_by_fingerprint.get(fingerprint)
        if not targets:
            continue
        exact_candidates.append(
            {
                "id": card["id"],
                "name": card["name"],
                "set_id": card["_set_id"],
                "supertype": card.get("supertype"),
                "fingerprint": fingerprint,
                "legal_expanded_print_ids": sorted(target["id"] for target in targets),
            }
        )

    by_supertype = Counter(row["supertype"] for row in exact_candidates)
    by_name = Counter(row["name"] for row in exact_candidates)
    by_set = Counter(row["set_id"] for row in exact_candidates)

    return {
        "exact_fingerprint_candidates": exact_candidates,
        "same_name_review_pool": same_name_review_pool,
        "counts": {
            "exact_candidate_prints": len(exact_candidates),
            "exact_candidate_variants": len({row["fingerprint"] for row in exact_candidates}),
            "exact_candidate_names": len(by_name),
            "same_name_review_prints": len(same_name_review_pool),
            "same_name_review_names": len({row["name"] for row in same_name_review_pool}),
            "exact_by_supertype": dict(sorted(by_supertype.items())),
            "exact_by_name": dict(sorted(by_name.items())),
            "exact_by_set": dict(sorted(by_set.items())),
        },
        "interpretation": (
            "Exact gameplay-fingerprint matches are conservative reprint-equivalence candidates, "
            "not an official legality decision. Functional equivalence can survive wording changes, "
            "so same-name candidates outside this exact set still require semantic or official review."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Find conservative reprint-equivalence candidates.")
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    args = parser.parse_args()
    print(json.dumps(build_candidates(args.resources_root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
