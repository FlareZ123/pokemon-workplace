from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.deck_legality_proof import adjudicate_deck
from tools.deck_validator import DeckEntry

RESOURCES = ROOT / "resources"
GRASS = "bw1-105"
SNIVY = "bw1-1"


def deck(*entries, as_of=date(2026, 10, 8)):
    return adjudicate_deck(
        [DeckEntry(card_id, qty) for card_id, qty in entries],
        RESOURCES,
        as_of=as_of,
    )


def proof(report, card_id):
    return next(row for row in report.print_proofs if row.card_id == card_id)


current = deck((SNIVY, 1), (GRASS, 59))
assert current.disposition == "eligible_snapshot"
assert current.construction.valid
assert current.snapshot_reference_date == date(2026, 9, 16)

waiting = deck(
    (SNIVY, 1),
    ("me55c-106", 1),
    (GRASS, 58),
    as_of=date(2026, 9, 29),
)
assert waiting.disposition == "invalid"
assert proof(waiting, "me55c-106").eligibility == "ineligible"
assert proof(waiting, "me55c-106").provenance.disposition == "direct_release_waiting"

candidate = deck((SNIVY, 1), ("ex7-83", 1), (GRASS, 58))
assert candidate.disposition == "unresolved"
assert proof(candidate, "ex7-83").eligibility == "unresolved"
assert proof(candidate, "ex7-83").provenance.reprint_kind == "official_semantic_candidate"

review = deck((SNIVY, 1), ("base1-87", 1), (GRASS, 58))
assert review.disposition == "unresolved"
assert proof(review, "base1-87").provenance.disposition == "semantic_review"

negative = deck((SNIVY, 1), ("base5-17", 1), (GRASS, 58))
assert negative.disposition == "invalid"
assert proof(negative, "base5-17").eligibility == "ineligible"
assert proof(negative, "base5-17").provenance.disposition == "known_non_equivalent"

computer_search = deck((SNIVY, 1), ("base1-71", 1), (GRASS, 58))
assert computer_search.disposition == "invalid"
assert proof(computer_search, "base1-71").eligibility == "ineligible"
assert proof(computer_search, "base1-71").provenance.disposition == "known_non_equivalent"

banned = deck((SNIVY, 1), ("xy6-77", 1), (GRASS, 58))
assert banned.disposition == "invalid"
assert proof(banned, "xy6-77").provenance.disposition == "direct_banned"

historical = deck(
    (SNIVY, 1),
    (GRASS, 59),
    as_of=date(2012, 1, 1),
)
assert historical.disposition == "unresolved"
assert proof(historical, SNIVY).eligibility == "unresolved"

copy_rule = deck(("me55c-106", 2), (GRASS, 58))
assert copy_rule.disposition == "invalid"
assert any(
    issue.code == "self_named_singleton_limit"
    for issue in copy_rule.construction.issues
)

historical_copy_rule = deck(("neo4-106", 2), (GRASS, 58))
assert historical_copy_rule.disposition == "invalid"
assert any(
    issue.code == "self_named_singleton_limit"
    for issue in historical_copy_rule.construction.issues
)

unknown = deck((SNIVY, 1), ("does-not-exist", 1), (GRASS, 58))
assert unknown.disposition == "invalid"
assert proof(unknown, "does-not-exist").eligibility == "ineligible"
assert any(issue.code == "unknown_print" for issue in unknown.construction.issues)

print("deck legality proof regression passed")
