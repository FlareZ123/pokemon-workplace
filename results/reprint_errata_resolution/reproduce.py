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
print("resolver counts before assertions:", counts)
print("historical candidates by name before assertions:", summary["historical_official_candidates_by_name"])

assert counts["same_name_review_pool_prints"] == 4260
assert counts["exact_fingerprint_candidate_prints"] == 123
assert counts["historical_official_reprint_candidate_prints"] == 39
assert counts["historical_official_reprint_candidate_names"] == 8
assert counts["official_errata_candidate_prints"] == 44
assert counts["official_errata_candidate_names"] == 11
assert counts["known_non_equivalent_prints"] == 67
assert counts["known_non_equivalent_names"] == 21
assert counts["official_semantic_candidate_prints"] == 3
assert counts["official_semantic_candidate_names"] == 1
assert counts["semantic_review_prints"] == 3984
assert counts["high_confidence_candidate_prints"] == 209
assert counts["exact_fingerprint_trainer_candidate_prints"] == 19
assert counts["trainer_same_name_review_pool_prints"] == 168
assert counts["historical_official_trainer_candidate_prints"] == 38
assert counts["high_confidence_trainer_candidate_prints"] == 104
assert counts["name_wide_trainer_errata_names"] == 15

assert summary["official_semantic_candidates_by_name"] == {"Copycat": 3}
assert summary["official_semantic_candidate_ids"] == ["ecard1-138", "ex15-73", "ex7-83"]

assert summary["known_non_equivalent_by_name"] == {
    "Apricorn Maker": 1,
    "Computer Search": 2,
    "Darkness Energy": 15,
    "Devolution Spray": 1,
    "Friend Ball": 1,
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

assert summary["historical_official_candidates_by_name"] == {
    "Double Colorless Energy": 1,
    "Energy Search": 7,
    "Energy Switch": 7,
    "Full Heal": 1,
    "Poké Ball": 6,
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

assert resolver.resolve("base1-71").kind == "known_non_equivalent"
assert resolver.resolve("base4-101").kind == "known_non_equivalent"
assert resolver.resolve("base5-17").kind == "known_non_equivalent"
assert resolver.resolve("base5-80").kind == "known_non_equivalent"
assert resolver.resolve("dp2-119").kind == "known_non_equivalent"
assert resolver.resolve("ex5-90").kind == "known_non_equivalent"
assert resolver.resolve("ex6-93").kind == "known_non_equivalent"
assert resolver.resolve("ex11-99").kind == "known_non_equivalent"
assert resolver.resolve("base1-76").kind == "known_non_equivalent"
assert resolver.resolve("base1-85").kind == "known_non_equivalent"
assert resolver.resolve("gym2-117").kind == "known_non_equivalent"
assert resolver.resolve("base1-89").kind == "known_non_equivalent"
assert resolver.resolve("base1-72").kind == "known_non_equivalent"
assert resolver.resolve("ecard2-139").kind == "known_non_equivalent"
assert resolver.resolve("ex5-91").kind == "known_non_equivalent"
assert resolver.resolve("ex1-88").kind == "known_non_equivalent"
assert resolver.resolve("hgss1-96").kind == "known_non_equivalent"
assert resolver.resolve("dp2-110").kind == "known_non_equivalent"
assert resolver.resolve("ecard3-121").kind == "known_non_equivalent"
assert resolver.resolve("ecard3-126").kind == "known_non_equivalent"
assert resolver.resolve("ecard2-130").kind == "known_non_equivalent"
assert resolver.resolve("base1-90").kind == "known_non_equivalent"
assert resolver.resolve("ex15-82").kind == "known_non_equivalent"
assert resolver.resolve("base1-95").kind == "historical_official_reprint_candidate"
assert resolver.resolve("base1-96").kind == "historical_official_reprint_candidate"
assert resolver.resolve("dp4-99").kind == "official_errata_candidate"
assert resolver.resolve("ex2-88").kind == "official_errata_candidate"
assert resolver.resolve("gym1-18").kind == "exact_fingerprint_candidate"
assert resolver.resolve("hgss2-78").kind == "exact_fingerprint_candidate"
assert resolver.resolve("hgss1-93").kind == "exact_fingerprint_candidate"
assert resolver.resolve("ecard3-125").kind == "exact_fingerprint_candidate"
assert resolver.resolve("hgss1-92").kind == "exact_fingerprint_candidate"
assert resolver.resolve("pl1-108").kind == "exact_fingerprint_candidate"
assert resolver.resolve("hgss2-79").kind == "exact_fingerprint_candidate"
assert resolver.resolve("hgss1-94").kind == "exact_fingerprint_candidate"
assert resolver.resolve("ex6-100").kind == "exact_fingerprint_candidate"
assert resolver.resolve("pl3-140").kind == "exact_fingerprint_candidate"
assert resolver.resolve("ecard1-137").kind == "exact_fingerprint_candidate"
assert resolver.resolve("ex14-71").kind == "exact_fingerprint_candidate"
assert resolver.resolve("ex6-87").kind == "exact_fingerprint_candidate"
assert resolver.resolve("pop5-6").kind == "exact_fingerprint_candidate"
assert resolver.resolve("dp1-110").kind == "exact_fingerprint_candidate"
assert resolver.resolve("ex7-83").kind == "official_semantic_candidate"
assert resolver.resolve("ex15-73").kind == "official_semantic_candidate"
assert resolver.resolve("ecard1-138").kind == "official_semantic_candidate"
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
