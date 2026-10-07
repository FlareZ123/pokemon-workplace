from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.trainer_boilerplate_candidate_audit import (
    audit_boilerplate_candidate_delta,
)

summary = audit_boilerplate_candidate_delta(ROOT / "resources")
assert summary["counts"]["known_negative_collisions"] == 0

print("Trainer boilerplate candidate delta probe: PASS")
print(json.dumps(summary["counts"], sort_keys=True))
print(json.dumps(summary["new_exact_by_name"], sort_keys=True))
for row in summary["rows"]:
    print(json.dumps(row, sort_keys=True))
