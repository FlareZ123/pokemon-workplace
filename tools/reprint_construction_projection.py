from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.reprint_errata_resolution import ReprintResolver, build_reprint_resolver


@dataclass(frozen=True)
class ConstructionProjectionHazard:
    source_card_id: str
    name: str
    source_rules: tuple[str, ...]
    resolution_kind: str
    same_name_target_ids: tuple[str, ...]
    divergent_same_name_target_ids: tuple[str, ...]
    resolver_target_ids: tuple[str, ...]
    divergent_resolver_target_ids: tuple[str, ...]


def copy_limit_rules(card: dict) -> tuple[str, ...]:
    return tuple(
        sorted(
            rule
            for rule in (card.get("rules") or ())
            if "can't have more than" in rule.lower() and "deck" in rule.lower()
        )
    )


def _divergent_targets(
    resolver: ReprintResolver,
    source_rules: tuple[str, ...],
    target_ids: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(
        card_id
        for card_id in target_ids
        if copy_limit_rules(resolver.cards_by_id[card_id]) != source_rules
    )


def audit_construction_projection(
    resources_root: Path,
) -> tuple[ConstructionProjectionHazard, ...]:
    resolver = build_reprint_resolver(resources_root)
    rows: list[ConstructionProjectionHazard] = []

    for card_id, card in sorted(resolver.cards_by_id.items()):
        if card["_set_id"] in resolver.expanded_sets:
            continue

        same_name_targets = tuple(
            sorted(target["id"] for target in resolver.legal_expanded_by_name.get(card["name"], ()))
        )
        if not same_name_targets:
            continue

        source_rules = copy_limit_rules(card)
        divergent_same_name = _divergent_targets(
            resolver,
            source_rules,
            same_name_targets,
        )
        if not divergent_same_name:
            continue

        resolution = resolver.resolve(card_id)
        resolver_targets = tuple(sorted(resolution.target_print_ids))
        rows.append(
            ConstructionProjectionHazard(
                source_card_id=card_id,
                name=card["name"],
                source_rules=source_rules,
                resolution_kind=resolution.kind,
                same_name_target_ids=same_name_targets,
                divergent_same_name_target_ids=divergent_same_name,
                resolver_target_ids=resolver_targets,
                divergent_resolver_target_ids=_divergent_targets(
                    resolver,
                    source_rules,
                    resolver_targets,
                ),
            )
        )

    return tuple(rows)
