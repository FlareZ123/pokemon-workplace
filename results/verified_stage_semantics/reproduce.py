"""Regression for audited source-data corrections across semantic fingerprints."""

from copy import deepcopy
from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.current_card_semantics import (
    current_semantic_fingerprint,
    normalize_current_card_semantics,
)
from tools.verified_stage_metadata_repairs import (
    CHAND_RULE,
    normalize_verified_stage_metadata,
)

ROOT = Path(__file__).resolve().parents[2]
cards = {
    card["id"]: card
    for card in load_json(ROOT / "resources" / "cards" / "en" / "me5.json")
}

mankey = cards["me5-42"]
special = cards["me5-115"]
ordinary = cards["me5-38"]
alternate = cards["me5-99"]

assert not mankey.get("subtypes")
assert special["subtypes"] == ["MEGA", "ex"]
assert not special.get("rules")

fixed_mankey = normalize_current_card_semantics(mankey)
assert fixed_mankey["subtypes"] == ["Basic"]
assert normalize_current_card_semantics(fixed_mankey) == fixed_mankey
assert mankey.get("subtypes") is None

target_fingerprint = current_semantic_fingerprint(ordinary)
assert current_semantic_fingerprint(alternate) == target_fingerprint

partial_stage = deepcopy(special)
partial_stage["subtypes"] = ["Stage 2", "MEGA", "ex"]
partial_rule = deepcopy(special)
partial_rule["rules"] = [CHAND_RULE]
complete = deepcopy(partial_stage)
complete["rules"] = [CHAND_RULE]

for source in (special, partial_stage, partial_rule, complete):
    corrected = normalize_verified_stage_metadata(source)
    assert corrected["subtypes"] == ["Stage 2", "MEGA", "ex"]
    assert corrected["rules"] == [CHAND_RULE]
    assert normalize_verified_stage_metadata(corrected) == corrected
    assert current_semantic_fingerprint(source) == target_fingerprint

assert special["subtypes"] == ["MEGA", "ex"]
assert not special.get("rules")

unrelated = deepcopy(ordinary)
assert normalize_current_card_semantics(unrelated) == normalize_current_card_semantics(ordinary)

print("verified stage/current fingerprint bridge: PASS")
print("Mega Chandelure ex print variants:", "me5-38", "me5-99", "me5-115")
print("Mankey Basic stage corrected:", fixed_mankey["subtypes"])
