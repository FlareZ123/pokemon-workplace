"""Physical-print and source-data regression for duplicated Tera Bench guards."""

from collections import Counter
from copy import deepcopy
from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.current_card_semantics import (
    current_semantic_fingerprint,
    normalize_current_card_semantics,
)
from tools.deck_validator import load_all_card_records
from tools.verified_tera_duplicate_rules import (
    AUDITED_DUPLICATE_TERA_PRINTS,
    CORRECT_RULES,
    DUPLICATED_RULES,
    normalize_verified_tera_duplicate_rules,
)

ROOT = Path(__file__).resolve().parents[2]
folder = ROOT / "resources" / "cards" / "en"
cards = {
    card["id"]: card
    for prefix in ("sv5", "sv6", "sv8pt5")
    for card in load_json(folder / f"{prefix}.json")
}
observed = {
    card_id
    for card_id, card in cards.items()
    if card.get("supertype") == "Pokémon"
    and card.get("rules") == DUPLICATED_RULES
}
assert observed == AUDITED_DUPLICATE_TERA_PRINTS
assert len(observed) == 24
assert Counter(card_id.split("-")[0] for card_id in observed) == {
    "sv5": 4,
    "sv6": 20,
}

records = load_all_card_records(ROOT / "resources")
for card_id in observed:
    source = cards[card_id]
    original = deepcopy(source)
    fixed = normalize_verified_tera_duplicate_rules(source)
    assert fixed["rules"] == CORRECT_RULES
    assert source == original
    assert normalize_verified_tera_duplicate_rules(fixed) == fixed
    assert normalize_current_card_semantics(source)["rules"] == CORRECT_RULES
    assert records[card_id].rules == tuple(CORRECT_RULES)
    assert "Tera" in records[card_id].subtypes

dragapult_2024 = cards["sv6-130"]
dragapult_reprint = cards["sv8pt5-73"]
assert dragapult_reprint["rules"] == CORRECT_RULES
assert current_semantic_fingerprint(dragapult_2024) == current_semantic_fingerprint(dragapult_reprint)
assert records["sv6-130"].rules == records["sv8pt5-73"].rules

for card_id in ("sv5-60", "sv6-130"):
    altered = deepcopy(cards[card_id])
    altered["rules"][-1] = "Unrelated effect"
    try:
        normalize_verified_tera_duplicate_rules(altered)
    except ValueError:
        pass
    else:
        raise AssertionError(f"Unexpected source mutation was accepted: {card_id}")

# The separate PRE Terapagos omission and SV5/6 double-entry error do not overlap.
assert "sv8pt5-92" not in AUDITED_DUPLICATE_TERA_PRINTS
assert normalize_verified_tera_duplicate_rules(cards["sv8pt5-92"]) == cards["sv8pt5-92"]

print("24 duplicated Tera Bench-rule print repairs: PASS")
print("counts:", dict(sorted(Counter(k.split("-")[0] for k in observed).items())))
print("cross-set Dragapult ex normalized fingerprint: PASS")
