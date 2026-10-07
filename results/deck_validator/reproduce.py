from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.deck_validator import (
    DeckEntry,
    _recognized_copy_constraint,
    load_expanded_card_records,
    validate_deck,
)
RESOURCES = ROOT / "resources"
GRASS = "bw1-105"
SNIVY = "bw1-1"


def codes(report):
    return [issue.code for issue in report.issues if issue.severity == "error"]


def warnings(report):
    return [issue.code for issue in report.issues if issue.severity == "warning"]


def deck(*entries):
    return validate_deck(
        [DeckEntry(card_id, qty) for card_id, qty in entries],
        RESOURCES,
    )


r = deck((SNIVY, 1), (GRASS, 59))
assert r.valid and not r.issues
assert deck((SNIVY, 1), (GRASS, 58)).total_cards == 59
assert "deck_size" in codes(deck((SNIVY, 1), (GRASS, 58)))
assert "missing_basic_pokemon" in codes(deck((GRASS, 60)))

r = deck(("bw10-90", 3), ("bw5-102", 2), (SNIVY, 1), (GRASS, 54))
assert "name_copy_limit" in codes(r)
r = deck(("bw11-113", 5), (SNIVY, 1), (GRASS, 54))
assert "name_copy_limit" in codes(r)
assert deck((SNIVY, 1), (GRASS, 59)).valid

r = deck(("bw7-137", 1), ("bw8-128", 1), (SNIVY, 1), (GRASS, 57))
assert "ace_spec_limit" in codes(r)
r = deck(("pgo-4", 1), ("pgo-11", 1), (GRASS, 58))
assert "radiant_limit" in codes(r)
r = deck(("sm5-58", 2), (GRASS, 58))
assert "prism_star_name_limit" in codes(r)
r = deck(("sm5-58", 1), ("sm5-62", 1), (GRASS, 58))
assert r.valid
r = deck(("me55c-106", 2), (GRASS, 58))
assert "self_named_singleton_limit" in codes(r)
assert "set_fallback_legality" in warnings(r)
r = deck(("smp-SM79", 2), (GRASS, 58))
assert r.valid

r = deck(("xy6-77", 1), (GRASS, 59))
assert "illegal_print" in codes(r)
r = deck(("bw4-5", 1), (GRASS, 59))
assert r.valid
r = deck(("swshp-SWSH132", 1), (SNIVY, 1), (GRASS, 58))
assert "illegal_print" in codes(r)

r = deck(("does-not-exist", 1), (SNIVY, 1), (GRASS, 58))
assert "unknown_print" in codes(r)
r = validate_deck(
    [DeckEntry(SNIVY, 1), DeckEntry(GRASS, 59), DeckEntry("bw10-90", 0)],
    RESOURCES,
)
assert "invalid_quantity" in codes(r)

records = load_expanded_card_records(RESOURCES)
restriction_prints = 0
restriction_texts = set()
for record in records.values():
    if record.effective_status != "Legal":
        continue
    for rule in record.rules:
        if "can't have more than" in rule.lower() and "deck" in rule.lower():
            restriction_prints += 1
            restriction_texts.add(rule)
            assert _recognized_copy_constraint(record, rule), (
                record.card_id,
                record.name,
                rule,
            )

assert restriction_prints == 97
assert len(restriction_texts) == 5

print("deck validator regressions: PASS")
print("legal copy-limit rule prints:", restriction_prints)
print("unique recognized copy-limit rule texts:", len(restriction_texts))
