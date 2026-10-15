"""Exact cross-language correction manifest regeneration regression."""

import json
from pathlib import Path

from tools.export_verified_card_metadata import (
    build_metadata_patch_manifest,
    manifest_json,
)
from tools.verified_card_metadata import AUDITED_CARD_METADATA_IDS

ROOT = Path(__file__).resolve().parents[2]
manifest_file = ROOT / "results" / "verified_card_metadata_boundary" / "overrides.json"
actual_text = manifest_file.read_text(encoding="utf-8")
actual = json.loads(actual_text)
expected = build_metadata_patch_manifest(ROOT / "resources")

assert actual == expected
assert list(actual["patches"]) == sorted(AUDITED_CARD_METADATA_IDS)
assert len(actual["patches"]) == 73
assert actual_text == manifest_json(ROOT / "resources")

summary = {
    key: sum(print_id.startswith(key + "-") for print_id in actual["patches"])
    for key in ("me2pt5", "me3", "me5", "me55", "sv5", "sv6", "sv8pt5")
}
assert summary == {
    "me2pt5": 33,
    "me3": 12,
    "me5": 2,
    "me55": 1,
    "sv5": 4,
    "sv6": 20,
    "sv8pt5": 1,
}

print("verified source metadata manifest regenerated exactly: PASS")
print("Audited print count:", len(actual["patches"]))
print("Set distribution:", summary)
