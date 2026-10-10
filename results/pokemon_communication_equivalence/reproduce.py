from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.pokemon_communication_equivalence import verify
from tools.reprint_errata_resolution import build_reprint_resolver

resolver = build_reprint_resolver(ROOT / "resources")
old = resolver.cards_by_id["hgss1-98"]
bw = resolver.cards_by_id["bw1-99"]
sm = resolver.cards_by_id["sm9-152"]
assert all(c["name"] == "Pokémon Communication" for c in (old, bw, sm))
assert all("Item" in c.get("subtypes", ()) for c in (old, bw, sm))
assert "show it to your opponent" in old["rules"][0]
assert "on top of your deck" in bw["rules"][0]
assert "into your deck" in sm["rules"][0]
assert resolver.resolve("hgss1-98").kind == "semantic_review"
assert verify() == (54, 1854)
print("Pokémon Communication bounded operational equivalence: PASS")
