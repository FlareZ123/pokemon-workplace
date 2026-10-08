from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_negative_evidence import (
    collect_known_non_equivalent_ids,
    summarize_negative_reprint_evidence,
)
from tools.reprint_errata_resolution import build_reprint_resolver

RESOURCES = ROOT / "resources"
summary = summarize_negative_reprint_evidence(RESOURCES)

assert summary["counts"] == {
    "known_non_equivalent_prints": 64,
    "names": 19,
}
assert summary["prints_by_name"] == {
    "Apricorn Maker": 1,
    "Darkness Energy": 15,
    "Devolution Spray": 1,
    "Life Herb": 2,
    "Magnetic Storm": 1,
    "Master Ball": 5,
    "Max Revive": 1,
    "Metal Energy": 15,
    "Pokémon Breeder": 3,
    "Pokémon Center": 3,
    "Pokémon Fan Club": 2,
    "PokéNav": 3,
    "Pokégear 3.0": 1,
    "Power Plant": 1,
    "Rainbow Energy": 2,
    "Super Potion": 2,
    "TV Reporter": 3,
    "Revive": 1,
    "Dusk Ball": 2,
}
assert len(collect_known_non_equivalent_ids(RESOURCES)) == 64

resolver = build_reprint_resolver(RESOURCES)
for card_id in summary["card_ids"]:
    assert resolver.resolve(card_id).kind == "known_non_equivalent"

assert resolver.resolve("base5-17").kind == "known_non_equivalent"
assert resolver.resolve("base5-80").kind == "known_non_equivalent"
assert resolver.resolve("dp2-119").kind == "known_non_equivalent"
assert resolver.resolve("dp2-120").kind == "known_non_equivalent"
assert resolver.resolve("ex5-90").kind == "known_non_equivalent"
assert resolver.resolve("ex6-93").kind == "known_non_equivalent"
assert resolver.resolve("ecard3-121").kind == "known_non_equivalent"
assert resolver.resolve("ecard2-130").kind == "known_non_equivalent"
assert resolver.resolve("base1-90").kind == "known_non_equivalent"
assert resolver.resolve("ex15-82").kind == "known_non_equivalent"

print("known negative reprint evidence: PASS")
print("known non-equivalent prints:", summary["counts"]["known_non_equivalent_prints"])
print("names:", summary["prints_by_name"])
