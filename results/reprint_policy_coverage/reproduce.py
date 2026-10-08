from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_errata_resolution import build_reprint_resolver, summarize_reprint_resolver
from tools.reprint_policy_coverage import summarize_reprint_policy_coverage

RESOURCES = ROOT / "resources"
resolver_summary = summarize_reprint_resolver(build_reprint_resolver(RESOURCES))
resolver_counts = resolver_summary["counts"]

summary = summarize_reprint_policy_coverage(
    RESOURCES,
    as_of=date(2026, 10, 8),
)

assert summary["snapshot_reference_date"] == "2026-09-16"
assert summary["same_name_outside_scope_prints"] == resolver_counts["same_name_review_pool_prints"]

conservative = summary["coverage"]["conservative"]
assert conservative["eligible"] == 0
assert conservative["ineligible"] == resolver_counts["known_non_equivalent_prints"]
assert conservative["unresolved"] == (
    resolver_counts["same_name_review_pool_prints"]
    - resolver_counts["known_non_equivalent_prints"]
)

current = summary["coverage"]["current_semantic_evidence"]
assert current["eligible"] == (
    resolver_counts["exact_fingerprint_candidate_prints"]
    + resolver_counts["official_errata_candidate_prints"]
    + resolver_counts["official_semantic_candidate_prints"]
)
assert current["ineligible"] == resolver_counts["known_non_equivalent_prints"]
assert current["unresolved"] == (
    resolver_counts["historical_official_reprint_candidate_prints"]
    + resolver_counts["semantic_review_prints"]
)
assert current["total"] == resolver_counts["same_name_review_pool_prints"]

current_kinds = summary["kinds_by_policy"]["current_semantic_evidence"]
assert current_kinds["eligible"] == {
    "exact_fingerprint_candidate": resolver_counts["exact_fingerprint_candidate_prints"],
    "official_errata_candidate": resolver_counts["official_errata_candidate_prints"],
    "official_semantic_candidate": resolver_counts["official_semantic_candidate_prints"],
}
assert current_kinds["ineligible"] == {
    "known_non_equivalent": resolver_counts["known_non_equivalent_prints"]
}
assert current_kinds["unresolved"] == {
    "historical_official_reprint_candidate": resolver_counts[
        "historical_official_reprint_candidate_prints"
    ],
    "semantic_review": resolver_counts["semantic_review_prints"],
}

print("reprint policy coverage regression passed")
print("current semantic eligible:", current["eligible"])
print("current semantic ineligible:", current["ineligible"])
print("current semantic unresolved:", current["unresolved"])
