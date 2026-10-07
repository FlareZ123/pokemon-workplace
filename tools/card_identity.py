from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from tools.build_expanded_legality_baseline import (
    classify_effective_legality,
    gameplay_fingerprint,
    load_json,
)

Legality = Literal["Legal", "Banned", "Mixed"]


@dataclass(frozen=True)
class PrintIdentity:
    card_id: str
    name: str
    set_id: str
    supertype: str | None
    effective_status: Literal["Legal", "Banned"]
    legality_source: Literal["database", "official_overlay", "card_text_tournament_ban", "set_fallback"]
    variant_id: str


@dataclass(frozen=True)
class IdentityIndex:
    prints_by_id: dict[str, PrintIdentity]
    prints_by_name: dict[str, tuple[PrintIdentity, ...]]
    prints_by_variant: dict[str, tuple[PrintIdentity, ...]]

    def name_legality(self, name: str) -> Legality:
        records = self.prints_by_name[name]
        return _collapse_legality(record.effective_status for record in records)

    def variant_legality(self, variant_id: str) -> Legality:
        records = self.prints_by_variant[variant_id]
        return _collapse_legality(record.effective_status for record in records)


def _collapse_legality(statuses: Iterable[Literal["Legal", "Banned"]]) -> Legality:
    unique = set(statuses)
    if unique == {"Legal"}:
        return "Legal"
    if unique == {"Banned"}:
        return "Banned"
    return "Mixed"


def build_identity_index(resources_root: Path) -> IdentityIndex:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    prints_by_id: dict[str, PrintIdentity] = {}
    names: dict[str, list[PrintIdentity]] = {}
    variants: dict[str, list[PrintIdentity]] = {}

    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        set_id = path.stem
        if set_id not in expanded_sets:
            continue

        for raw in load_json(path):
            card_id = raw["id"]
            effective_status, legality_source = classify_effective_legality(raw)

            record = PrintIdentity(
                card_id=card_id,
                name=raw["name"],
                set_id=set_id,
                supertype=raw.get("supertype"),
                effective_status=effective_status,
                legality_source=legality_source,
                variant_id=gameplay_fingerprint(raw),
            )
            if card_id in prints_by_id:
                raise ValueError(f"Duplicate card ID: {card_id}")
            prints_by_id[card_id] = record
            names.setdefault(record.name, []).append(record)
            variants.setdefault(record.variant_id, []).append(record)

    return IdentityIndex(
        prints_by_id=prints_by_id,
        prints_by_name={name: tuple(rows) for name, rows in names.items()},
        prints_by_variant={variant: tuple(rows) for variant, rows in variants.items()},
    )


def summarize_identity_index(index: IdentityIndex) -> dict[str, object]:
    mixed_names = []
    for name in sorted(index.prints_by_name):
        records = index.prints_by_name[name]
        if index.name_legality(name) != "Mixed":
            continue
        mixed_names.append(
            {
                "name": name,
                "legal_print_ids": [r.card_id for r in records if r.effective_status == "Legal"],
                "banned_print_ids": [r.card_id for r in records if r.effective_status == "Banned"],
                "distinct_variants": len({r.variant_id for r in records}),
            }
        )

    variant_sizes = [len(rows) for rows in index.prints_by_variant.values()]
    name_variant_counts = {
        name: len({record.variant_id for record in records})
        for name, records in index.prints_by_name.items()
    }
    top_variant_names = sorted(
        (
            {"name": name, "distinct_variants": count, "print_count": len(index.prints_by_name[name])}
            for name, count in name_variant_counts.items()
        ),
        key=lambda row: (-row["distinct_variants"], -row["print_count"], row["name"]),
    )[:20]

    return {
        "counts": {
            "prints": len(index.prints_by_id),
            "names": len(index.prints_by_name),
            "variants": len(index.prints_by_variant),
            "names_with_multiple_variants": sum(count > 1 for count in name_variant_counts.values()),
            "mixed_legality_names": sum(index.name_legality(name) == "Mixed" for name in index.prints_by_name),
            "all_banned_names": sum(index.name_legality(name) == "Banned" for name in index.prints_by_name),
            "mixed_legality_variants": sum(index.variant_legality(variant) == "Mixed" for variant in index.prints_by_variant),
            "legal_variants": sum(index.variant_legality(variant) == "Legal" for variant in index.prints_by_variant),
            "banned_variants": sum(index.variant_legality(variant) == "Banned" for variant in index.prints_by_variant),
            "variants_with_multiple_prints": sum(size > 1 for size in variant_sizes),
            "max_prints_in_one_variant": max(variant_sizes, default=0),
        },
        "mixed_legality_names": mixed_names,
        "top_names_by_variant_count": top_variant_names,
    }
