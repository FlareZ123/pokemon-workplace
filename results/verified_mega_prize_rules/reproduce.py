"""Source-grounded regression for 45 incorrectly duplicated generic ex rules."""

from collections import Counter
from copy import deepcopy
from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.current_card_semantics import (
    current_semantic_fingerprint,
    normalize_current_card_semantics,
)
from tools.deck_validator import load_all_card_records
from tools.verified_mega_prize_rules import (
    AUDITED_DUPLICATED_RULE_PRINTS,
    EX_TWO_PRIZE_RULE,
    MEGA_THREE_PRIZE_RULE,
    normalize_verified_mega_prize_rules,
)

ROOT = Path(__file__).resolve().parents[2]
CARDS = ROOT / "resources" / "cards" / "en"
records = load_all_card_records(ROOT / "resources")
source = {
    c["id"]: c
    for set_name in ("me1", "me2", "me2pt5", "me3", "me4", "me5")
    for c in load_json(CARDS / f"{set_name}.json")
    if c.get("supertype") == "Pokémon"
    and {"MEGA", "ex"}.issubset(set(c.get("subtypes") or ()))
}

observed_bad = {
    card_id
    for card_id, card in source.items()
    if card.get("rules") == [EX_TWO_PRIZE_RULE, MEGA_THREE_PRIZE_RULE]
}
assert len(observed_bad) == 45
assert observed_bad == AUDITED_DUPLICATED_RULE_PRINTS
assert Counter(card_id.split("-")[0] for card_id in observed_bad) == {
    "me2pt5": 33,
    "me3": 12,
}

for card_id, card in source.items():
    before = deepcopy(card)
    corrected = normalize_verified_mega_prize_rules(card)
    assert card == before, f"source was mutated: {card_id}"
    assert normalize_verified_mega_prize_rules(corrected) == corrected

    if card_id in observed_bad:
        assert corrected["rules"] == [MEGA_THREE_PRIZE_RULE]
        assert normalize_current_card_semantics(card)["rules"] == [MEGA_THREE_PRIZE_RULE]
        assert records[card_id].rules == (MEGA_THREE_PRIZE_RULE,)
        assert EX_TWO_PRIZE_RULE not in records[card_id].rules
        assert card["rules"] == [EX_TWO_PRIZE_RULE, MEGA_THREE_PRIZE_RULE]
    elif card_id != "me5-115":
        assert corrected == card, f"unrelated Mega print modified: {card_id}"

assert records["me1-60"].rules == (MEGA_THREE_PRIZE_RULE,)
assert records["me2pt5-89"].rules == records["me1-60"].rules
assert current_semantic_fingerprint(source["me2pt5-89"]) == current_semantic_fingerprint(source["me1-60"])

# Guard against changing real rule text or subtype semantics under an old ID.
changed_text = deepcopy(source["me2pt5-89"])
changed_text["rules"][0] = "Unexpected other effect"
try:
    normalize_verified_mega_prize_rules(changed_text)
except ValueError:
    pass
else:
    raise AssertionError("changed source rules were silently accepted")

changed_stage = deepcopy(source["me3-47"])
changed_stage["subtypes"] = ["Basic", "ex"]
try:
    normalize_verified_mega_prize_rules(changed_stage)
except ValueError:
    pass
else:
    raise AssertionError("changed Mega identity was silently accepted")

# Existing deck print still gets one 3-Prize liability, ordinary ex remains 2.
assert len(records["me3-47"].rules) == 1
assert records["me3-47"].rules[0] == MEGA_THREE_PRIZE_RULE

print("audited Mega ex Rule Box corrections: PASS")
print("affected current prints:", len(observed_bad))
print("set distribution:", dict(sorted(Counter(x.split("-")[0] for x in observed_bad).items())))
print("example physical rule:", records["me2pt5-89"].rules)
