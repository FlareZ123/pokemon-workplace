from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from tools.build_expanded_legality_baseline import load_json
from tools.verified_card_metadata import normalize_verified_card_metadata


@dataclass(frozen=True)
class RuleBoxAudit:
    category_counts: dict[str, int]
    violations: tuple[tuple[str, str], ...]


def audit_pokemon_ruleboxes(cards_root: Path, *, corrected: bool) -> RuleBoxAudit:
    """Audit unambiguous printed-rule invariants, preserving print identities.

    The categories are deliberately separate. A missing subtype can evade a
    category-specific test; same-print comparison supplies another guard.
    """
    counts: Counter[str] = Counter()
    violations: list[tuple[str, str]] = []
    for file in sorted(cards_root.glob("*.json")):
        for raw in load_json(file):
            if raw.get("supertype") != "Pokémon":
                continue
            card = normalize_verified_card_metadata(raw) if corrected else raw
            card_id = card["id"]
            categories = set(card.get("subtypes") or ())
            rules = list(card.get("rules") or ())
            text = " ".join(rules)

            if {"MEGA", "ex"} <= categories:
                counts["Mega ex"] += 1
                mega = [r for r in rules if "Mega Evolution ex Rule:" in r]
                if (
                    len(mega) != 1
                    or "3 Prize cards" not in mega[0]
                    or any("Pokémon ex rule:" in r for r in rules)
                ):
                    violations.append((card_id, "Mega ex Prize Rule Box"))

            if {"Tera", "ex"} <= categories:
                counts["Tera ex"] += 1
                protection = [
                    r for r in rules
                    if "As long as this Pokémon is on your Bench" in r
                    and "prevent all damage done to this Pokémon by attacks" in r
                ]
                if len(protection) != 1:
                    violations.append((card_id, "Tera ex Bench protection"))

            for subtype, prize, category in (
                ("VMAX", "3", "VMAX"),
                ("VSTAR", "2", "VSTAR"),
                ("TAG TEAM", "3", "TAG TEAM"),
            ):
                if subtype not in categories:
                    continue
                counts[category] += 1
                if not any(subtype in r and f"{prize} Prize cards" in r for r in rules):
                    violations.append((card_id, category + " Prize Rule Box"))

            if "Radiant" in categories:
                counts["Radiant"] += 1
                if not any("1 Radiant Pokémon" in r for r in rules):
                    violations.append((card_id, "Radiant singleton Rule Box"))

    return RuleBoxAudit(
        category_counts=dict(sorted(counts.items())),
        violations=tuple(sorted(violations)),
    )
