"""Expanded-legal XY Mega/Primal turn-end rule and Spirit Link coverage audit.

Coverage is based on printed names and exact Tool-effect targets, not artwork
or generic 'Mega' subtype classification. The bundled card pool includes
newer Mega Evolution ex prints with different rule semantics.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import json

from build_expanded_legality_baseline import classify_effective_legality


@dataclass(frozen=True)
class LegacyMegaCoverage:
    legacy_prints_by_name: tuple[tuple[str, tuple[str, ...]], ...]
    spirit_link_prints_by_target: tuple[tuple[str, tuple[str, ...]], ...]
    uncovered_names: tuple[str, ...]

    @property
    def total_legacy_prints(self) -> int:
        return sum(len(ids) for _, ids in self.legacy_prints_by_name)

    @property
    def total_link_prints(self) -> int:
        return sum(len(ids) for _, ids in self.spirit_link_prints_by_target)


def audit_legacy_mega_spirit_links(resources: Path) -> LegacyMegaCoverage:
    sets = json.loads(
        (resources / "sets" / "en.json").read_text(encoding="utf-8")
    )
    eligible_sets = {
        row["id"] for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    megas: dict[str, list[str]] = defaultdict(list)
    links: dict[str, list[str]] = defaultdict(list)
    for path in sorted((resources / "cards" / "en").glob("*.json")):
        if path.stem not in eligible_sets:
            continue
        cards = json.loads(path.read_text(encoding="utf-8"))
        for card in cards:
            if classify_effective_legality(card)[0] != "Legal":
                continue
            name = card["name"]
            rules = tuple(card.get("rules") or ())
            if card.get("supertype") == "Pokémon" and (
                any(rule.startswith("Mega Evolution rule: When") for rule in rules)
                or any(rule.startswith("Primal Reversion rule: When") for rule in rules)
            ):
                megas[name].append(card["id"])

            if (
                card.get("supertype") == "Trainer"
                and "Pokémon Tool" in (card.get("subtypes") or ())
                and name.endswith(" Spirit Link")
            ):
                for rule in rules:
                    prefix = (
                        "Your turn does not end if the Pokémon this card "
                        "is attached to becomes "
                    )
                    if rule.startswith(prefix) and rule.endswith("."):
                        target = rule[len(prefix):-1]
                        links[target].append(card["id"])

    ordered_mega = tuple(
        (name, tuple(sorted(ids)))
        for name, ids in sorted(megas.items())
    )
    ordered_links = tuple(
        (name, tuple(sorted(ids)))
        for name, ids in sorted(links.items())
    )
    return LegacyMegaCoverage(
        legacy_prints_by_name=ordered_mega,
        spirit_link_prints_by_target=ordered_links,
        uncovered_names=tuple(sorted(megas.keys() - links.keys())),
    )
