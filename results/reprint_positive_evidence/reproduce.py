from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_errata_resolution import build_reprint_resolver
from tools.reprint_positive_evidence import (
    EXPLICIT_POSITIVE_SOURCE_ID,
    EXPLICIT_POSITIVE_TARGET_ID,
    collect_known_equivalent_ids,
    summarize_positive_reprint_evidence,
)

RESOURCES = ROOT / "resources"
summary = summarize_positive_reprint_evidence(RESOURCES)

assert summary["counts"] == {
    "official_semantic_candidate_prints": 3,
    "names": 1,
}
assert summary["prints_by_name"] == {"Copycat": 3}
assert summary["card_ids"] == ["ecard1-138", "ex15-73", "ex7-83"]
assert summary["explicit_target_id"] == "sm7-127"
assert EXPLICIT_POSITIVE_SOURCE_ID == "ex7-83"
assert EXPLICIT_POSITIVE_TARGET_ID == "sm7-127"
assert len(collect_known_equivalent_ids(RESOURCES)) == 3

resolver = build_reprint_resolver(RESOURCES)
for card_id in summary["card_ids"]:
    row = resolver.resolve(card_id)
    assert row.kind == "official_semantic_candidate"
    assert row.target_print_ids == ("sm7-127",)

assert resolver.resolve("col1-77").kind == "semantic_review"
assert resolver.resolve("hgss1-90").kind == "semantic_review"

print("current-handbook positive reprint evidence: PASS")
print("official semantic candidates:", summary["card_ids"])
print("explicit legal target:", summary["explicit_target_id"])
