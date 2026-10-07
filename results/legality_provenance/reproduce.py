from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.legality_provenance import LegalityProvenanceIndex

index = LegalityProvenanceIndex.from_resources(ROOT / "resources")

before = index.resolve("me55c-106", as_of=date(2026, 9, 29))
assert before.disposition == "direct_release_waiting"
assert before.timing_status == "audited_waiting_period"
assert before.ordinary_legal_date == date(2026, 9, 30)
assert before.direct_status == "Legal"
assert before.direct_status_source == "set_fallback"

on_date = index.resolve("me55c-106", as_of=date(2026, 9, 30))
assert on_date.disposition == "direct_legal_release_verified"
assert on_date.timing_status == "audited_release_eligible"

pre_ban = index.resolve("swsh7-83", as_of=date(2026, 4, 9))
assert pre_ban.disposition == "direct_legal_snapshot_timing_unverified"
assert pre_ban.direct_status == "Legal"
assert pre_ban.direct_status_source == "database_pre_overlay"

on_ban = index.resolve("swsh7-83", as_of=date(2026, 4, 10))
assert on_ban.disposition == "direct_banned"
assert on_ban.direct_status == "Banned"
assert on_ban.direct_status_source == "official_overlay"

ordinary = index.resolve("bw5-100", as_of=date(2026, 10, 7))
assert ordinary.disposition == "direct_legal_snapshot_timing_unverified"
assert ordinary.reprint_kind == "direct_legal"

banned = index.resolve("xy6-77", as_of=date(2026, 10, 7))
assert banned.disposition == "direct_banned"
assert banned.reprint_kind == "direct_banned"

for card_id, kind in {
    "ecard3-125": "exact_fingerprint_candidate",
    "pl1-108": "exact_fingerprint_candidate",
    "ex7-83": "official_semantic_candidate",
    "base1-96": "historical_official_reprint_candidate",
    "dp4-99": "official_errata_candidate",
}.items():
    row = index.resolve(card_id, as_of=date(2026, 10, 7))
    assert row.disposition == "high_confidence_reprint_candidate"
    assert row.reprint_kind == kind
    assert row.target_evidence

negative = index.resolve("ex5-90", as_of=date(2026, 10, 7))
assert negative.disposition == "known_non_equivalent"
assert negative.reprint_kind == "known_non_equivalent"

review = index.resolve("base1-87", as_of=date(2026, 10, 7))
assert review.disposition == "semantic_review"
assert review.reprint_kind == "semantic_review"
assert review.regional_legality_scope == "not_evaluated"

print("legality provenance regression passed")
