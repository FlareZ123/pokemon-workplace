from __future__ import annotations

from pathlib import Path

from tools.build_expanded_legality_baseline import classify_effective_legality, load_json
from tools.reprint_policy_evidence import HANDBOOK_SOURCE

UNLIMITED = "You may have as many of this card in your deck as you like."


def collect_arceus_rule_non_equivalent_ids(resources_root: Path) -> dict[str, str]:
    """Identify historical Arceus whose copy-limit text differs from legal targets."""
    expanded_sets = {
        row["id"] for row in load_json(resources_root / "sets" / "en.json")
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }
    sources: list[dict] = []
    targets: list[dict] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for card in load_json(path):
            if card["name"] != "Arceus":
                continue
            if path.stem in expanded_sets:
                if classify_effective_legality(card)[0] == "Legal":
                    targets.append(card)
            elif UNLIMITED in (card.get("rules") or ()):
                sources.append(card)
    if not sources or not targets:
        raise ValueError("Expected historical unlimited and legal Expanded Arceus")
    if any(UNLIMITED in (c.get("rules") or ()) for c in targets):
        raise ValueError("A legal Expanded Arceus has the historical unlimited rule")
    if any("Basic" not in (c.get("subtypes") or ()) for c in sources + targets):
        raise ValueError("Compared Arceus prints must be Basic")
    reason = (
        "Deck-rule divergence: historical Arceus permits any number of that "
        "printed card, while legal Expanded same-name Arceus prints have the "
        "ordinary four-copy maximum. Five copies of one historical print "
        "distinguish the deck-construction rules. Current reprint policy "
        f"requires functionally identical printed text: {HANDBOOK_SOURCE}"
    )
    return dict.fromkeys(sorted(c["id"] for c in sources), reason)
