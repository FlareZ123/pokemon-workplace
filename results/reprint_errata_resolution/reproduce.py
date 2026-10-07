from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_errata_resolution import (
    NAME_WIDE_TRAINER_ERRATA,
    build_reprint_resolver,
    summarize_reprint_resolver,
)

RESOURCES = ROOT / "resources"
resolver = build_reprint_resolver(RESOURCES)
summary = summarize_reprint_resolver(resolver)
counts = summary["counts"]

assert counts["same_name_review_pool_prints"] == 4260
assert counts["exact_fingerprint_candidate_prints"] == 106
assert counts["historical_official_reprint_candidate_prints"] == 42
assert counts["historical_official_reprint_candidate_names"] == 8
assert counts["official_errata_candidate_prints"] == 44
assert counts["official_errata_candidate_names"] == 11
assert counts["known_non_equivalent_prints"] == 34
assert counts["known_non_equivalent_names"] == 4
assert counts["semantic_review_prints"] == 4034
assert counts["high_confidence_candidate_prints"] == 192
assert counts["exact_fingerprint_trainer_candidate_prints"] == 2
assert counts["trainer_same_name_review_pool_prints"] == 168
assert counts["historical_official_trainer_candidate_prints"] == 41
assert counts["high_confidence_trainer_candidate_prints"] == 87
assert counts["name_wide_trainer_errata_names"] == 15

assert summary["known_non_equivalent_by_name"] == {
    "Darkness Energy": 15,
    "Life Herb": 2,
    "Metal Energy": 15,
    "Rainbow Energy": 2,
}

assert summary["historical_official_candidates_by_name"] == {
    "Double Colorless Energy": 1,
    "Energy Search": 7,
    "Energy Switch": 7,
    "Full Heal": 1,
    "Poké Ball": 9,
    "Recycle": 1,
    "Super Scoop Up": 6,
    "Switch": 10,
}

assert summary["official_errata_candidates_by_name"] == {
    "Energy Retrieval": 3,
    "Great Ball": 4,
    "Hyper Potion": 1,
    "Leftovers": 1,
    "Lum Berry": 2,
    "PlusPower": 6,
    "Potion": 16,
    "Quick Ball": 2,
    "Rare Candy": 7,
    "Sitrus Berry": 1,
    "Super Rod": 1,
}

assert all(name in resolver.legal_expanded_by_name for name in NAME_WIDE_TRAINER_ERRATA)

assert resolver.resolve("base5-17").kind == "known_non_equivalent"
assert resolver.resolve("base5-80").kind == "known_non_equivalent"
assert resolver.resolve("dp2-119").kind == "known_non_equivalent"
assert resolver.resolve("ex5-90").kind == "known_non_equivalent"
assert resolver.resolve("ex6-93").kind == "known_non_equivalent"
assert resolver.resolve("base1-95").kind == "historical_official_reprint_candidate"
assert resolver.resolve("base1-96").kind == "historical_official_reprint_candidate"
assert resolver.resolve("dp4-99").kind == "official_errata_candidate"
assert resolver.resolve("ex2-88").kind == "official_errata_candidate"
assert resolver.resolve("gym1-18").kind == "exact_fingerprint_candidate"
assert resolver.resolve("ex7-83").kind == "semantic_review"
assert resolver.resolve("bw5-100").kind == "direct_legal"

print("errata-aware reprint resolution: PASS")
print("same-name review pool:", counts["same_name_review_pool_prints"])
print("exact fingerprint candidates:", counts["exact_fingerprint_candidate_prints"])
print("historical official candidates:", counts["historical_official_reprint_candidate_prints"])
print("official errata candidates:", counts["official_errata_candidate_prints"])
print("remaining semantic review:", counts["semantic_review_prints"])
print(
    "trainer high-confidence candidates:",
    f'{counts["high_confidence_trainer_candidate_prints"]}/{counts["trainer_same_name_review_pool_prints"]}',
)
