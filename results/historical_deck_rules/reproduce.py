from pathlib import Path

from tools.arceus_unlimited_reprint_divergence import collect_arceus_rule_non_equivalent_ids
from tools.deck_validator import (
    DeckEntry, UNLIMITED_SELF_RULE, UNOWN_FAMILY_RULE,
    load_all_card_records, validate_deck_construction,
)
from tools.reprint_errata_resolution import build_reprint_resolver

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
GRASS = "bw1-105"
SNIVY = "bw1-1"


def error_codes(*entries):
    report = validate_deck_construction(
        [DeckEntry(card_id, quantity) for card_id, quantity in entries],
        RESOURCES,
    )
    return {issue.code for issue in report.issues if issue.severity == "error"}


cards = load_all_card_records(RESOURCES)
assert sum(UNLIMITED_SELF_RULE in c.rules for c in cards.values()) == 15
assert sum(UNOWN_FAMILY_RULE in c.rules for c in cards.values()) == 26
assert not error_codes(("pl4-AR1", 5), (GRASS, 55))
assert not error_codes(("pl4-94", 5), (SNIVY, 1), (GRASS, 54))
assert "name_copy_limit" in error_codes(("xyp-XY83", 5), (GRASS, 55))
assert not error_codes(("neo2-14", 2), ("neo3-39", 2), (GRASS, 56))
assert "unown_family_limit" in error_codes(
    ("neo2-14", 2), ("neo3-39", 3), (GRASS, 55)
)
sources = collect_arceus_rule_non_equivalent_ids(RESOURCES)
assert set(sources) == {"dpp-DP50"} | {f"pl4-AR{i}" for i in range(1, 10)}
resolver = build_reprint_resolver(RESOURCES)
assert all(resolver.resolve(card_id).kind == "known_non_equivalent" for card_id in sources)
assert resolver.resolve("pl4-94").kind == "no_expanded_counterpart"
print("historical construction and Arceus reprint: PASS")
print("Arceus rule-divergent historical prints:", len(sources))
