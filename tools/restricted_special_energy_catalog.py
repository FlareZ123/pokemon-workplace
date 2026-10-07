"""Catalog effectively legal holder-restricted Special Energy prints."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


_REQUIREMENT = re.compile(
    r"can only be attached to (?:a )?(.+?) Pok(?:é|e)mon",
    re.IGNORECASE,
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_requirement(raw: str) -> str:
    value = " ".join(raw.split()).strip()
    aliases = {
        "evolution": "Evolution",
        "grass": "Grass",
        "fire": "Fire",
        "water": "Water",
        "lightning": "Lightning",
        "psychic": "Psychic",
        "fighting": "Fighting",
        "darkness": "Darkness",
        "metal": "Metal",
        "fairy": "Fairy",
        "dragon": "Dragon",
        "rapid strike": "Rapid Strike",
        "single strike": "Single Strike",
        "fusion strike": "Fusion Strike",
        "team aqua": "Team Aqua",
        "team magma": "Team Magma",
        "team rocket's": "Team Rocket's",
    }
    key = value.lower()
    if key not in aliases:
        raise ValueError(f"unrecognized attachment requirement: {value!r}")
    return aliases[key]


def build(resources_root: Path) -> dict[str, Any]:
    sets = _load_json(resources_root / "sets" / "en.json")
    expanded_sets = {
        entry["id"]
        for entry in sets
        if (entry.get("legalities") or {}).get("expanded") == "Legal"
    }

    rows: list[dict[str, Any]] = []
    for path in sorted((resources_root / "cards" / "en").glob("*.json")):
        if path.stem not in expanded_sets:
            continue

        for card in _load_json(path):
            if card.get("supertype") != "Energy":
                continue
            if "Special" not in (card.get("subtypes") or []):
                continue
            status, _reason = classify_effective_legality(card)
            if status == "Banned":
                continue

            text = " ".join(card.get("rules") or [])
            normalized = " ".join(text.split())
            if (
                "can only be attached to" not in normalized.lower()
                or "discard this card" not in normalized.lower()
            ):
                continue

            match = _REQUIREMENT.search(normalized)
            if match is None:
                raise ValueError(
                    f"could not parse holder restriction for {card['id']}"
                )

            rows.append({
                "card_id": card["id"],
                "card_name": card["name"],
                "required_tag": _normalize_requirement(match.group(1)),
                "text": normalized,
            })

    by_requirement = Counter(row["required_tag"] for row in rows)
    return {
        "print_rows": len(rows),
        "distinct_names": len({row["card_name"] for row in rows}),
        "by_requirement": dict(sorted(by_requirement.items())),
        "rows": rows,
    }


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    print(json.dumps(build(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
