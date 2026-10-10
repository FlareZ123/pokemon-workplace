"""Audit how Special Energy print text changes across English BW-onward reprints."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
import json
from pathlib import Path
import re


BW_START = date(2011, 4, 25)


@dataclass(frozen=True)
class SpecialEnergyPrint:
    name: str
    print_id: str
    release_date: date
    raw_text: str
    normalized_text: str


def _records(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    return value.get("data", value) if isinstance(value, dict) else value


def _normalize(text: str) -> str:
    # Whitespace is not rules semantics. Preserve all punctuation and words.
    # A missing space after a full stop in the source is normalized as well.
    return re.sub(r"\s+", " ", re.sub(r"(?<=\.)\s*", " ", text)).strip()


def scan_special_energy_prints(root: Path) -> tuple[SpecialEnergyPrint, ...]:
    released = {
        row["id"]: datetime.strptime(row["releaseDate"], "%Y/%m/%d").date()
        for row in _records(root / "sets" / "en.json")
    }
    out = []
    for path in sorted((root / "cards" / "en").glob("*.json")):
        date_value = released.get(path.stem)
        if date_value is None or date_value < BW_START:
            continue
        for card in _records(path):
            if card.get("supertype") != "Energy" or "Special" not in (card.get("subtypes") or []):
                continue
            raw = " ".join(card.get("rules") or ())
            out.append(SpecialEnergyPrint(
                name=card["name"],
                print_id=card["id"],
                release_date=date_value,
                raw_text=raw,
                normalized_text=_normalize(raw),
            ))
    return tuple(out)


def text_variant_groups(
    rows: tuple[SpecialEnergyPrint, ...], *, normalized: bool,
) -> dict[str, dict[str, tuple[str, ...]]]:
    grouped: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        key = row.normalized_text if normalized else row.raw_text
        grouped[row.name][key].append(row.print_id)
    return {
        name: {text: tuple(sorted(ids)) for text, ids in variants.items()}
        for name, variants in grouped.items()
    }
