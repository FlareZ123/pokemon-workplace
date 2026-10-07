"""Catalog effectively legal Special Energy with state-dependent unit counts."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
from typing import Any

from build_expanded_legality_baseline import classify_effective_legality


_ENERGY_WORDS = (
    "Colorless",
    "Lightning",
    "Psychic",
    "Fighting",
    "Darkness",
    "Grass",
    "Fire",
    "Water",
    "Metal",
    "Fairy",
)
_WORD_ALT = "|".join(_ENERGY_WORDS)
_SYMBOL_RUN = re.compile(
    rf"provides ((?:(?:{_WORD_ALT}))+?) Energy",
    re.IGNORECASE,
)
_ONE_WORD = re.compile(_WORD_ALT, re.IGNORECASE)
_NUMERIC_AT_A_TIME = re.compile(
    r"provides (?:only )?(\d+) Energy at a time",
    re.IGNORECASE,
)
_NUMERIC_COMBINATION = re.compile(
    r"provides (\d+) in any combination",
    re.IGNORECASE,
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def provider_unit_counts(text: str) -> tuple[int, ...]:
    """Return explicit Energy-unit counts stated in one Special Energy text."""

    normalized = " ".join(text.split())
    counts: list[int] = []

    for match in _SYMBOL_RUN.finditer(normalized):
        counts.append(len(_ONE_WORD.findall(match.group(1))))
    counts.extend(
        int(match.group(1))
        for match in _NUMERIC_AT_A_TIME.finditer(normalized)
    )
    counts.extend(
        int(match.group(1))
        for match in _NUMERIC_COMBINATION.finditer(normalized)
    )
    return tuple(sorted(set(counts)))


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
            counts = provider_unit_counts(text)
            if len(counts) <= 1:
                continue

            rows.append({
                "card_id": card["id"],
                "card_name": card["name"],
                "unit_counts": counts,
                "text": " ".join(text.split()),
            })

    profiles = Counter(
        ",".join(str(value) for value in row["unit_counts"])
        for row in rows
    )
    names = sorted({row["card_name"] for row in rows})
    return {
        "print_rows": len(rows),
        "distinct_names": len(names),
        "names": names,
        "profiles": dict(sorted(profiles.items())),
        "rows": rows,
    }


def main() -> None:
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("resources")
    print(json.dumps(build(root), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
