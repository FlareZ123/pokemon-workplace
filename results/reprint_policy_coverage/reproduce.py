from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_policy_coverage import summarize_reprint_policy_coverage

summary = summarize_reprint_policy_coverage(
    ROOT / "resources",
    as_of=date(2026, 10, 8),
)

assert summary["snapshot_reference_date"] == "2026-09-16"
assert summary["same_name_outside_scope_prints"] == 4260

assert summary["coverage"]["conservative"] == {
    "eligible": 0,
    "ineligible": 67,
    "unresolved": 4193,
    "total": 4260,
}
assert summary["coverage"]["current_semantic_evidence"] == {
    "eligible": 166,
    "ineligible": 67,
    "unresolved": 4027,
    "total": 4260,
}

current = summary["kinds_by_policy"]["current_semantic_evidence"]
assert current["eligible"] == {
    "exact_fingerprint_candidate": 119,
    "official_errata_candidate": 44,
    "official_semantic_candidate": 3,
}
assert current["ineligible"] == {"known_non_equivalent": 67}
assert current["unresolved"] == {
    "historical_official_reprint_candidate": 39,
    "semantic_review": 3988,
}

print("reprint policy coverage regression passed")
print("current semantic eligible:", summary["coverage"]["current_semantic_evidence"]["eligible"])
print("current semantic unresolved:", summary["coverage"]["current_semantic_evidence"]["unresolved"])
