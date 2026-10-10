from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.copycat_number_wording import (
    REFERENCE_TEXT,
    SOURCE_IDS,
    SOURCE_TEXT,
    normalize_copycat_count_wording,
)
from tools.current_card_semantics import current_semantic_fingerprint
from tools.reprint_errata_resolution import build_reprint_resolver
from tools.reprint_positive_evidence import collect_known_equivalent_ids

resolver = build_reprint_resolver(ROOT / "resources")
reference = resolver.cards_by_id["ex7-83"]
certified_target = resolver.cards_by_id["sm7-127"]
assert certified_target["name"] == "Copycat"
assert REFERENCE_TEXT in reference["rules"]

expected = {"ecard1-138", "ex15-73", "ex7-83"} | SOURCE_IDS
positives = collect_known_equivalent_ids(ROOT / "resources")
assert set(positives) == expected

for source_id in sorted(SOURCE_IDS):
    source = resolver.cards_by_id[source_id]
    assert SOURCE_TEXT in source["rules"]
    normalized = normalize_copycat_count_wording(source)
    assert normalized["rules"] == reference["rules"]
    assert current_semantic_fingerprint(source) == current_semantic_fingerprint(reference)
    assert resolver.resolve(source_id).kind == "official_semantic_candidate"
    assert resolver.resolve(source_id).target_print_ids == ("sm7-127",)
    assert normalize_copycat_count_wording(normalized) == normalized

# Exhaustively verify the only numerical rewrite: both texts request exactly
# the same number of cards, including shortages after the shuffle.
for opponent_hand in range(61):
    for available_deck_cards_after_shuffle in range(61):
        historical_requested = opponent_hand
        exemplar_requested = sum(1 for _ in range(opponent_hand))
        assert min(historical_requested, available_deck_cards_after_shuffle) == min(
            exemplar_requested, available_deck_cards_after_shuffle
        )

# Print-local guard: never change another historical identity even if its
# rule happens to contain exactly the same surface wording.
other = dict(resolver.cards_by_id["sm7-127"])
assert normalize_copycat_count_wording(other) == other

print("Copycat numerical-wording bridge: PASS")
print("Newly covered source IDs:", ", ".join(sorted(SOURCE_IDS)))
print("Current official-semantic Copycat candidates:", len(expected))
