from pathlib import Path
from tools.outside_set_expanded_flag_audit import audit_outside_set_expanded_flags

ROOT = Path(__file__).resolve().parents[2]
report = audit_outside_set_expanded_flags(ROOT / "resources")
assert report["flagged_prints"] == 243
assert sum(report["kinds"].values()) == 243
negative_ids = {r["id"] for r in report["known_negative_conflicts"]}
assert {"ex15-82", "ex3-88", "pop2-11", "hgss1-96"}.issubset(negative_ids)
assert report["still_unresolved"]

print("outside-set Expanded flag audit: PASS")
print("print count:", report["flagged_prints"])
print("distinct sets:", report["flagged_sets"])
print("resolver evidence classes:", report["kinds"])
print("negative conflicts:", len(negative_ids))
for row in report["known_negative_conflicts"]:
    print(" conflict", row["id"], row["name"], row["kind"])
print("unresolved:", len(report["still_unresolved"]))
