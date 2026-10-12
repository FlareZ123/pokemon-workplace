"""Regression for the omitted Tera subtype and Bench protection of PRE Terapagos."""

from copy import deepcopy
from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.current_card_semantics import current_semantic_fingerprint
from tools.deck_validator import load_all_card_records
from tools.verified_tera_metadata_repairs import (
    EX_RULE,
    NEW_SUBTYPES,
    TERA_RULE,
    normalize_verified_tera_metadata,
)

ROOT = Path(__file__).resolve().parents[2]
cards = {
    card["id"]: card
    for card in load_json(ROOT / "resources" / "cards" / "en" / "sv8pt5.json")
}
original = cards["sv8pt5-92"]
reference = cards["sv8pt5-169"]
alternate = cards["sv8pt5-180"]

assert original["subtypes"] == ["Basic", "ex"]
assert original["rules"] == [EX_RULE]
assert reference["subtypes"] == list(NEW_SUBTYPES)
assert reference["rules"] == [TERA_RULE, EX_RULE]
assert alternate["subtypes"] == list(NEW_SUBTYPES)
assert alternate["rules"] == [TERA_RULE, EX_RULE]

expected = current_semantic_fingerprint(reference)
assert current_semantic_fingerprint(alternate) == expected

partial_subtype = deepcopy(original)
partial_subtype["subtypes"] = list(NEW_SUBTYPES)
partial_rule = deepcopy(original)
partial_rule["rules"] = [TERA_RULE, EX_RULE]

for card in (original, partial_subtype, partial_rule, reference):
    corrected = normalize_verified_tera_metadata(card)
    assert corrected["subtypes"] == list(NEW_SUBTYPES)
    assert corrected["rules"] == [TERA_RULE, EX_RULE]
    assert normalize_verified_tera_metadata(corrected) == corrected
    assert current_semantic_fingerprint(card) == expected

records = load_all_card_records(ROOT / "resources")
record = records["sv8pt5-92"]
assert "Tera" in record.subtypes
assert record.rules == (TERA_RULE, EX_RULE)
assert records["sv8pt5-169"].subtypes == record.subtypes
assert records["sv8pt5-180"].rules == record.rules

# Area Zero Underdepths checks whether a player has any Tera Pokémon in play.
stadium = cards["sv8pt5-94"]
assert "any Tera Pokémon in play" in stadium["rules"][0]
assert ("Tera" in original["subtypes"]) is False
assert "Tera" in record.subtypes

assert original["subtypes"] == ["Basic", "ex"]
assert original["rules"] == [EX_RULE]
assert normalize_verified_tera_metadata(alternate) == alternate

print("Prismatic Evolutions Terapagos ex Tera metadata: PASS")
print("Fingerprint-matched printings: sv8pt5-92, sv8pt5-169, sv8pt5-180")
print("Area Zero Tera predicate on corrected #92:", "Tera" in record.subtypes)
