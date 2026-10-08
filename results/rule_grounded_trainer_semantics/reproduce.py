from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.current_card_semantics import current_semantic_fingerprint
from tools.reprint_errata_resolution import build_reprint_resolver
from tools.reprint_semantic_benchmark import summarize_semantic_benchmark

RESOURCES = ROOT / "resources"
resolver = build_reprint_resolver(RESOURCES)

assert current_semantic_fingerprint(resolver.cards_by_id["ecard3-125"]) == current_semantic_fingerprint(
    resolver.cards_by_id["sm7-130"]
)
assert current_semantic_fingerprint(resolver.cards_by_id["hgss1-92"]) == current_semantic_fingerprint(
    resolver.cards_by_id["sm7-130"]
)

assert current_semantic_fingerprint(resolver.cards_by_id["pl1-108"]) == current_semantic_fingerprint(
    resolver.cards_by_id["sm7-136"]
)
assert current_semantic_fingerprint(resolver.cards_by_id["hgss2-79"]) == current_semantic_fingerprint(
    resolver.cards_by_id["sm7-136"]
)

assert current_semantic_fingerprint(resolver.cards_by_id["hgss1-94"]) == current_semantic_fingerprint(
    resolver.cards_by_id["sm8-185"]
)
assert resolver.resolve("hgss1-94").kind == "exact_fingerprint_candidate"

for source_id in ("ex6-100", "pl3-140"):
    assert current_semantic_fingerprint(resolver.cards_by_id[source_id]) == current_semantic_fingerprint(
        resolver.cards_by_id["xy4-109"]
    )
    assert resolver.resolve(source_id).kind == "exact_fingerprint_candidate"

for source_id in ("ecard1-137", "ex14-71", "ex6-87", "pop5-6"):
    assert current_semantic_fingerprint(resolver.cards_by_id[source_id]) == current_semantic_fingerprint(
        resolver.cards_by_id["sm7-126"]
    )
    assert resolver.resolve(source_id).kind == "exact_fingerprint_candidate"

for source_id in ("ecard3-140", "pl2-97"):
    assert current_semantic_fingerprint(resolver.cards_by_id[source_id]) == current_semantic_fingerprint(
        resolver.cards_by_id["sm7-150"]
    )
    assert resolver.resolve(source_id).kind == "exact_fingerprint_candidate"

assert current_semantic_fingerprint(resolver.cards_by_id["pl4-88"]) == current_semantic_fingerprint(
    resolver.cards_by_id["swsh1-167"]
)
assert resolver.resolve("pl4-88").kind == "exact_fingerprint_candidate"

assert current_semantic_fingerprint(resolver.cards_by_id["ex5-90"]) != current_semantic_fingerprint(
    resolver.cards_by_id["sm7-136"]
)
assert current_semantic_fingerprint(resolver.cards_by_id["ex6-93"]) != current_semantic_fingerprint(
    resolver.cards_by_id["sm7-136"]
)
assert resolver.resolve("ex5-90").kind == "known_non_equivalent"
assert resolver.resolve("ex6-93").kind == "known_non_equivalent"

assert current_semantic_fingerprint(resolver.cards_by_id["base1-87"]) != current_semantic_fingerprint(
    resolver.cards_by_id["bw1-98"]
)
assert current_semantic_fingerprint(resolver.cards_by_id["base4-115"]) != current_semantic_fingerprint(
    resolver.cards_by_id["bw1-98"]
)

summary = summarize_semantic_benchmark(RESOURCES, resolver=resolver)
counts = summary["counts"]
assert counts["legacy_no_reference_trainer_prints"] == 76
assert counts["legacy_current_resolver_kinds"] == {
    "exact_fingerprint_candidate": 5,
    "historical_official_reprint_candidate": 38,
    "known_non_equivalent": 2,
    "official_errata_candidate": 26,
    "official_semantic_candidate": 3,
    "semantic_review": 2,
}
assert counts["legacy_semantic_review_gap"] == 2
assert summary["legacy_semantic_review_ids"] == ["base1-87", "base4-115"]

assert resolver.resolve("ecard3-125").kind == "exact_fingerprint_candidate"
assert resolver.resolve("pl1-108").kind == "exact_fingerprint_candidate"

print("rule-grounded Trainer semantic regression passed")
