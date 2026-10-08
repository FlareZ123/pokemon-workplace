from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_deck_rule_divergence import (
    ACE_SPEC_RULE,
    collect_proven_deck_rule_non_equivalent_ids,
    summarize_deck_rule_divergence,
)

RESOURCES = ROOT / "resources"
summary = summarize_deck_rule_divergence(RESOURCES)
reasons = collect_proven_deck_rule_non_equivalent_ids(RESOURCES)

assert summary["counts"] == {
    "cases": 1,
    "source_prints": 2,
    "names": 1,
}
assert set(reasons) == {"base1-71", "base4-101"}
case = summary["cases"][0]
assert case["name"] == "Computer Search"
assert case["target_id"] == "bw7-137"
assert case["axis"] == "rule_category"
assert case["missing_source_rule"] == ACE_SPEC_RULE
assert "two Computer Search cards" in case["witness"]

print("reprint deck-rule divergence: PASS")
print("source prints:", sorted(reasons))
print("target:", case["target_id"])
