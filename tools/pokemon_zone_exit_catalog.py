"""Catalog effectively legal Expanded Pokemon board-object zone exits.

The scanner is intentionally conservative. It recognizes text that explicitly
moves a Pokemon together with all attached cards to hand/deck, plus the common
split form that moves the Pokemon to hand and discards all attached cards.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


_COMBINED_ROUTE_RE = re.compile(
    r"(?:put|shuffle|shuffles)[^.]{0,240}"
    r"(?:pokémon|pokemon)[^.]{0,240}"
    r"all (?:cards )?attached[^.]{0,120}"
    r"into (?:your|their) (hand|deck)",
    re.IGNORECASE,
)

_SPLIT_HAND_DISCARD_RE = re.compile(
    r"put[^.]{0,220}(?:pokémon|pokemon)[^.]{0,120}"
    r"into (?:your|their) hand(?: instead of [^.]+)?"
    r"\.\s*\(discard all (?:cards )?attached[^)]*\)",
    re.IGNORECASE,
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _effect_rows(card: dict[str, Any]) -> tuple[tuple[str, str, str], ...]:
    rows: list[tuple[str, str, str]] = []
    rows.extend(
        ("rule", "", rule)
        for rule in (card.get("rules") or [])
    )
    rows.extend(
        ("attack", attack.get("name") or "", attack.get("text") or "")
        for attack in (card.get("attacks") or [])
    )
    rows.extend(
        ("ability", ability.get("name") or "", ability.get("text") or "")
        for ability in (card.get("abilities") or [])
    )
    return tuple(rows)


def _routing(text: str) -> tuple[str, str, str] | None:
    normalized = " ".join(text.split())

    combined = _COMBINED_ROUTE_RE.search(normalized)
    if combined is not None:
        destination = combined.group(1).lower()
        return destination, destination, combined.group(0)

    split = _SPLIT_HAND_DISCARD_RE.search(normalized)
    if split is not None:
        return "hand", "discard", split.group(0)

    return None


def catalog_pokemon_zone_exits(
    resources_root: Path = Path("resources"),
) -> dict[str, Any]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[dict[str, Any]] = []

    for path in sorted(
        (resources_root / "cards" / "en").glob("*.json")
    ):
        if path.stem not in expanded_sets:
            continue

        for card in _load_json(path):
            effective_status, legality_source = classify_effective_legality(card)
            if effective_status != "Legal":
                continue

            for source_kind, effect_name, text in _effect_rows(card):
                routing = _routing(text)
                if routing is None:
                    continue

                (
                    pokemon_destination,
                    attachment_destination,
                    routing_text,
                ) = routing
                timing_class = (
                    "knockout_triggered"
                    if "knocked out" in text.lower()
                    else "direct_effect"
                )
                rows.append(
                    {
                        "id": card["id"],
                        "name": card["name"],
                        "supertype": card.get("supertype"),
                        "subtypes": card.get("subtypes") or [],
                        "source_kind": source_kind,
                        "effect_name": effect_name,
                        "pokemon_destination": pokemon_destination,
                        "attachment_destination": attachment_destination,
                        "timing_class": timing_class,
                        "routing_text": routing_text,
                        "text": " ".join(text.split()),
                        "legality_source": legality_source,
                    }
                )

    route_print_counts = Counter(
        (
            row["pokemon_destination"],
            row["attachment_destination"],
        )
        for row in rows
    )
    timing_print_counts = Counter(
        row["timing_class"]
        for row in rows
    )

    route_unique_names: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        key = (
            row["pokemon_destination"],
            row["attachment_destination"],
        )
        route_unique_names.setdefault(key, set()).add(row["name"])

    timing_unique_names: dict[str, set[str]] = {}
    for row in rows:
        timing_unique_names.setdefault(
            row["timing_class"],
            set(),
        ).add(row["name"])

    return {
        "summary": {
            "prints": len(rows),
            "unique_names": len({row["name"] for row in rows}),
            "timing_print_counts": dict(
                sorted(timing_print_counts.items())
            ),
            "timing_unique_name_counts": {
                timing: len(names)
                for timing, names in sorted(
                    timing_unique_names.items()
                )
            },
            "route_print_counts": {
                f"{pokemon}->{attachment}": count
                for (pokemon, attachment), count
                in sorted(route_print_counts.items())
            },
            "route_unique_name_counts": {
                f"{pokemon}->{attachment}": len(names)
                for (pokemon, attachment), names
                in sorted(route_unique_names.items())
            },
        },
        "rows": rows,
    }
