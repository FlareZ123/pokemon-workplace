from pathlib import Path

from tools.build_expanded_legality_baseline import gameplay_fingerprint, load_json
from tools.current_card_semantics import current_semantic_fingerprint
from tools.independent_mega_ex_rule_order import (
    EX_RULE, MEGA_RULE, normalize_independent_mega_ex_rules,
)
from tools.reprint_errata_resolution import build_reprint_resolver

ROOT = Path(__file__).resolve().parents[2]
RESOURCES = ROOT / "resources"
cards: dict[str, dict] = {}
rule_order_ids: dict[str, list[str]] = {
    "canonical": [],
    "reversed": [],
}
for path in sorted((RESOURCES / "cards" / "en").glob("*.json")):
    for card in load_json(path):
        cards[card["id"]] = card
        if (card.get("rules") or []) == [MEGA_RULE, EX_RULE]:
            rule_order_ids["canonical"].append(card["id"])
        elif (card.get("rules") or []) == [EX_RULE, MEGA_RULE]:
            rule_order_ids["reversed"].append(card["id"])

assert len(rule_order_ids["canonical"]) == 85
assert rule_order_ids["reversed"] == ["cel25c-76_A"]
older = cards["xy6-76"]
newer = cards["cel25c-76_A"]
assert older["name"] == newer["name"] == "M Rayquaza-EX"
assert gameplay_fingerprint(older) != gameplay_fingerprint(newer)
assert normalize_independent_mega_ex_rules(older) is older
normalized = normalize_independent_mega_ex_rules(newer)
assert normalized["rules"] == older["rules"]
assert normalized is not newer
assert newer["rules"] == [EX_RULE, MEGA_RULE]
assert normalize_independent_mega_ex_rules(normalized) is normalized
assert current_semantic_fingerprint(older) == current_semantic_fingerprint(newer)

resolver = build_reprint_resolver(RESOURCES)
resolved = resolver.resolve("cel25c-76_A")
assert resolved.kind == "exact_fingerprint_candidate"
assert "xy6-76" in resolved.target_print_ids
assert resolver.resolve("xy6-76").kind == "direct_legal"

print("independent XY Mega/EX rule-order semantic normalization: PASS")
print("canonical pair print count:", len(rule_order_ids["canonical"]))
print("reversed pair:", rule_order_ids["reversed"])
print("reprint state:", resolved.kind)
