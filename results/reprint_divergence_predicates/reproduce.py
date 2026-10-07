from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_divergence_predicates import (
    summarize_benchmark_exclusion_predicates,
)

RESOURCES = ROOT / "resources"
summary = summarize_benchmark_exclusion_predicates(RESOURCES)

assert summary["counts"] == {
    "benchmark_rows_with_explicit_exclusions": 5,
    "overridden_by_name_wide_errata": 3,
    "reachable_current_divergence": 2,
    "currently_unwitnessed": 0,
    "distinct_reachable_predicates": 1,
    "distinct_reachable_witness_cards": 1,
}

rows = summary["rows"]
assert {row["source_card_id"] for row in rows} == {
    "ex11-90",
    "ex16-77",
    "ex5-90",
    "ex6-92",
    "ex6-93",
}

reachable = [
    row for row in rows if row["status"] == "reachable_current_divergence"
]
assert {row["source_card_id"] for row in reachable} == {"ex5-90", "ex6-93"}
assert {row["name"] for row in reachable} == {"Life Herb"}
assert {row["predicate"] for row in reachable} == {"target is Pokémon-ex"}
assert all(set(row["current_target_print_ids"]) == {"sm7-136", "sm7-180"} for row in reachable)
assert all(row["witness_card_ids"] == ["me55c-108"] for row in reachable)

overridden = [
    row for row in rows if row["status"] == "overridden_by_name_wide_errata"
]
assert {row["source_card_id"] for row in overridden} == {
    "ex11-90",
    "ex16-77",
    "ex6-92",
}
assert {row["name"] for row in overridden} == {"Great Ball"}

print("reprint divergence predicates: PASS")
print("explicit exclusion rows:", summary["counts"]["benchmark_rows_with_explicit_exclusions"])
print("reachable current divergences:", len(reachable))
print("predicate:", reachable[0]["predicate"])
print("witness:", reachable[0]["witness_card_ids"][0])
