from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from tools.reprint_errata_resolution import (
    NAME_WIDE_TRAINER_ERRATA,
    ReprintResolver,
    build_reprint_resolver,
)
from tools.reprint_semantic_benchmark import build_semantic_benchmark

EXCLUSION_RE = re.compile(r"\bexcluding\s+([^)]+)\)", flags=re.IGNORECASE)

PredicateStatus = Literal[
    "overridden_by_name_wide_errata",
    "reachable_current_divergence",
    "currently_unwitnessed",
]


@dataclass(frozen=True)
class ExclusionPredicate:
    source_card_id: str
    name: str
    exclusion: str
    predicate: str
    status: PredicateStatus
    current_target_print_ids: tuple[str, ...]
    witness_card_ids: tuple[str, ...]


def extract_explicit_exclusions(card: dict[str, object]) -> tuple[str, ...]:
    text = " ".join(str(rule) for rule in (card.get("rules") or ()))
    return tuple(match.group(1).strip() for match in EXCLUSION_RE.finditer(text))


def _pokemon_ex_witness_ids(resolver: ReprintResolver) -> tuple[str, ...]:
    witness_ids: list[str] = []
    for card_id, card in resolver.cards_by_id.items():
        if resolver.resolve(card_id).kind != "direct_legal":
            continue
        rules = card.get("rules") or ()
        if any("When Pokémon-ex has been Knocked Out" in str(rule) for rule in rules):
            witness_ids.append(card_id)
    return tuple(sorted(witness_ids))


def _predicate_for_exclusion(exclusion: str) -> str:
    if exclusion.casefold() == "pokémon-ex".casefold():
        return "target is Pokémon-ex"
    return f"target matches excluded class: {exclusion}"


def scan_benchmark_exclusion_predicates(
    resources_root: Path,
    *,
    resolver: ReprintResolver | None = None,
) -> tuple[ExclusionPredicate, ...]:
    resolver = resolver or build_reprint_resolver(resources_root)
    pokemon_ex_witnesses = _pokemon_ex_witness_ids(resolver)
    rows: list[ExclusionPredicate] = []

    for case in build_semantic_benchmark(resources_root, resolver=resolver):
        if case.evidence_class != "legacy_no_reference_positive":
            continue

        source = resolver.cards_by_id[case.source_card_id]
        exclusions = extract_explicit_exclusions(source)
        if not exclusions:
            continue

        current_targets = resolver.legal_expanded_by_name[case.name]
        for exclusion in exclusions:
            divergent_targets = tuple(
                sorted(
                    target["id"]
                    for target in current_targets
                    if exclusion.casefold()
                    not in {
                        value.casefold()
                        for value in extract_explicit_exclusions(target)
                    }
                )
            )

            if case.name in NAME_WIDE_TRAINER_ERRATA:
                status: PredicateStatus = "overridden_by_name_wide_errata"
                witness_ids: tuple[str, ...] = ()
            elif exclusion.casefold() == "pokémon-ex".casefold() and divergent_targets:
                witness_ids = pokemon_ex_witnesses
                status = (
                    "reachable_current_divergence"
                    if witness_ids
                    else "currently_unwitnessed"
                )
            else:
                witness_ids = ()
                status = "currently_unwitnessed"

            rows.append(
                ExclusionPredicate(
                    source_card_id=case.source_card_id,
                    name=case.name,
                    exclusion=exclusion,
                    predicate=_predicate_for_exclusion(exclusion),
                    status=status,
                    current_target_print_ids=divergent_targets,
                    witness_card_ids=witness_ids,
                )
            )

    return tuple(rows)


def summarize_benchmark_exclusion_predicates(
    resources_root: Path,
    *,
    resolver: ReprintResolver | None = None,
) -> dict[str, object]:
    rows = scan_benchmark_exclusion_predicates(resources_root, resolver=resolver)
    status_counts = Counter(row.status for row in rows)
    reachable = [
        row for row in rows if row.status == "reachable_current_divergence"
    ]

    return {
        "counts": {
            "benchmark_rows_with_explicit_exclusions": len(rows),
            "overridden_by_name_wide_errata": status_counts[
                "overridden_by_name_wide_errata"
            ],
            "reachable_current_divergence": status_counts[
                "reachable_current_divergence"
            ],
            "currently_unwitnessed": status_counts["currently_unwitnessed"],
            "distinct_reachable_predicates": len(
                {row.predicate for row in reachable}
            ),
            "distinct_reachable_witness_cards": len(
                {
                    card_id
                    for row in reachable
                    for card_id in row.witness_card_ids
                }
            ),
        },
        "rows": [
            {
                "source_card_id": row.source_card_id,
                "name": row.name,
                "exclusion": row.exclusion,
                "predicate": row.predicate,
                "status": row.status,
                "current_target_print_ids": list(row.current_target_print_ids),
                "witness_card_ids": list(row.witness_card_ids),
            }
            for row in rows
        ],
    }
