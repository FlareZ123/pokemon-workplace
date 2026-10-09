from __future__ import annotations
from collections import Counter
from pathlib import Path
from tools.build_expanded_legality_baseline import load_json
from tools.reprint_errata_resolution import build_reprint_resolver

def audit_outside_set_expanded_flags(resources_root: Path) -> dict[str, object]:
    resolver = build_reprint_resolver(resources_root)
    flagged = []
    for card_id, card in sorted(resolver.cards_by_id.items()):
        if card["_set_id"] in resolver.expanded_sets:
            continue
        if (card.get("legalities") or {}).get("expanded") != "Legal":
            continue
        resolution = resolver.resolve(card_id)
        flagged.append({
            "id": card_id,
            "name": card["name"],
            "set_id": card["_set_id"],
            "kind": resolution.kind,
            "evidence": resolution.evidence_source,
        })
    counts = Counter(row["kind"] for row in flagged)
    conflicts = [r for r in flagged if r["kind"] == "known_non_equivalent"]
    unresolved = [
        r for r in flagged
        if r["kind"] in {"semantic_review", "historical_official_reprint_candidate"}
    ]
    return {
        "flagged_prints": len(flagged),
        "flagged_sets": len({r["set_id"] for r in flagged}),
        "kinds": dict(sorted(counts.items())),
        "known_negative_conflicts": conflicts,
        "still_unresolved": unresolved,
        "records": flagged,
    }
