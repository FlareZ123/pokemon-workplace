from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.attack_empty_field_normalization import audit_empty_attack_field_matches
from tools.reprint_errata_resolution import build_reprint_resolver

RESOURCES = ROOT / "resources"
rows = audit_empty_attack_field_matches(RESOURCES)
by_id = {row.source_card_id: row for row in rows}

assert set(by_id) == {
    "base1-58",
    "base4-87",
    "ex7-19",
    "hgss4-99",
    "hgss4-100",
    "neo4-106",
    "pl2-112",
    "pop2-16",
}

assert by_id["neo4-106"].target_card_ids == ("me55c-106",)
assert by_id["ex7-19"].target_card_ids == ("me55c-19",)
assert set(by_id["hgss4-99"].target_card_ids) == {"me55c-99", "me55c-100"}

resolver = build_reprint_resolver(RESOURCES)
for card_id in by_id:
    assert resolver.resolve(card_id).kind == "exact_fingerprint_candidate"

print("empty attack-field normalization regression passed")
print("promoted source prints:", len(rows))
print("source ids:", sorted(by_id))
