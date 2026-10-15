"""Official-print-backed 30th Celebration Zoroark evolution parent repair."""

from copy import deepcopy
from pathlib import Path

from tools.build_expanded_legality_baseline import gameplay_fingerprint, load_json
from tools.current_card_semantics import (
    current_semantic_fingerprint,
    normalize_current_card_semantics,
)
from tools.verified_evolution_parent_repairs import (
    CARD_ID,
    PARENT,
    normalize_verified_evolution_parent,
)

ROOT = Path(__file__).resolve().parents[2]
cards = load_json(ROOT / "resources" / "cards" / "en" / "me55.json")
by_id = {card["id"]: card for card in cards}
zoroark = by_id[CARD_ID]
assert zoroark["name"] == "Zoroark"
assert zoroark["subtypes"] == ["Stage 1"]
assert "evolvesFrom" not in zoroark
assert PARENT == "Zorua"

raw_snapshot = deepcopy(zoroark)
normalized = normalize_verified_evolution_parent(zoroark)
assert normalized["evolvesFrom"] == PARENT
assert normalized["abilities"] == zoroark["abilities"]
assert zoroark == raw_snapshot
assert normalize_verified_evolution_parent(normalized) is normalized
assert normalize_current_card_semantics(zoroark)["evolvesFrom"] == PARENT
assert current_semantic_fingerprint(zoroark) == current_semantic_fingerprint(normalized)
assert gameplay_fingerprint(normalized) != gameplay_fingerprint(
    {**normalized, "evolvesFrom": "Hisuian Zorua"}
)

other_stage_1 = next(c for c in cards if c["id"] != CARD_ID and "Stage 1" in (c.get("subtypes") or []))
assert normalize_verified_evolution_parent(other_stage_1) is other_stage_1

for changed in (
    {**zoroark, "name": "Hisuian Zoroark"},
    {**zoroark, "evolvesFrom": "Hisuian Zorua"},
    {**zoroark, "subtypes": ["Basic"]},
):
    try:
        normalize_verified_evolution_parent(changed)
    except ValueError:
        pass
    else:
        raise AssertionError("Unrecognized Zoroark source mutation accepted")

assert len([c for c in cards if c.get("id") == CARD_ID]) == 1
print("30th Celebration Zoroark exact-print evolution parent: PASS")
print("Raw source parent: missing; verified parent:", normalized["evolvesFrom"])
print("Current-semantic fingerprint:", current_semantic_fingerprint(zoroark))
