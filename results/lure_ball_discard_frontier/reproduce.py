from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.lure_ball_discard_frontier import exhaustive_comparison
from tools.reprint_errata_resolution import build_reprint_resolver

resolver = build_reprint_resolver(ROOT / "resources")
old = resolver.cards_by_id["ecard3-128"]
new = resolver.cards_by_id["sm7-138"]
assert old["name"] == new["name"] == "Lure Ball"
assert old["_set_id"] not in resolver.expanded_sets
assert new["_set_id"] in resolver.expanded_sets
assert "Flip 3 coins" in old["rules"][0] and "Flip 3 coins" in new["rules"][0]
assert "Evolution card from your discard pile" in old["rules"][0]
assert "Evolution Pokémon from your discard pile" in new["rules"][0]
assert resolver.resolve("ecard3-128").kind == "semantic_review"

summary = exhaustive_comparison()
assert summary["source_states"] == 28
assert summary["conditional_outcomes"] == 2012
assert summary["histories_by_evolution_targets"] == {
    0: 8, 1: 8, 2: 15, 3: 34, 4: 73, 5: 136, 6: 229
}
print("Lure Ball conditional frontiers: PASS")
print(summary)
