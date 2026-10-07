from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    has_tournament_ban_rule,
    load_json,
)
from tools.reprint_policy_evidence import HANDBOOK_PAIR_EVIDENCE, MAJOR_NAME_ERRATA


def analyze(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    cards: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    by_fingerprint: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards.append(card)
            by_id[card["id"]] = card
            by_fingerprint[gameplay_fingerprint(card)].append(card)

    legal_expanded_names: set[str] = set()
    legal_expanded_ids: set[str] = set()
    for card in cards:
        if card["_set_id"] not in expanded_sets:
            continue
        status, _source = classify_effective_legality(card)
        if status == "Legal":
            legal_expanded_names.add(card["name"])
            legal_expanded_ids.add(card["id"])

    def source_print_allowed(card: dict[str, Any]) -> bool:
        if card["_set_id"] in expanded_sets:
            return False
        if has_tournament_ban_rule(card):
            return False
        if (card.get("legalities") or {}).get("unlimited") == "Banned":
            return False
        return True

    errata_candidates = sorted(
        (
            {
                "id": card["id"],
                "name": card["name"],
                "set_id": card["_set_id"],
                "supertype": card.get("supertype"),
            }
            for card in cards
            if source_print_allowed(card)
            and card["name"] in MAJOR_NAME_ERRATA
            and card["name"] in legal_expanded_names
        ),
        key=lambda row: row["id"],
    )

    handbook_positive: list[dict[str, Any]] = []
    handbook_negative: list[dict[str, Any]] = []
    for evidence in HANDBOOK_PAIR_EVIDENCE:
        left = by_id[evidence.left_print_id]
        right = by_id[evidence.right_print_id]
        left_fp = gameplay_fingerprint(left)
        right_fp = gameplay_fingerprint(right)
        if evidence.relation == "equivalent":
            if right["id"] not in legal_expanded_ids:
                continue
            for card in by_fingerprint[left_fp]:
                if source_print_allowed(card) and card["name"] == right["name"]:
                    handbook_positive.append(
                        {
                            "id": card["id"],
                            "name": card["name"],
                            "set_id": card["_set_id"],
                            "source_example": [evidence.left_print_id, evidence.right_print_id],
                            "old_fingerprint": left_fp,
                            "legal_fingerprint": right_fp,
                        }
                    )
        else:
            for card in by_fingerprint[left_fp]:
                if source_print_allowed(card) and card["name"] == right["name"]:
                    handbook_negative.append(
                        {
                            "id": card["id"],
                            "name": card["name"],
                            "set_id": card["_set_id"],
                            "source_example": [evidence.left_print_id, evidence.right_print_id],
                            "old_fingerprint": left_fp,
                            "legal_fingerprint": right_fp,
                        }
                    )

    handbook_positive.sort(key=lambda row: row["id"])
    handbook_negative.sort(key=lambda row: row["id"])

    positive_ids = {row["id"] for row in errata_candidates}
    positive_ids.update(row["id"] for row in handbook_positive)

    return {
        "errata_candidates": errata_candidates,
        "handbook_positive_variant_candidates": handbook_positive,
        "handbook_negative_variant_examples": handbook_negative,
        "counts": {
            "errata_candidate_prints": len(errata_candidates),
            "errata_candidate_names": len({row["name"] for row in errata_candidates}),
            "handbook_positive_variant_prints": len(handbook_positive),
            "handbook_negative_variant_prints": len(handbook_negative),
            "combined_semantic_candidate_prints": len(positive_ids),
        },
        "interpretation": (
            "These are policy-evidence candidates for reprint resolution. Name-level errata and "
            "handbook examples provide stronger semantic evidence than raw name matching, while "
            "the explicit Rainbow Energy counterexample guards against treating same-name text "
            "changes as automatically equivalent."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit errata and handbook reprint evidence.")
    parser.add_argument("--resources-root", type=Path, default=Path("resources"))
    args = parser.parse_args()
    print(json.dumps(analyze(args.resources_root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
