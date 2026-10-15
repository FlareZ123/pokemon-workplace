"""Test historical Maintenance against current XY Item text."""

from copy import deepcopy
from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.maintenance_shuffle_equivalence import exhaustively_compare
from tools.current_card_semantics import current_semantic_fingerprint, normalize_current_card_semantics
from tools.maintenance_current_semantics import (
    CURRENT_RULE,
    LEGACY_RULE,
    normalize_historical_maintenance,
)

ROOT = Path(__file__).resolve().parents[2]
by_id = {}
for set_id in ("base1", "base4", "g1", "xy3", "xy12"):
    for card in load_json(ROOT / "resources" / "cards" / "en" / f"{set_id}.json"):
        by_id[card["id"]] = card

historical = ("base1-83", "base4-112")
xy = ("xy3-96", "xy12-79")
for card_id in historical + xy:
    assert by_id[card_id]["name"] == "Maintenance"
    assert by_id[card_id]["supertype"] == "Trainer"

for card_id in historical:
    c = by_id[card_id]
    assert c.get("subtypes") is None
    assert c["rules"] == [
        "Shuffle 2 of the other cards from your hand into your deck in order to draw a card."
    ]

for card_id in xy:
    c = by_id[card_id]
    assert c["subtypes"] == ["Item"]
    assert c["rules"][0] == (
        "Shuffle 2 cards from your hand into your deck. "
        "(If you can't shuffle 2 cards into your deck, you can't play this card.) "
        "Then, draw a card."
    )

# Keep the legal modern XY print as the canonical semantic target.
expected = current_semantic_fingerprint(by_id["xy3-96"])
assert current_semantic_fingerprint(by_id["xy12-79"]) == expected
for card_id in historical:
    raw = by_id[card_id]
    untouched = deepcopy(raw)
    normalized = normalize_historical_maintenance(raw)
    assert normalized["subtypes"] == ["Item"]
    assert normalized["rules"] == [CURRENT_RULE]
    assert normalize_historical_maintenance(normalized) is normalized
    assert current_semantic_fingerprint(raw) == expected
    assert normalize_current_card_semantics(raw)["subtypes"] == ["Item"]
    assert raw == untouched
    for mutation in (
        {**raw, "name": "Scoop Up"},
        {**raw, "rules": ["Shuffle one card from hand."]},
        {**raw, "subtypes": ["Supporter"]},
    ):
        try:
            normalize_historical_maintenance(mutation)
        except ValueError:
            pass
        else:
            raise AssertionError("Unknown old Maintenance source mutation accepted")

assert normalize_historical_maintenance(by_id["xy3-96"]) is by_id["xy3-96"]
assert LEGACY_RULE == by_id["base1-83"]["rules"][0]

summary = exhaustively_compare()
assert summary["worlds"] == 24
assert summary["playable_worlds"] == 16
assert summary["conditional_outcomes"] > 0
print("Maintenance historical/current action-frontier equivalence: PASS")
print(summary)
