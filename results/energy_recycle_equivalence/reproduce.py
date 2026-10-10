from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.energy_recycle_equivalence import exhaustively_compare
from tools.reprint_errata_resolution import build_reprint_resolver

resolver = build_reprint_resolver(ROOT / "resources")
sources = ("ex3-84", "ex10-81", "ex16-73")
target = resolver.cards_by_id["sm7-128"]

assert target["name"] == "Energy Recycle System"
assert "Item" in (target.get("subtypes") or [])
assert target["_set_id"] in resolver.expanded_sets
assert any("Choose 1:" in rule for rule in target.get("rules") or ())
assert any("Shuffle 3 basic Energy cards" in rule for rule in target.get("rules") or ())

for source_id in sources:
    source = resolver.cards_by_id[source_id]
    assert source["name"] == target["name"]
    assert "Item" in (source.get("subtypes") or [])
    assert source["_set_id"] not in resolver.expanded_sets
    assert any("show 1 basic Energy card" in rule for rule in source.get("rules") or ())
    assert any("show 3 basic Energy cards" in rule for rule in source.get("rules") or ())
    # Preserve the present-day conservative classification until a separate
    # review decides how to incorporate this model into positive evidence.
    assert resolver.resolve(source_id).kind == "semantic_review"

census = exhaustively_compare()
assert census["worlds"] == 108
assert census["conditional_outcomes"] > 108
print("Energy Recycle System action-frontier equivalence: PASS")
print("Historical source IDs:", ", ".join(sources))
print("Exhaustive distinct-card worlds:", census["worlds"])
print("Conditional physical outcomes:", census["conditional_outcomes"])
