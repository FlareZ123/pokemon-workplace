from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable

from tools.build_expanded_legality_baseline import load_json
from tools.verified_card_metadata import normalize_verified_card_metadata


@dataclass(frozen=True)
class PrintVariantIssue:
    set_id: str
    name: str
    print_ids: tuple[str, ...]
    subtype_variants: tuple[tuple[str, ...], ...]
    rule_variants: tuple[tuple[str, ...], ...]


def combat_signature(card: dict[str, Any]) -> str:
    """Deliberately omit print-specific subtype/rules, art, rarity and set data."""
    fields = (
        "name",
        "hp",
        "types",
        "evolvesFrom",
        "attacks",
        "abilities",
        "weaknesses",
        "resistances",
        "retreatCost",
    )
    return json.dumps(
        {key: card.get(key) for key in fields},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def find_same_set_print_anomalies(
    cards_root: Path, *, normalize: bool
) -> tuple[PrintVariantIssue, ...]:
    """Flag same-combat, same-set variants with differing subtype/rule data.

    This candidate generator does not decide whether a difference is a
    meaningful game rule, a wording-only variation, or an archive error.
    """
    issues: list[PrintVariantIssue] = []
    for file in sorted(cards_root.glob("*.json")):
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for raw in load_json(file):
            if raw.get("supertype") != "Pokémon":
                continue
            card = normalize_verified_card_metadata(raw) if normalize else raw
            groups[combat_signature(card)].append(card)

        for matching in groups.values():
            if len(matching) < 2:
                continue
            subtypes = tuple(
                sorted({tuple(card.get("subtypes") or ()) for card in matching})
            )
            rules = tuple(
                sorted({tuple(card.get("rules") or ()) for card in matching})
            )
            if len(subtypes) == len(rules) == 1:
                continue
            issues.append(
                PrintVariantIssue(
                    set_id=file.stem,
                    name=matching[0]["name"],
                    print_ids=tuple(sorted(card["id"] for card in matching)),
                    subtype_variants=subtypes,
                    rule_variants=rules,
                )
            )

    return tuple(sorted(issues, key=lambda row: (row.set_id, row.name, row.print_ids)))
