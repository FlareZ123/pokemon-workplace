from pathlib import Path

from tools.basic_switch_rule_semantics import (
    SWITCH_CURRENT, SWITCH_OLD,
    ENERGY_SWITCH_CURRENT, ENERGY_SWITCH_OLD, ENERGY_SWITCH_OLD_MISSING_TO,
    normalize_basic_switch_wording,
)
from tools.build_expanded_legality_baseline import load_json
from tools.current_card_semantics import current_semantic_fingerprint
from tools.reprint_errata_resolution import build_reprint_resolver, summarize_reprint_resolver

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
cards = {}
changed_ids = []
for path in sorted((RESOURCES / "cards" / "en").glob("*.json")):
    for card in load_json(path):
        cards[card["id"]] = card
        normalized = normalize_basic_switch_wording(card)
        if normalized != card:
            changed_ids.append(card["id"])
            assert normalized["name"] == card["name"]
            assert normalized["rules"] != card["rules"]
            assert normalize_basic_switch_wording(normalized) == normalized

expected_changed = {
    "ex1-92", "ex15-83", "hgss1-102", "ex11-102",
    "ex6-102", "dp1-119", "dp3-128", "dp7-93",
    "ex16-75", "ex10-84", "ex1-82", "hgss1-91",
    "ex6-90", "dp1-107", "dp7-84",
}
assert set(changed_ids) == expected_changed, set(changed_ids) ^ expected_changed
assert len(changed_ids) == 15

assert cards["hgss1-102"]["rules"] == [SWITCH_OLD]
assert cards["hgss1-91"]["rules"] == [ENERGY_SWITCH_OLD_MISSING_TO]
assert cards["ex16-75"]["rules"] == [ENERGY_SWITCH_OLD]
assert cards["bw1-104"]["rules"][0] == SWITCH_CURRENT
assert cards["bw1-94"]["rules"][0] == ENERGY_SWITCH_CURRENT

assert current_semantic_fingerprint(cards["hgss1-102"]) == current_semantic_fingerprint(cards["bw1-104"])
assert current_semantic_fingerprint(cards["hgss1-91"]) == current_semantic_fingerprint(cards["bw1-94"])
assert cards["hgss1-91"]["rules"] == [ENERGY_SWITCH_OLD_MISSING_TO]

resolver = build_reprint_resolver(RESOURCES)
assert resolver.resolve("hgss1-102").kind == "exact_fingerprint_candidate"
assert resolver.resolve("hgss1-91").kind == "exact_fingerprint_candidate"
assert resolver.resolve("ecard2-120").kind == "historical_official_reprint_candidate"
assert resolver.resolve("base1-95").kind == "historical_official_reprint_candidate"
assert resolver.resolve("bw1-104").kind == "direct_legal"
assert resolver.resolve("bw1-94").kind == "direct_legal"

counts = summarize_reprint_resolver(resolver)["counts"]
assert counts["exact_fingerprint_candidate_prints"] == 149
assert counts["historical_official_reprint_candidate_prints"] == 26
assert counts["semantic_review_prints"] == 3961
assert counts["high_confidence_candidate_prints"] == 222
print("rules-grounded basic Switch and Energy Switch equivalence: PASS")
print("changed source prints:", len(changed_ids))
print("new matches:", {"Switch": "hgss1-102", "Energy Switch": "hgss1-91"})
print("resolver exact:", counts["exact_fingerprint_candidate_prints"])
