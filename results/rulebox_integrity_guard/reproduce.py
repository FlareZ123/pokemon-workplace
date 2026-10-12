"""Complete snapshot rulebox check for six Pokémon rule families."""

from pathlib import Path

from tools.rulebox_integrity_audit import audit_pokemon_ruleboxes
from tools.verified_mega_prize_rules import AUDITED_DUPLICATED_RULE_PRINTS
from tools.verified_tera_duplicate_rules import AUDITED_DUPLICATE_TERA_PRINTS

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "resources" / "cards" / "en"

raw = audit_pokemon_ruleboxes(CARDS, corrected=False)
fixed = audit_pokemon_ruleboxes(CARDS, corrected=True)

assert raw.category_counts == {
    "Mega ex": 114,
    "Radiant": 16,
    "TAG TEAM": 120,
    "Tera ex": 146,
    "VMAX": 210,
    "VSTAR": 95,
}
assert fixed.category_counts == {**raw.category_counts, "Tera ex": 147}
assert len(raw.violations) == 70
assert not fixed.violations, fixed.violations

expected = {
    *((card_id, "Mega ex Prize Rule Box") for card_id in AUDITED_DUPLICATED_RULE_PRINTS),
    ("me5-115", "Mega ex Prize Rule Box"),
    *((card_id, "Tera ex Bench protection") for card_id in AUDITED_DUPLICATE_TERA_PRINTS),
}
assert set(raw.violations) == expected
assert len(expected) == 70

print("complete Rule Box metadata integrity regression: PASS")
print("after correction:", fixed.category_counts)
print("raw violations repaired:", len(raw.violations))
print("extra Tera identity recovered:", fixed.category_counts["Tera ex"] - raw.category_counts["Tera ex"])
