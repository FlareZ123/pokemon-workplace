"""Enumerate current unresolved old-print Trainer same-name reprint cases."""

import json
from collections import Counter, defaultdict
from pathlib import Path

from tools.reprint_errata_resolution import build_reprint_resolver

ROOT = Path(__file__).resolve().parents[2]
resolver = build_reprint_resolver(ROOT / "resources")
same_name = [
    resolver.resolve(card_id)
    for card_id, card in resolver.cards_by_id.items()
    if card["_set_id"] not in resolver.expanded_sets
    and card.get("supertype") == "Trainer"
    and card["name"] in resolver.legal_expanded_by_name
]
by_kind = Counter(row.kind for row in same_name)
review = [row for row in same_name if row.kind == "semantic_review"]
by_name = defaultdict(list)
for row in review:
    by_name[row.name].append(row.card_id)

assert len(same_name) == 168
assert by_kind["semantic_review"] == 21
assert by_kind["known_non_equivalent"] == 35
assert sum(by_kind.values()) == 168
print("Old-print Trainer semantic frontier: PASS")
print("Total same-name historical Trainer prints:", len(same_name))
print("Resolver partition:", json.dumps(dict(sorted(by_kind.items())), ensure_ascii=True))
for name, ids in sorted(by_name.items()):
    targets = sorted(c["id"] for c in resolver.legal_expanded_by_name[name])
    print(json.dumps({
        "name": name,
        "historical_print_ids": sorted(ids),
        "expanded_target_print_ids": targets,
    }, ensure_ascii=True))
