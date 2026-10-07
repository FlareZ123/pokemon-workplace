from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.trainer_name_reuse_divergence import (
    CASES,
    collect_proven_name_reuse_non_equivalent_ids,
    summarize_name_reuse_divergence,
)
from tools.reprint_errata_resolution import build_reprint_resolver

RESOURCES = ROOT / "resources"

summary = summarize_name_reuse_divergence(RESOURCES)
reasons = collect_proven_name_reuse_non_equivalent_ids(RESOURCES)

assert summary["counts"] == {
    "cases": 8,
    "source_prints": 16,
    "names": 8,
}
assert len(CASES) == 8
assert len(reasons) == 16

expected = {
    "Master Ball": 5,
    "Pokémon Breeder": 3,
    "Pokémon Center": 3,
    "Max Revive": 1,
    "Revive": 1,
    "Devolution Spray": 1,
    "Power Plant": 1,
    "Magnetic Storm": 1,
}
actual = {
    case.name: len(case.source_ids)
    for case in CASES
}
assert actual == expected

resolver = build_reprint_resolver(RESOURCES)
for card_id in reasons:
    assert resolver.resolve(card_id).kind == "known_non_equivalent"

assert resolver.resolve("ex11-99").kind == "known_non_equivalent"
assert resolver.resolve("base1-76").kind == "known_non_equivalent"
assert resolver.resolve("base1-85").kind == "known_non_equivalent"
assert resolver.resolve("gym2-117").kind == "known_non_equivalent"
assert resolver.resolve("base1-89").kind == "known_non_equivalent"
assert resolver.resolve("base1-72").kind == "known_non_equivalent"
assert resolver.resolve("ecard2-139").kind == "known_non_equivalent"
assert resolver.resolve("ex5-91").kind == "known_non_equivalent"

print("Trainer name-reuse divergence regression: PASS")
print(summary["counts"])
