"""Archive-wide regression for same-combat, same-set print metadata drift."""

from pathlib import Path

from tools.same_set_print_anomalies import find_same_set_print_anomalies

ROOT = Path(__file__).resolve().parents[2]
cards_root = ROOT / "resources" / "cards" / "en"

raw = find_same_set_print_anomalies(cards_root, normalize=False)
corrected = find_same_set_print_anomalies(cards_root, normalize=True)

raw_ids = {(issue.set_id, issue.name): issue.print_ids for issue in raw}
corrected_ids = {(issue.set_id, issue.name): issue.print_ids for issue in corrected}

assert raw_ids == {
    ("me5", "Mega Chandelure ex"): ("me5-115", "me5-38", "me5-99"),
    ("sv8pt5", "Terapagos ex"): ("sv8pt5-169", "sv8pt5-180", "sv8pt5-92"),
    ("svp", "Charizard ex"): ("svp-56", "svp-74"),
}
assert corrected_ids == {
    ("svp", "Charizard ex"): ("svp-56", "svp-74")
}

# Both Charizard physical prints already agree on the Tera subtype; the
# surviving difference is merely the "Tera:" label on the same guard text.
charizard, = corrected
assert len(charizard.subtype_variants) == 1
assert len(charizard.rule_variants) == 2
variants = charizard.rule_variants
assert len(variants[0]) == len(variants[1]) == 2
assert sorted(tuple(rule.removeprefix("Tera: ") for rule in rules) for rules in variants)[0] == sorted(tuple(rule.removeprefix("Tera: ") for rule in rules) for rules in variants)[1]

print("same-set gameplay-variant metadata guard: PASS")
print("raw candidate families:", sorted(raw_ids))
print("remaining explicitly reviewed cosmetic family:", sorted(corrected_ids))
