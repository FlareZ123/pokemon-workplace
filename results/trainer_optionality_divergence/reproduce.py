from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.trainer_optionality_divergence import (
    CASES,
    collect_proven_optionality_non_equivalent_ids,
    summarize_optionality_divergence,
)
from tools.reprint_errata_resolution import build_reprint_resolver

RESOURCES = ROOT / "resources"

summary = summarize_optionality_divergence(RESOURCES)
reasons = collect_proven_optionality_non_equivalent_ids(RESOURCES)

assert summary["counts"] == {
    "cases": 3,
    "source_prints": 6,
    "names": 3,
}
assert len(CASES) == 3
assert len(reasons) == 6

expected = {
    "PokéNav": 3,
    "Pokégear 3.0": 1,
    "Dusk Ball": 2,
}
assert {case.name: len(case.source_ids) for case in CASES} == expected

resolver = build_reprint_resolver(RESOURCES)
for card_id in reasons:
    assert resolver.resolve(card_id).kind == "known_non_equivalent"

assert resolver.resolve("ex1-88").kind == "known_non_equivalent"
assert resolver.resolve("hgss1-96").kind == "known_non_equivalent"
assert resolver.resolve("dp2-110").kind == "known_non_equivalent"

print("Trainer optionality divergence regression: PASS")
print(summary["counts"])
