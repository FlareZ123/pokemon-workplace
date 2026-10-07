from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_contextual_equivalence import summarize_contextual_divergence

RESOURCES = ROOT / "resources"
summary = summarize_contextual_divergence(RESOURCES)

assert summary["counts"] == {
    "life_herb_historical_prints_with_current_divergence": 2,
    "distinct_witness_cards": 1,
}

witnesses = summary["witnesses"]
assert {row["historical_card_id"] for row in witnesses} == {"ex5-90", "ex6-93"}
assert {row["current_card_id"] for row in witnesses} == {"sm7-136"}
assert {row["witness_card_id"] for row in witnesses} == {"me55c-108"}
assert all(row["name"] == "Life Herb" for row in witnesses)
assert all("different target sets" in row["consequence"] for row in witnesses)

print("format-relative reprint divergence witness: PASS")
print("historical Life Herb printings with current divergence:", len(witnesses))
print("current target witness:", witnesses[0]["witness_card_id"])
