from datetime import date
from pathlib import Path

from tools.deck_legality_proof import (
    classify_print_eligibility, adjudicate_deck,
)
from tools.deck_validator import DeckEntry
from tools.legality_provenance import LegalityProvenanceIndex

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
index = LegalityProvenanceIndex.from_resources(RESOURCES)
snapshot = max(
    index.set_release_dates[set_id]
    for set_id in index.resolver.expanded_sets
)
assert snapshot == date(2026, 9, 16)

before = index.resolve("xy6-77", as_of=date(2014, 1, 1))
assert before.direct_status == "Banned"
assert before.timing_status == "before_set_release"
assert before.disposition == "direct_not_yet_released"
assert classify_print_eligibility(
    before, snapshot_reference_date=snapshot, reprint_evidence_policy="conservative"
)[0] == "ineligible"

after_release = index.resolve("xy6-77", as_of=date(2016, 1, 1))
assert after_release.timing_status == "post_release_not_audited"
assert after_release.disposition == "direct_banned"
assert classify_print_eligibility(
    after_release, snapshot_reference_date=snapshot, reprint_evidence_policy="conservative"
)[0] == "unresolved"

current = index.resolve("xy6-77", as_of=date(2026, 10, 9))
assert current.disposition == "direct_banned"
assert classify_print_eligibility(
    current, snapshot_reference_date=snapshot, reprint_evidence_policy="conservative"
)[0] == "ineligible"

historical = adjudicate_deck(
    [DeckEntry("bw1-1", 1), DeckEntry("xy6-77", 1), DeckEntry("bw1-105", 58)],
    RESOURCES,
    as_of=date(2014, 1, 1),
)
assert historical.disposition == "invalid"
proof = next(x for x in historical.print_proofs if x.card_id == "xy6-77")
assert proof.eligibility == "ineligible"
assert proof.provenance.disposition == "direct_not_yet_released"

print("unreleased banned-print priority: PASS")
print("2014:", before.disposition)
print("2016:", after_release.disposition)
print("2026:", current.disposition)
