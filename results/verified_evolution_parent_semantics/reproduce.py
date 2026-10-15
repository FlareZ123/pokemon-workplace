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
    ARCHEN_IDS,
    ARCHEN_PARENT,
    ARCHEN_SOURCE_PARENT,
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

# White Flare fossil's printed title (and Evolves-into-Archen label) supplies
# an independent official identity witness for the two misspelled parents.
white_flare = {
    c["id"]: c
    for c in load_json(ROOT / "resources" / "cards" / "en" / "rsv10pt5.json")
}
fossil = white_flare["rsv10pt5-79"]
assert fossil["name"] == ARCHEN_PARENT
assert fossil["supertype"] == "Trainer"
assert "Item" in fossil["subtypes"]
assert len(ARCHEN_IDS) == 2
for card_id in sorted(ARCHEN_IDS):
    raw = white_flare[card_id]
    original = deepcopy(raw)
    assert raw["name"] == "Archen"
    assert raw["subtypes"] == ["Stage 1"]
    assert raw["evolvesFrom"] == ARCHEN_SOURCE_PARENT
    fixed = normalize_verified_evolution_parent(raw)
    assert fixed["evolvesFrom"] == ARCHEN_PARENT
    assert normalize_verified_evolution_parent(fixed) is fixed
    assert normalize_current_card_semantics(raw)["evolvesFrom"] == ARCHEN_PARENT
    assert current_semantic_fingerprint(raw) == current_semantic_fingerprint(fixed)
    assert raw == original
    for invalid in (
        {**raw, "name": "Archeops"},
        {**raw, "evolvesFrom": "Plume Fossil"},
    ):
        try:
            normalize_verified_evolution_parent(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Archen audit allowed unexpected source data")

assert current_semantic_fingerprint(white_flare["rsv10pt5-50"]) == current_semantic_fingerprint(
    white_flare["rsv10pt5-131"]
)
print("White Flare Archen physical evolution parents: PASS")
print("30th Celebration Zoroark exact-print evolution parent: PASS")
print("Raw source parent: missing; verified parent:", normalized["evolvesFrom"])
print("Current-semantic fingerprint:", current_semantic_fingerprint(zoroark))
