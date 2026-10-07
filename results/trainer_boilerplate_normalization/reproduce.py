from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.build_expanded_legality_baseline import gameplay_fingerprint, load_json
from tools.trainer_boilerplate_normalization import (
    normalize_trainer_boilerplate,
    summarize_trainer_boilerplate,
)

RESOURCES = ROOT / "resources"
summary = summarize_trainer_boilerplate(RESOURCES)
counts = summary["counts"]

assert counts == {
    "archive_changed_prints": 1801,
    "archive_changed_names": 760,
    "archive_item_changed_prints": 656,
    "archive_supporter_changed_prints": 1145,
    "legal_expanded_prints": 14829,
    "legal_changed_prints": 1646,
    "legal_changed_names": 670,
    "legal_item_changed_prints": 647,
    "legal_supporter_changed_prints": 999,
    "raw_legal_gameplay_fingerprints": 10416,
    "normalized_legal_gameplay_fingerprints": 10389,
    "legal_fingerprint_reduction": 27,
    "legal_merge_groups": 26,
}

assert summary["archive_rule_counts"] == {
    "You can play only 1 Supporter card each turn. When you play this card, put it next to your Active Pokémon. When your turn ends, discard this card.": 6,
    "You can play only one Supporter card each turn. When you play this card, put it next to your Active Pokémon. When your turn ends, discard this card.": 125,
    "You may play any number of Item cards during your turn.": 318,
    "You may play as many Item cards as you like during your turn (before your attack).": 338,
    "You may play only 1 Supporter card during your turn.": 671,
    "You may play only 1 Supporter card during your turn (before your attack).": 343,
}

assert "Copycat" in summary["legal_merge_names"]
assert "Switch" in summary["legal_merge_names"]
assert "Crushing Hammer" in summary["legal_merge_names"]

cards = {}
for path in sorted((RESOURCES / "cards" / "en").glob("*.json")):
    for raw in load_json(path):
        cards[raw["id"]] = raw

copycat_sm = normalize_trainer_boilerplate(cards["sm7-127"])
copycat_swsh = normalize_trainer_boilerplate(cards["swsh7-143"])
assert gameplay_fingerprint(copycat_sm) == gameplay_fingerprint(copycat_swsh)

switch_bw = normalize_trainer_boilerplate(cards["bw1-104"])
switch_sv = normalize_trainer_boilerplate(cards["sv1-194"])
assert gameplay_fingerprint(switch_bw) == gameplay_fingerprint(switch_sv)

charon = normalize_trainer_boilerplate(cards["pl2-RT6"])
assert "put this card into your hand instead of discarding it" in charon["rules"][0]

print("Trainer boilerplate normalization audit: PASS")
print("archive changed prints:", counts["archive_changed_prints"])
print("legal changed prints:", counts["legal_changed_prints"])
print("legal fingerprint reduction:", counts["legal_fingerprint_reduction"])
print("legal merge groups:", counts["legal_merge_groups"])
