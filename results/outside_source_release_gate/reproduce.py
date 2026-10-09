from datetime import date
from pathlib import Path

from tools.deck_legality_proof import (
    adjudicate_deck, classify_print_eligibility,
)
from tools.deck_validator import DeckEntry
from tools.legality_provenance import LegalityProvenanceIndex

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
index = LegalityProvenanceIndex.from_resources(RESOURCES)
snapshot = max(index.set_release_dates[s] for s in index.resolver.expanded_sets)
assert snapshot == date(2026, 9, 16)
assert index.set_release_dates["cel25c"] == date(2021, 10, 8)

# A card-level Expanded Legal label or functional reprint target does
# not make a *future physical print* available before its source release.
early = index.resolve("cel25c-113_A", as_of=date(2012, 1, 1))
assert early.timing_status == "before_set_release"
assert early.disposition == "outside_not_yet_released"
assert early.reprint_kind == index.resolver.resolve("cel25c-113_A").kind
assert classify_print_eligibility(
    early,
    snapshot_reference_date=snapshot,
    reprint_evidence_policy="current_semantic_evidence",
)[0] == "ineligible"

# All 25 Classic Collection print records share the same source release.
classic_ids = sorted(
    cid for cid, card in index.resolver.cards_by_id.items()
    if card["_set_id"] == "cel25c"
)
assert len(classic_ids) == 25
before = [
    index.resolve(cid, as_of=date(2021, 10, 7))
    for cid in classic_ids
]
assert all(p.disposition == "outside_not_yet_released" for p in before)
assert all(p.timing_status == "before_set_release" for p in before)
assert all(
    classify_print_eligibility(
        p, snapshot_reference_date=snapshot,
        reprint_evidence_policy="current_semantic_evidence",
    )[0] == "ineligible"
    for p in before
)

on_release = index.resolve("cel25c-113_A", as_of=date(2021, 10, 8))
assert on_release.disposition != "outside_not_yet_released"
assert on_release.timing_status is None

# The date gate also composes through whole-deck adjudication.
report = adjudicate_deck(
    [DeckEntry("bw1-1", 1), DeckEntry("cel25c-113_A", 1), DeckEntry("bw1-105", 58)],
    RESOURCES,
    as_of=date(2012, 1, 1),
    reprint_evidence_policy="current_semantic_evidence",
)
assert report.disposition == "invalid"
specific = next(p for p in report.print_proofs if p.card_id == "cel25c-113_A")
assert specific.eligibility == "ineligible"
assert specific.provenance.disposition == "outside_not_yet_released"

# Older source print still predates the same query and retains its
# ordinary reprint evidence (other policy constraints apply).
old = index.resolve("base1-96", as_of=date(2012, 1, 1))
assert old.disposition == "high_confidence_reprint_candidate"

print("outside-set source release gate: PASS")
print("Classic Collection unavailable pre-release prints:", len(classic_ids))
print("historical source:", old.disposition)
