from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.errata_reprint_candidates import analyze

result = analyze(ROOT / "resources")
counts = result["counts"]

assert counts == {
    "errata_candidate_prints": 44,
    "errata_candidate_names": 11,
    "handbook_positive_variant_prints": 3,
    "handbook_negative_variant_prints": 2,
    "combined_semantic_candidate_prints": 47,
}

assert {row["id"] for row in result["handbook_positive_variant_candidates"]} == {
    "ecard1-138",
    "ex15-73",
    "ex7-83",
}
assert {row["id"] for row in result["handbook_negative_variant_examples"]} == {
    "base5-17",
    "base5-80",
}

print("errata-aware reprint candidate audit: PASS")
print("errata candidates:", counts["errata_candidate_prints"])
print("Copycat old-fingerprint candidates:", counts["handbook_positive_variant_prints"])
print("Rainbow Energy explicit non-equivalent old-fingerprint prints:", counts["handbook_negative_variant_prints"])
