"""Catalog high-confidence card-text families that alter physical card topology."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


WHEN_IF_KO = re.compile(r"\b(?:when|if)\b.*\bKnocked Out\b", re.IGNORECASE)


def normalize(text: str) -> str:
    return " ".join(text.split())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_text_units(card: dict[str, Any]):
    for index, rule in enumerate(card.get("rules") or []):
        yield "rule", str(index), normalize(rule)
    for ability in card.get("abilities") or []:
        yield "ability", ability["name"], normalize(ability.get("text") or "")
    for attack in card.get("attacks") or []:
        yield "attack", attack["name"], normalize(attack.get("text") or "")


def classify_text(card: dict[str, Any], text: str) -> tuple[str, ...]:
    lower = text.lower()
    categories: list[str] = []

    if WHEN_IF_KO.search(text):
        categories.append("knock_out_trigger")

    if "knocked out" in lower and "instead of the discard pile" in lower:
        categories.append("knock_out_zone_redirection")

    if (
        "knocked out" in lower
        and "attached" in lower
        and ("into your hand" in lower or "to your hand" in lower)
    ):
        categories.append("knock_out_attached_recovery")

    if (
        re.search(r"\bmove\b", text, re.IGNORECASE)
        and "energy" in lower
        and " from " in lower
        and " to " in lower
    ):
        categories.append("energy_move")

    if (
        card.get("supertype") == "Energy"
        and "Special" in (card.get("subtypes") or [])
        and (
            "can only be attached to" in lower
            or "attached to anything other than" in lower
        )
    ):
        categories.append("restricted_special_energy_attachment")

    if (
        "attached" in lower
        and ("into your hand" in lower or "to your hand" in lower)
    ):
        categories.append("attached_card_to_hand")

    if (
        "instead of the discard pile" in lower
        or "instead of discarding" in lower
    ):
        categories.append("discard_redirection")

    return tuple(categories)


def build(resources_root: Path) -> dict[str, Any]:
    sets = load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        row["id"]
        for row in sets
        if (row.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue

        for card in load_json(path):
            if classify_effective_legality(card)[0] == "Banned":
                continue

            for source_kind, source_name, text in iter_text_units(card):
                categories = classify_text(card, text)
                if not categories:
                    continue
                rows.append(
                    {
                        "card_id": card["id"],
                        "card_name": card["name"],
                        "source_kind": source_kind,
                        "source_name": source_name,
                        "categories": categories,
                        "text": text,
                    }
                )

    category_print_text_counts = Counter(
        category
        for row in rows
        for category in row["categories"]
    )
    category_distinct_text_counts = {
        category: len(
            {
                row["text"]
                for row in rows
                if category in row["categories"]
            }
        )
        for category in sorted(category_print_text_counts)
    }
    category_card_counts = {
        category: len(
            {
                row["card_id"]
                for row in rows
                if category in row["categories"]
            }
        )
        for category in sorted(category_print_text_counts)
    }

    return {
        "summary": {
            "matched_text_units": len(rows),
            "matched_cards": len({row["card_id"] for row in rows}),
            "print_text_instances_by_category": dict(
                sorted(category_print_text_counts.items())
            ),
            "distinct_texts_by_category": category_distinct_text_counts,
            "cards_by_category": category_card_counts,
        },
        "rows": rows,
    }


def rows_for_card(catalog: dict[str, Any], card_id: str) -> list[dict[str, Any]]:
    return [
        row
        for row in catalog["rows"]
        if row["card_id"] == card_id
    ]


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    print(json.dumps(build(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
