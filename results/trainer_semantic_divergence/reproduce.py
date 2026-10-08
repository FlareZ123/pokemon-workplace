from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.trainer_semantic_divergence import (
    CASES,
    collect_proven_trainer_semantic_non_equivalent_ids,
    distinguishing_witnesses,
    summarize_trainer_semantic_divergence,
)
from tools.reprint_errata_resolution import build_reprint_resolver

RESOURCES = ROOT / "resources"

summary = summarize_trainer_semantic_divergence(RESOURCES)
reasons = collect_proven_trainer_semantic_non_equivalent_ids(RESOURCES)
witnesses = distinguishing_witnesses()

assert summary["counts"] == {
    "cases": 4,
    "source_prints": 8,
    "names": 4,
}
assert len(CASES) == 4
assert len(reasons) == 8

assert {case.name: len(case.source_ids) for case in CASES} == {
    "Apricorn Maker": 1,
    "Pokémon Fan Club": 2,
    "Super Potion": 2,
    "TV Reporter": 3,
}

assert witnesses["Apricorn Maker"] == {
    "witness_card": "Ball Guy",
    "witness_subtype": "Supporter",
    "historical_eligible": True,
    "current_eligible": False,
}
assert witnesses["Pokémon Fan Club"] == {
    "historical_destination": "bench",
    "current_destination": "hand",
}
assert witnesses["Super Potion"] == {
    "starting_damage": 60,
    "historical_remaining_damage": 20,
    "current_remaining_damage": 0,
}
assert witnesses["TV Reporter"] == {
    "deck_cards": 0,
    "other_hand_cards": 1,
    "historical_changes_state": True,
    "current_playable": False,
}

resolver = build_reprint_resolver(RESOURCES)
for card_id in reasons:
    assert resolver.resolve(card_id).kind == "known_non_equivalent"

for card_id in (
    "ecard3-121",
    "ecard2-130",
    "pop4-9",
    "base1-90",
    "base4-117",
    "ex15-82",
    "ex3-88",
    "pop2-11",
):
    assert resolver.resolve(card_id).kind == "known_non_equivalent"

print("Trainer semantic divergence regression: PASS")
print(summary["counts"])
