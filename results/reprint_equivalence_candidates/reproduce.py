from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.build_expanded_legality_baseline import gameplay_fingerprint, load_json
from tools.reprint_equivalence_candidates import build_candidates

RESOURCES = ROOT / "resources"
result = build_candidates(RESOURCES)
counts = result["counts"]

assert counts["exact_candidate_prints"] == 100
assert counts["exact_candidate_variants"] == 16
assert counts["exact_candidate_names"] == 16
assert counts["same_name_review_prints"] == 4248
assert counts["same_name_review_names"] == 636
assert counts["exact_by_supertype"] == {"Energy": 91, "Pokémon": 9}

cards = {}
for path in (RESOURCES / "cards" / "en").glob("*.json"):
    for card in load_json(path):
        if card["id"] in {"sm7-127", "ex7-83"}:
            cards[card["id"]] = card

assert set(cards) == {"sm7-127", "ex7-83"}
assert cards["sm7-127"]["name"] == cards["ex7-83"]["name"] == "Copycat"
assert gameplay_fingerprint(cards["sm7-127"]) != gameplay_fingerprint(cards["ex7-83"])

print("reprint equivalence candidate audit: PASS")
print("exact fingerprint candidates:", counts["exact_candidate_prints"])
print("same-name semantic review pool:", counts["same_name_review_prints"])
print("Copycat official-example fingerprints differ")
