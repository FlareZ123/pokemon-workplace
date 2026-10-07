from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.reprint_errata_resolution import build_reprint_resolver
from tools.reprint_semantic_benchmark import (
    CURRENT_HANDBOOK_NEGATIVE_PAIRS,
    CURRENT_HANDBOOK_POSITIVE_PAIRS,
    build_semantic_benchmark,
    summarize_semantic_benchmark,
)

RESOURCES = ROOT / "resources"
resolver = build_reprint_resolver(RESOURCES)
cases = build_semantic_benchmark(RESOURCES, resolver=resolver)
summary = summarize_semantic_benchmark(RESOURCES, resolver=resolver)
counts = summary["counts"]

assert counts["legacy_no_reference_trainer_prints"] == 76
assert counts["legacy_no_reference_trainer_names"] == 15
assert counts["legacy_current_resolver_kinds"] == {
    "exact_fingerprint_candidate": 5,
    "historical_official_reprint_candidate": 38,
    "known_non_equivalent": 2,
    "official_errata_candidate": 26,
    "official_semantic_candidate": 3,
    "semantic_review": 2,
}
assert counts["legacy_semantic_review_gap"] == 2
assert counts["current_handbook_positive_pairs"] == 1
assert counts["current_handbook_negative_pairs"] == 1

assert summary["legacy_positive_by_name"] == {
    "Copycat": 3,
    "Energy Search": 7,
    "Energy Switch": 7,
    "Fisherman": 1,
    "Full Heal": 1,
    "Great Ball": 4,
    "Life Herb": 3,
    "PlusPower": 5,
    "Poké Ball": 9,
    "Pokédex": 2,
    "Potion": 12,
    "Rare Candy": 5,
    "Recycle": 1,
    "Super Scoop Up": 6,
    "Switch": 10,
}

assert ("ex7-83", "sm7-127") in CURRENT_HANDBOOK_POSITIVE_PAIRS
assert ("base5-17", "sm7-151") in CURRENT_HANDBOOK_NEGATIVE_PAIRS
assert resolver.resolve("ex7-83").kind == "official_semantic_candidate"
assert resolver.resolve("base5-17").kind == "known_non_equivalent"
assert resolver.resolve("ecard3-125").kind == "exact_fingerprint_candidate"
assert resolver.resolve("pl1-108").kind == "exact_fingerprint_candidate"
assert summary["legacy_semantic_review_ids"] == ["base1-87", "base4-115"]

positive = [case for case in cases if case.evidence_class == "current_handbook_positive"]
negative = [case for case in cases if case.evidence_class == "current_handbook_negative"]
assert positive[0].name == negative[0].name or positive[0].name == "Copycat"
assert negative[0].name == "Rainbow Energy"

print("official reprint semantic benchmark: PASS")
print("legacy no-reference Trainer positives:", counts["legacy_no_reference_trainer_prints"])
print("exact after current normalization:", counts["legacy_current_resolver_kinds"]["exact_fingerprint_candidate"])
print("historically bridged:", counts["legacy_current_resolver_kinds"]["historical_official_reprint_candidate"])
print("resolved by current errata:", counts["legacy_current_resolver_kinds"]["official_errata_candidate"])
print("resolved by current handbook semantics:", counts["legacy_current_resolver_kinds"]["official_semantic_candidate"])
print("current known negatives:", counts["legacy_current_resolver_kinds"]["known_non_equivalent"])
print("remaining semantic review:", counts["legacy_semantic_review_gap"])
print("current handbook positive pair:", next(iter(CURRENT_HANDBOOK_POSITIVE_PAIRS)))
print("current handbook negative pair:", next(iter(CURRENT_HANDBOOK_NEGATIVE_PAIRS)))
