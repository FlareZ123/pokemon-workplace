from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.historical_reprint_evidence import NO_REFERENCE_REPRINTS
from tools.pokeball_restored_counterexample import search_option_sets
from tools.reprint_errata_resolution import build_reprint_resolver

r = build_reprint_resolver(ROOT / "resources")
old_ids = ("base2-64", "base4-121", "ex1-86", "ex6-95", "ex10-87", "ex14-82")
assert set(old_ids).issubset(NO_REFERENCE_REPRINTS["Poké Ball"])
for id in old_ids:
    assert "Basic Pokémon or Evolution card" in r.cards_by_id[id]["rules"][0]
    assert r.resolve(id).kind == "historical_official_reprint_candidate"
assert "search your deck for a Pokémon" in r.cards_by_id["bw1-97"]["rules"][0]

restored = [c for c in r.cards_by_id.values() if c["_set_id"] in r.expanded_sets and "Restored" in (c.get("subtypes") or ())]
assert len(restored) == 13
basic, evo = r.cards_by_id["bw1-1"], r.cards_by_id["bw1-3"]
for fossil in restored:
    assert r.resolve(fossil["id"]).kind == "direct_legal"
    narrow, broad = search_option_sets((basic, evo, fossil))
    assert narrow == frozenset(("bw1-1", "bw1-3"))
    assert broad == narrow | {fossil["id"]}
    assert search_option_sets((fossil,)) == (frozenset(), frozenset((fossil["id"],)))
print("Poké Ball target-domain witnesses: PASS",len(old_ids)*len(restored))
