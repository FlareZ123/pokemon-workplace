"""Shared validated card-data normalization boundary regression."""

from copy import deepcopy
from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.current_card_semantics import normalize_current_card_semantics
from tools.deck_validator import load_all_card_records
from tools.verified_card_metadata import (
    AUDITED_CARD_METADATA_IDS,
    normalize_verified_card_metadata,
)
from tools.verified_stage_metadata_repairs import KNOWN_STAGE_REPAIRS
from tools.verified_tera_metadata_repairs import CARD_ID as TERAPAGOS_TERA_PRINT_ID
from tools.verified_mega_prize_rules import AUDITED_DUPLICATED_RULE_PRINTS
from tools.verified_tera_duplicate_rules import AUDITED_DUPLICATE_TERA_PRINTS
from tools.verified_evolution_parent_repairs import AUDITED_EVOLUTION_PARENT_PRINTS

ROOT = Path(__file__).resolve().parents[2]
subsets = (
    set(KNOWN_STAGE_REPAIRS),
    {TERAPAGOS_TERA_PRINT_ID},
    set(AUDITED_DUPLICATED_RULE_PRINTS),
    set(AUDITED_DUPLICATE_TERA_PRINTS),
    set(AUDITED_EVOLUTION_PARENT_PRINTS),
)
assert list(map(len, subsets)) == [2, 1, 45, 24, 3]
assert sum(map(len, subsets)) == len(set.union(*subsets)) == len(AUDITED_CARD_METADATA_IDS) == 75

cards = {}
for set_id in ("me5", "me2pt5", "me3", "sv5", "sv6", "sv8pt5", "me55", "rsv10pt5"):
    for card in load_json(ROOT / "resources" / "cards" / "en" / f"{set_id}.json"):
        cards[card["id"]] = card

assert all(card_id in cards for card_id in AUDITED_CARD_METADATA_IDS)
records = load_all_card_records(ROOT / "resources")
for card_id in AUDITED_CARD_METADATA_IDS:
    source = cards[card_id]
    untouched = deepcopy(source)
    normalized = normalize_verified_card_metadata(source)
    assert normalized == normalize_verified_card_metadata(normalized)
    assert source == untouched
    assert records[card_id].subtypes == tuple(normalized.get("subtypes") or ())
    assert records[card_id].rules == tuple(normalized.get("rules") or ())
    current = normalize_current_card_semantics(source)
    assert current.get("subtypes") == normalized.get("subtypes")
    assert current.get("rules") == normalized.get("rules")
    assert current.get("evolvesFrom") == normalized.get("evolvesFrom")

unrelated = cards["me2pt5-11"]
assert unrelated["id"] not in AUDITED_CARD_METADATA_IDS
assert normalize_verified_card_metadata(unrelated) is unrelated

print("single verified-card metadata correction boundary: PASS")
print("audited IDs:", len(AUDITED_CARD_METADATA_IDS))
print("proof-family sizes:", list(map(len, subsets)))
