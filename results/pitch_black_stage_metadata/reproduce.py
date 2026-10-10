from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.verified_stage_metadata_repairs import (
    CHAND_RULE,
    KNOWN_STAGE_REPAIRS,
    normalize_verified_stage_metadata,
)
from tools.build_expanded_legality_baseline import gameplay_fingerprint
from tools.reprint_errata_resolution import build_reprint_resolver

resolver = build_reprint_resolver(ROOT / "resources")
assert set(KNOWN_STAGE_REPAIRS) == {"me5-42", "me5-115"}
for card_id in KNOWN_STAGE_REPAIRS:
    original = resolver.cards_by_id[card_id]
    corrected = normalize_verified_stage_metadata(original)
    assert corrected != original
    assert normalize_verified_stage_metadata(corrected) == corrected
    assert resolver.resolve(card_id).kind == "direct_legal"

mankey = normalize_verified_stage_metadata(resolver.cards_by_id["me5-42"])
assert mankey["subtypes"] == ["Basic"]
assert mankey["name"] == "Mankey" and mankey["hp"] == "50"

reference = resolver.cards_by_id["me5-38"]
alt = resolver.cards_by_id["me5-99"]
repaired = normalize_verified_stage_metadata(resolver.cards_by_id["me5-115"])
assert repaired["subtypes"] == ["Stage 2", "MEGA", "ex"]
assert repaired["rules"] == reference["rules"] == alt["rules"] == [CHAND_RULE]
assert gameplay_fingerprint(repaired) == gameplay_fingerprint(reference)
assert gameplay_fingerprint(repaired) == gameplay_fingerprint(alt)

# No other Mega Chandelure printing needs or receives this correction.
assert normalize_verified_stage_metadata(reference) == reference
assert normalize_verified_stage_metadata(alt) == alt
print("Pitch Black stage metadata audit: PASS")
print("Guarded repairs:", ", ".join(sorted(KNOWN_STAGE_REPAIRS)))
