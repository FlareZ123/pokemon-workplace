from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.audit_set_fallback_legality import audit
result = audit(ROOT / "resources", as_of=date(2026, 10, 7))

assert result["fallback_print_count"] == 191
assert result["fallback_sets"] == [
    {
        "set_id": "me55",
        "set_name": "30th Celebration",
        "release_date": "2026-09-16",
        "nominal_two_week_date": "2026-09-30",
        "print_count": 161,
    },
    {
        "set_id": "me55c",
        "set_name": "30th Celebration: Classic Collection",
        "release_date": "2026-09-16",
        "nominal_two_week_date": "2026-09-30",
        "print_count": 30,
    },
]
assert result["all_past_nominal_two_week_date"]
assert all(row["unlimited_status"] == "Legal" for row in result["rows"])

print("set-fallback legality audit: PASS")
print("fallback prints:", result["fallback_print_count"])
print("sets:", ", ".join(row["set_id"] for row in result["fallback_sets"]))
