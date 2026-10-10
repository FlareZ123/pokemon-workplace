"""Conservative catalog of multi-output Trainer deck-search effects.

The catalog is intentionally literal. It identifies four useful connector shapes:

- fixed_axes: one search clause explicitly asks for several separately named
  targets joined by commas or "and";
- numeric_multi: the search wording explicitly allows two or more cards;
- unbounded_multi: the search wording says "any number of";
- conditional_additional: later text says the same play may also search for
  additional cards.

The classes can overlap. They are discovery metadata rather than a complete
semantic parser.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _legal_expanded_trainers(
    resources_root: Path,
) -> list[dict[str, Any]]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    trainers: list[dict[str, Any]] = []
    for path in sorted(
        (resources_root / "cards" / "en").glob("*.json")
    ):
        if path.stem not in expanded_sets:
            continue

        for card in _load_json(path):
            if card.get("supertype") != "Trainer":
                continue
            if classify_effective_legality(card)[0] != "Legal":
                continue
            trainers.append(card)

    return trainers


def _rules_text(card: dict[str, Any]) -> str:
    return " ".join(card.get("rules") or [])


def _first_search_target_clause(text: str) -> str | None:
    match = re.search(
        r"search your deck for (.*?)(?:\.| then, shuffle| shuffle)",
        text,
        re.IGNORECASE,
    )
    if match is None:
        return None

    clause = match.group(1)
    return clause.split(", reveal", 1)[0].strip()


def _fixed_axes_clause(text: str) -> str | None:
    target = _first_search_target_clause(text)
    if target is None:
        return None
    if " or " in target.lower():
        return None

    coordinated_article = re.search(
        r"(?:,\s*|\s+and\s+)(?:a|an)\s+",
        target,
        re.IGNORECASE,
    )
    if coordinated_article is None:
        return None
    return target


def _numeric_capacity(text: str) -> int | None:
    capacities: list[int] = []
    for pattern in (
        r"search your deck for up to (\d+)",
        r"search your deck for (\d+)\s",
    ):
        capacities.extend(
            int(value)
            for value in re.findall(
                pattern,
                text,
                re.IGNORECASE,
            )
            if int(value) >= 2
        )
    return max(capacities, default=None)


def catalog_multi_output_trainers(
    resources_root: Path = Path("resources"),
) -> dict[str, Any]:
    """Return conservative multi-output search metadata for legal Trainers."""

    rows: list[dict[str, Any]] = []
    for card in _legal_expanded_trainers(resources_root):
        text = _rules_text(card)
        lower = text.lower()
        if "search your deck for" not in lower:
            continue

        classifications: list[str] = []
        fixed_clause = _fixed_axes_clause(text)
        numeric_capacity = _numeric_capacity(text)

        if fixed_clause is not None:
            classifications.append("fixed_axes")
        if numeric_capacity is not None:
            classifications.append("numeric_multi")
        if "search your deck for any number of" in lower:
            classifications.append("unbounded_multi")
        if "may also search for" in lower:
            classifications.append("conditional_additional")

        if not classifications:
            continue

        rows.append(
            {
                "id": card["id"],
                "name": card["name"],
                "subtypes": card.get("subtypes") or [],
                "classifications": classifications,
                "fixed_axes_clause": fixed_clause,
                "numeric_capacity": numeric_capacity,
                "rules": card.get("rules") or [],
            }
        )

    class_print_counts = Counter(
        classification
        for row in rows
        for classification in row["classifications"]
    )
    class_names: dict[str, set[str]] = {
        classification: set()
        for classification in class_print_counts
    }
    for row in rows:
        for classification in row["classifications"]:
            class_names[classification].add(row["name"])

    return {
        "summary": {
            "union_unique_names": len(
                {row["name"] for row in rows}
            ),
            "union_prints": len(rows),
            "class_print_counts": dict(
                sorted(class_print_counts.items())
            ),
            "class_unique_name_counts": {
                classification: len(names)
                for classification, names in sorted(
                    class_names.items()
                )
            },
        },
        "rows": rows,
    }
