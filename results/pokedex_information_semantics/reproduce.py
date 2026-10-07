from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.pokedex_information_semantics import (
    current_pokedex_witnesses,
    legacy_pokedex_witnesses,
    observation_counts_by_outcome,
    physical_outcomes,
    summarize_distinct_prefix,
)

for size in range(1, 6):
    summary = summarize_distinct_prefix(size)
    assert summary["physical_outcomes_equal"] is True
    assert summary["legacy_physical_outcomes"] == summary["expected_physical_outcomes"]
    assert summary["current_physical_outcomes"] == summary["expected_physical_outcomes"]
    if size == 1:
        assert summary["legacy_outcomes_with_lower_information_witness"] == 0
    else:
        assert summary["legacy_outcomes_with_lower_information_witness"] > 0

five = tuple("ABCDE")
legacy = legacy_pokedex_witnesses(five)
current = current_pokedex_witnesses(five)
assert len(legacy) == 153
assert len(current) == 120
assert len(physical_outcomes(legacy)) == 120
assert physical_outcomes(legacy) == physical_outcomes(current)

unchanged = five
legacy_counts = observation_counts_by_outcome(legacy)[unchanged]
current_counts = observation_counts_by_outcome(current)[unchanged]
assert legacy_counts == frozenset({1, 2, 3, 4, 5})
assert current_counts == frozenset({5})

assert summarize_distinct_prefix(5)["legacy_outcomes_with_lower_information_witness"] == 24

print("Pokédex physical/epistemic semantics regression passed")
