from pathlib import Path

from tools.deck_copy_rule_inventory import inventory_copy_rules
from tools.deck_validator import (
    DeckEntry, validate_deck_construction,
)

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
result = inventory_copy_rules(RESOURCES)
assert result["total_rule_prints"] == 179
assert result["classes"] == {
    "ace_spec": 53,
    "pokemon_star": 29,
    "prism_star": 27,
    "radiant": 16,
    "self_named_singleton": 13,
    "unlimited_exact_print": 15,
    "unown_family": 26,
}
assert result["unrecognized"] == []

records = {x["id"]: x["kind"] for x in result["rule_prints"]}
assert records["neo4-16"] == "self_named_singleton"
assert records["pl4-AR1"] == "unlimited_exact_print"
assert records["neo2-14"] == "unown_family"

def deck(*entries):
    return validate_deck_construction(
        [DeckEntry(card_id, quantity) for card_id, quantity in entries],
        RESOURCES,
    )

bad = deck(("neo4-16", 2), ("bw1-1", 1), ("bw1-105", 57))
assert "self_named_singleton_limit" in {
    issue.code for issue in bad.issues if issue.severity == "error"
}
assert "unrecognized_deck_constraint" not in {
    issue.code for issue in bad.issues if issue.severity == "warning"
}
good = deck(("neo4-16", 1), ("bw1-1", 1), ("bw1-105", 58))
assert good.valid
print("historical print-wide copy-rule inventory: PASS")
print("total copy-rule prints:", result["total_rule_prints"])
print("classes:", result["classes"])
