from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    has_tournament_ban_rule,
    load_json,
)
from tools.current_card_semantics import current_semantic_fingerprint
from tools.historical_reprint_evidence import (
    HISTORICAL_REPRINT_SOURCE,
    NO_REFERENCE_REPRINT_IDS,
)

ResolutionKind = Literal[
    "direct_legal",
    "direct_banned",
    "outside_disallowed",
    "exact_fingerprint_candidate",
    "historical_official_reprint_candidate",
    "official_errata_candidate",
    "semantic_review",
    "no_expanded_counterpart",
]

OFFICIAL_ERRATA_SOURCE = "https://play.pokemon.com/en-us/resources/documents/tcg-errata/"

# These are the name-wide Trainer entries under "Major Changes to Existing Cards"
# in the official TCG Errata resource. Exact print-specific corrections are
# normalized separately before gameplay fingerprints are compared.
NAME_WIDE_TRAINER_ERRATA = frozenset(
    {
        "Leftovers",
        "Super Rod",
        "Superior Energy Retrieval",
        "Rare Candy",
        "Potion",
        "Great Ball",
        "Pokémon Catcher",
        "Energy Retrieval",
        "Pal Pad",
        "Energy Recycler",
        "Lum Berry",
        "Sitrus Berry",
        "Hyper Potion",
        "Quick Ball",
        "PlusPower",
    }
)


@dataclass(frozen=True)
class ReprintResolution:
    card_id: str
    name: str
    kind: ResolutionKind
    target_print_ids: tuple[str, ...] = ()
    evidence_source: str | None = None


@dataclass(frozen=True)
class ReprintResolver:
    expanded_sets: frozenset[str]
    cards_by_id: dict[str, dict[str, Any]]
    legal_expanded_by_name: dict[str, tuple[dict[str, Any], ...]]
    legal_expanded_by_fingerprint: dict[str, tuple[dict[str, Any], ...]]

    def resolve(self, card_id: str) -> ReprintResolution:
        card = self.cards_by_id[card_id]
        name = card["name"]
        set_id = card["_set_id"]

        if set_id in self.expanded_sets:
            status, source = classify_effective_legality(card)
            return ReprintResolution(
                card_id,
                name,
                "direct_legal" if status == "Legal" else "direct_banned",
                (card_id,),
                source,
            )

        if has_tournament_ban_rule(card) or (card.get("legalities") or {}).get("unlimited") == "Banned":
            return ReprintResolution(card_id, name, "outside_disallowed")

        fingerprint_targets = self.legal_expanded_by_fingerprint.get(current_semantic_fingerprint(card), ())
        if fingerprint_targets:
            return ReprintResolution(
                card_id,
                name,
                "exact_fingerprint_candidate",
                tuple(sorted(target["id"] for target in fingerprint_targets)),
            )

        name_targets = self.legal_expanded_by_name.get(name, ())
        if name_targets and card_id in NO_REFERENCE_REPRINT_IDS:
            return ReprintResolution(
                card_id,
                name,
                "historical_official_reprint_candidate",
                tuple(sorted(target["id"] for target in name_targets)),
                HISTORICAL_REPRINT_SOURCE,
            )

        if name_targets and card.get("supertype") == "Trainer" and name in NAME_WIDE_TRAINER_ERRATA:
            return ReprintResolution(
                card_id,
                name,
                "official_errata_candidate",
                tuple(sorted(target["id"] for target in name_targets)),
                OFFICIAL_ERRATA_SOURCE,
            )

        if name_targets:
            return ReprintResolution(
                card_id,
                name,
                "semantic_review",
                tuple(sorted(target["id"] for target in name_targets)),
            )

        return ReprintResolution(card_id, name, "no_expanded_counterpart")


def build_reprint_resolver(resources_root: Path) -> ReprintResolver:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = frozenset(
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    )

    cards_by_id: dict[str, dict[str, Any]] = {}
    legal_by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    legal_by_fingerprint: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        for raw in load_json(path):
            card = dict(raw)
            card["_set_id"] = path.stem
            cards_by_id[card["id"]] = card
            if path.stem not in expanded_sets:
                continue
            status, _source = classify_effective_legality(card)
            if status != "Legal":
                continue
            legal_by_name[card["name"]].append(card)
            legal_by_fingerprint[current_semantic_fingerprint(card)].append(card)

    return ReprintResolver(
        expanded_sets=expanded_sets,
        cards_by_id=cards_by_id,
        legal_expanded_by_name={name: tuple(rows) for name, rows in legal_by_name.items()},
        legal_expanded_by_fingerprint={key: tuple(rows) for key, rows in legal_by_fingerprint.items()},
    )


def summarize_reprint_resolver(resolver: ReprintResolver) -> dict[str, Any]:
    outside_resolutions = [
        resolver.resolve(card_id)
        for card_id, card in resolver.cards_by_id.items()
        if card["_set_id"] not in resolver.expanded_sets
    ]
    counts = Counter(row.kind for row in outside_resolutions)

    trainer_review_pool = [
        row
        for row in outside_resolutions
        if resolver.cards_by_id[row.card_id].get("supertype") == "Trainer"
        and row.kind in {"exact_fingerprint_candidate", "historical_official_reprint_candidate", "official_errata_candidate", "semantic_review"}
    ]
    historical_rows = [
        row for row in outside_resolutions
        if row.kind == "historical_official_reprint_candidate"
    ]
    errata_rows = [row for row in outside_resolutions if row.kind == "official_errata_candidate"]
    exact_trainer_rows = [
        row
        for row in outside_resolutions
        if row.kind == "exact_fingerprint_candidate"
        and resolver.cards_by_id[row.card_id].get("supertype") == "Trainer"
    ]

    same_name_review_pool = [
        row
        for row in outside_resolutions
        if row.kind in {"exact_fingerprint_candidate", "historical_official_reprint_candidate", "official_errata_candidate", "semantic_review"}
    ]
    exact_rows = [row for row in outside_resolutions if row.kind == "exact_fingerprint_candidate"]

    return {
        "counts": {
            "outside_resolution_kinds": dict(sorted(counts.items())),
            "name_wide_trainer_errata_names": len(NAME_WIDE_TRAINER_ERRATA),
            "same_name_review_pool_prints": len(same_name_review_pool),
            "exact_fingerprint_candidate_prints": len(exact_rows),
            "historical_official_reprint_candidate_prints": len(historical_rows),
            "historical_official_reprint_candidate_names": len({row.name for row in historical_rows}),
            "official_errata_candidate_prints": len(errata_rows),
            "official_errata_candidate_names": len({row.name for row in errata_rows}),
            "semantic_review_prints": sum(row.kind == "semantic_review" for row in outside_resolutions),
            "high_confidence_candidate_prints": len(exact_rows) + len(historical_rows) + len(errata_rows),
            "exact_fingerprint_trainer_candidate_prints": len(exact_trainer_rows),
            "trainer_same_name_review_pool_prints": len(trainer_review_pool),
            "historical_official_trainer_candidate_prints": sum(
                row.kind == "historical_official_reprint_candidate"
                and resolver.cards_by_id[row.card_id].get("supertype") == "Trainer"
                for row in outside_resolutions
            ),
            "high_confidence_trainer_candidate_prints": (
                len(errata_rows)
                + len(exact_trainer_rows)
                + sum(
                    row.kind == "historical_official_reprint_candidate"
                    and resolver.cards_by_id[row.card_id].get("supertype") == "Trainer"
                    for row in outside_resolutions
                )
            ),
        },
        "historical_official_candidates_by_name": dict(
            sorted(Counter(row.name for row in historical_rows).items())
        ),
        "historical_official_candidate_ids": [
            row.card_id for row in sorted(historical_rows, key=lambda row: row.card_id)
        ],
        "official_errata_candidates_by_name": dict(
            sorted(Counter(row.name for row in errata_rows).items())
        ),
        "official_errata_candidate_ids": [
            row.card_id for row in sorted(errata_rows, key=lambda row: row.card_id)
        ],
    }
