"""Reproduce historical VS Seeker public-discard semantic comparison."""

from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.vs_seeker_public_discard_equivalence import exhaustively_compare

ROOT = Path(__file__).resolve().parents[2]
by_id = {}
for set_id in ("ex6", "pl3", "xy4", "xy6"):
    for card in load_json(ROOT / "resources" / "cards" / "en" / f"{set_id}.json"):
        by_id[card["id"]] = card

historical = ("ex6-100", "pl3-140")
current = ("xy4-109", "xy6-110")
for card_id in historical + current:
    c = by_id[card_id]
    assert c["name"] == "VS Seeker"
    assert c["supertype"] == "Trainer"
    assert c["subtypes"] == ["Item"]

for card_id in historical:
    rules = by_id[card_id]["rules"]
    assert len(rules) == 1
    assert rules[0] == (
        "Search your discard pile for a Supporter card, show it to your "
        "opponent, and put it into your hand."
    )

for card_id in current:
    rules = by_id[card_id]["rules"]
    assert rules[0] == "Put a Supporter card from your discard pile into your hand."

summary = exhaustively_compare()
assert summary["worlds"] == 32766
assert summary["playable_worlds"] > 0
assert summary["conditional_outcomes"] > summary["playable_worlds"]
print("VS Seeker historical/current public-discard frontier: PASS")
print(summary)
