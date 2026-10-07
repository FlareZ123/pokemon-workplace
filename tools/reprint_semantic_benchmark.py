from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from tools.reprint_errata_resolution import ReprintResolver, build_reprint_resolver

LEGACY_REPRINT_LIST_SOURCE = (
    "https://assets.pokemon.com/assets/cms/pdf/op/tournaments/2012/"
    "2012_modified_legal_reprints.pdf"
)
CURRENT_HANDBOOK_SOURCE = (
    "https://www.pokemon.com/static-assets/content-assets/cms2/pdf/play-pokemon/"
    "rules/play-pokemon-tournament-rules-handbook-10062023-en.pdf"
)

# Trainer printings explicitly marked "Reference Required: No" in the official
# 2012 Modified-Legal Reprint List, restricted to names that also have at least
# one legal print in the current repository Expanded pool.
#
# This is historical positive evidence that the listed older printing was usable
# without updated wording for the then-current legal reprint. It is a semantic
# benchmark, not an automatic present-day legality overlay.
LEGACY_NO_REFERENCE_TRAINER_IDS = frozenset(
    {
        "base1-84", "base1-87", "base1-94", "base1-95",
        "base2-64",
        "base3-59", "base3-61",
        "base4-113", "base4-115", "base4-121", "base4-122", "base4-123",
        "base6-110",
        "neo1-98",
        "ecard1-138", "ecard1-151", "ecard1-153", "ecard1-154", "ecard1-156", "ecard1-157",
        "ecard2-120",
        "ecard3-125",
        "ex1-82", "ex1-86", "ex1-90", "ex1-91", "ex1-92",
        "ex5-90",
        "ex6-90", "ex6-92", "ex6-93", "ex6-95", "ex6-99", "ex6-101", "ex6-102",
        "ex7-83",
        "ex9-83",
        "ex10-84", "ex10-87", "ex10-94", "ex10-95",
        "ex11-90", "ex11-100", "ex11-101", "ex11-102",
        "ex13-90",
        "ex14-82", "ex14-86", "ex14-87",
        "ex15-73", "ex15-83",
        "ex16-75", "ex16-77",
        "dp1-107", "dp1-109", "dp1-110", "dp1-115", "dp1-117", "dp1-118", "dp1-119",
        "dp3-121", "dp3-127", "dp3-128",
        "dp4-102",
        "dp5-85", "dp5-87", "dp5-90",
        "dp7-84", "dp7-85", "dp7-92", "dp7-93",
        "pl1-108", "pl1-112", "pl1-113",
        "pop5-7", "pop8-10",
    }
)

CURRENT_HANDBOOK_POSITIVE_PAIRS = frozenset({("ex7-83", "sm7-127")})
CURRENT_HANDBOOK_NEGATIVE_PAIRS = frozenset({("base5-17", "sm7-151")})

EvidenceClass = Literal[
    "legacy_no_reference_positive",
    "current_handbook_positive",
    "current_handbook_negative",
]


@dataclass(frozen=True)
class SemanticBenchmarkCase:
    evidence_class: EvidenceClass
    source_card_id: str
    target_card_id: str | None
    name: str
    source: str


def build_semantic_benchmark(
    resources_root: Path,
    *,
    resolver: ReprintResolver | None = None,
) -> tuple[SemanticBenchmarkCase, ...]:
    resolver = resolver or build_reprint_resolver(resources_root)
    cases: list[SemanticBenchmarkCase] = []

    for card_id in sorted(LEGACY_NO_REFERENCE_TRAINER_IDS):
        card = resolver.cards_by_id[card_id]
        targets = resolver.legal_expanded_by_name.get(card["name"], ())
        if not targets:
            raise ValueError(f"Legacy benchmark card has no legal Expanded same-name target: {card_id}")
        if card.get("supertype") != "Trainer":
            raise ValueError(f"Legacy benchmark card is not a Trainer: {card_id}")
        if card["_set_id"] in resolver.expanded_sets:
            raise ValueError(f"Legacy benchmark card is already directly in Expanded: {card_id}")

        cases.append(
            SemanticBenchmarkCase(
                evidence_class="legacy_no_reference_positive",
                source_card_id=card_id,
                target_card_id=None,
                name=card["name"],
                source=LEGACY_REPRINT_LIST_SOURCE,
            )
        )

    for source_id, target_id in sorted(CURRENT_HANDBOOK_POSITIVE_PAIRS):
        source = resolver.cards_by_id[source_id]
        target = resolver.cards_by_id[target_id]
        if source["name"] != target["name"]:
            raise ValueError(f"Positive pair name mismatch: {source_id}, {target_id}")
        cases.append(
            SemanticBenchmarkCase(
                "current_handbook_positive",
                source_id,
                target_id,
                source["name"],
                CURRENT_HANDBOOK_SOURCE,
            )
        )

    for source_id, target_id in sorted(CURRENT_HANDBOOK_NEGATIVE_PAIRS):
        source = resolver.cards_by_id[source_id]
        target = resolver.cards_by_id[target_id]
        if source["name"] != target["name"]:
            raise ValueError(f"Negative pair name mismatch: {source_id}, {target_id}")
        cases.append(
            SemanticBenchmarkCase(
                "current_handbook_negative",
                source_id,
                target_id,
                source["name"],
                CURRENT_HANDBOOK_SOURCE,
            )
        )

    return tuple(cases)


def summarize_semantic_benchmark(
    resources_root: Path,
    *,
    resolver: ReprintResolver | None = None,
) -> dict[str, object]:
    resolver = resolver or build_reprint_resolver(resources_root)
    cases = build_semantic_benchmark(resources_root, resolver=resolver)
    legacy = [case for case in cases if case.evidence_class == "legacy_no_reference_positive"]

    resolver_kinds = Counter(
        resolver.resolve(case.source_card_id).kind
        for case in legacy
    )
    legacy_names = Counter(case.name for case in legacy)

    return {
        "counts": {
            "legacy_no_reference_trainer_prints": len(legacy),
            "legacy_no_reference_trainer_names": len(legacy_names),
            "legacy_current_resolver_kinds": dict(sorted(resolver_kinds.items())),
            "legacy_semantic_review_gap": resolver_kinds["semantic_review"],
            "current_handbook_positive_pairs": len(CURRENT_HANDBOOK_POSITIVE_PAIRS),
            "current_handbook_negative_pairs": len(CURRENT_HANDBOOK_NEGATIVE_PAIRS),
        },
        "legacy_positive_by_name": dict(sorted(legacy_names.items())),
        "legacy_semantic_review_ids": [
            case.source_card_id
            for case in legacy
            if resolver.resolve(case.source_card_id).kind == "semantic_review"
        ],
    }
