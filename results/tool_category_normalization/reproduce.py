from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.build_expanded_legality_baseline import load_json
from tools.tool_category_normalization import (
    LEGACY_ITEM_RULES,
    normalize_legacy_tool_category,
    summarize_legacy_tool_normalization,
)

RESOURCES = ROOT / "resources"
summary = summarize_legacy_tool_normalization(RESOURCES)
counts = summary["counts"]

assert counts["legal_expanded_prints"] == 14829
assert counts["changed_tool_prints"] == 213
assert counts["changed_tool_names"] == 168
assert counts["dual_item_tool_prints"] == 30
assert counts["obsolete_item_rule_prints"] == 213
assert counts["raw_legal_gameplay_fingerprints"] == 10416
assert counts["normalized_legal_gameplay_fingerprints"] == 10416
assert summary["changed_by_series"] == {
    "Black & White": 22,
    "Sun & Moon": 62,
    "Sword & Shield": 69,
    "XY": 60,
}
assert summary["obsolete_item_rule_phrases"] == {
    "You may play any number of Item cards during your turn.": 69,
    "You may play as many Item cards as you like during your turn (before your attack).": 144,
}

cards = {}
for path in sorted((RESOURCES / "cards" / "en").glob("*.json")):
    for raw in load_json(path):
        cards[raw["id"]] = raw

forest_seal = normalize_legacy_tool_category(cards["swsh12-156"])
assert forest_seal["subtypes"] == ["Pokémon Tool"]
assert not any(rule in LEGACY_ITEM_RULES for rule in forest_seal["rules"])

rapid_scroll = normalize_legacy_tool_category(cards["swsh7-153"])
assert rapid_scroll["subtypes"] == ["Rapid Strike", "Pokémon Tool"]
assert not any(rule in LEGACY_ITEM_RULES for rule in rapid_scroll["rules"])

non_tool = normalize_legacy_tool_category(cards["sv3-191"])
assert non_tool == cards["sv3-191"]

print("legacy Pokemon Tool category normalization: PASS")
print("changed Tool prints:", counts["changed_tool_prints"])
print("affected names:", counts["changed_tool_names"])
print("dual Item + Tool prints:", counts["dual_item_tool_prints"])
print("distinct legal fingerprints:", counts["normalized_legal_gameplay_fingerprints"])
