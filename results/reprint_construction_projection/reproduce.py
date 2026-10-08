from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_construction_projection import audit_construction_projection

rows = audit_construction_projection(ROOT / "resources")
by_id = {row.source_card_id: row for row in rows}

expected_ids = {
    "base1-71",
    "base4-101",
    "ex8-88",
    "ex11-99",
    "ex16-78",
    "ecard1-143",
    "gym2-116",
    "neo4-106",
}
assert set(by_id) == expected_ids
assert Counter(row.name for row in rows) == {
    "Computer Search": 2,
    "Master Ball": 5,
    "Shining Celebi": 1,
}

for card_id in ("base1-71", "base4-101"):
    row = by_id[card_id]
    assert row.resolution_kind == "semantic_review"
    assert row.divergent_resolver_target_ids == ("bw7-137",)

for card_id in ("ex8-88", "ex11-99", "ex16-78", "ecard1-143", "gym2-116"):
    row = by_id[card_id]
    assert row.resolution_kind == "known_non_equivalent"
    assert row.resolver_target_ids == ()

celebi = by_id["neo4-106"]
assert celebi.resolution_kind == "exact_fingerprint_candidate"
assert "me55c-106" in celebi.resolver_target_ids
assert celebi.divergent_resolver_target_ids == ()

print("reprint construction projection regression passed")
print("name-level hazard prints:", len(rows))
print("resolver-target divergence:", sum(bool(row.divergent_resolver_target_ids) for row in rows))
